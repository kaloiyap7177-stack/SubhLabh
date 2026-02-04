from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.db.models import Sum, Count, Q, F
from datetime import timedelta
import random
import string
import os
from PIL import Image
from io import BytesIO
from django.core.files.base import ContentFile

class CustomUser(AbstractUser):
    """Custom User model with email-based authentication"""
    email = models.EmailField(unique=True)
    is_verified = models.BooleanField(default=False)
    phone_number = models.CharField(max_length=20, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_login_at = models.DateTimeField(null=True, blank=True)
    
    # Account deletion fields
    deletion_requested_at = models.DateTimeField(null=True, blank=True)
    is_pending_deletion = models.BooleanField(default=False)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.email


class OTPVerification(models.Model):
    """Store OTP and verification details"""
    email = models.EmailField()
    otp_code = models.CharField(max_length=10)
    purpose = models.CharField(
        max_length=20,
        choices=[('signup', 'Signup'), ('login', 'Login'), ('reset', 'Password Reset')],
        default='signup'
    )
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    attempt_count = models.IntegerField(default=0)
    max_attempts = models.IntegerField(default=5)
    
    class Meta:
        verbose_name = 'OTP Verification'
        verbose_name_plural = 'OTP Verifications'
        ordering = ['-created_at']
        indexes = [models.Index(fields=['email', '-created_at'])]
    
    def __str__(self):
        return f"{self.email} - {self.purpose}"
    
    def is_expired(self):
        """Check if OTP has expired"""
        return timezone.now() > self.expires_at
    
    def is_valid(self):
        """Check if OTP is still valid and not expired"""
        return not self.is_expired() and self.attempt_count < self.max_attempts
    
    def increment_attempts(self):
        """Increment failed attempt count"""
        self.attempt_count += 1
        self.save()
    
    @staticmethod
    def generate_otp(length=6):
        """Generate a random OTP"""
        return ''.join(random.choices(string.digits, k=length))
    
    @staticmethod
    def create_otp(email, purpose='signup', otp_expiry_time=300):
        """Create or update OTP for email"""
        otp_code = OTPVerification.generate_otp()
        expires_at = timezone.now() + timedelta(seconds=otp_expiry_time)
        
        otp_obj, created = OTPVerification.objects.update_or_create(
            email=email,
            purpose=purpose,
            defaults={
                'otp_code': otp_code,
                'expires_at': expires_at,
                'is_verified': False,
                'attempt_count': 0
            }
        )
        return otp_obj


class EmailLog(models.Model):
    """Log of all emails sent for audit and debugging"""
    email = models.EmailField()
    subject = models.CharField(max_length=255)
    purpose = models.CharField(
        max_length=20,
        choices=[('signup', 'Signup'), ('login', 'Login'), ('reset', 'Password Reset'), ('resend', 'Resend OTP')]
    )
    is_sent = models.BooleanField(default=False)
    error_message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Email Log'
        verbose_name_plural = 'Email Logs'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.email} - {self.subject}"


class UserProfile(models.Model):
    """Store additional user profile information for shop branding"""
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='profile')
    shop_name = models.CharField(max_length=255, blank=True, default='My Shop')
    shop_category = models.CharField(
        max_length=50,
        choices=[
            ('pizza', 'Pizza/Fast Food'),
            ('clothes', 'Clothes'),
            ('grocery', 'Grocery'),
            ('bartan', 'Bartan/Utensils'),
            ('medical', 'Medical'),
            ('electronics', 'Electronics'),
            ('other', 'Other'),
        ],
        default='other'
    )
    profile_picture = models.ImageField(upload_to='profiles/', null=True, blank=True)
    shop_logo = models.ImageField(upload_to='logos/', blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    pincode = models.CharField(max_length=10, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    email_notifications_enabled = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'
    
    def __str__(self):
        return f"{self.user.email} - {self.shop_name}"

    def save(self, *args, **kwargs):
        # Compress images if they are new or changed
        if self.profile_picture:
            self.profile_picture = self.compress_image(self.profile_picture)
        if self.shop_logo:
            self.shop_logo = self.compress_image(self.shop_logo)
        super().save(*args, **kwargs)

    def compress_image(self, image):
        try:
            img = Image.open(image)
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            output = BytesIO()
            img.save(output, format='JPEG', quality=70)
            output.seek(0)
            return ContentFile(output.read(), name=os.path.basename(image.name))
        except Exception:
            return image


class Customer(models.Model):
    """Customer model for tracking customer information and credit"""
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='customers')
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=20)
    address = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    udhar_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_purchased = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_visits = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Customer'
        verbose_name_plural = 'Customers'
        indexes = [models.Index(fields=['user', '-created_at'])]
    
    def __str__(self):
        return f"{self.name} ({self.phone})"


class Product(models.Model):
    """Product model for inventory management"""
    
    PRODUCT_TYPE_CHOICES = [
        ('product', 'Product'),
        ('service', 'Service'),
    ]
    
    CATEGORY_CHOICES = [
        ('pizza', 'Pizza/Fast Food'),
        ('clothes', 'Clothes'),
        ('grocery', 'Grocery'),
        ('bartan', 'Bartan/Utensils'),
        ('medical', 'Medical'),
        ('electronics', 'Electronics'),
        ('other', 'Other'),
    ]
    
    UNIT_CHOICES = [
        ('kg', 'Kilogram'),
        ('gm', 'Gram'),
        ('lt', 'Liter'),
        ('ml', 'Milliliter'),
        ('piece', 'Piece'),
        ('packet', 'Packet'),
        ('box', 'Box'),
        ('dozen', 'Dozen'),
    ]
    
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='products')
    name = models.CharField(max_length=255)
    product_type = models.CharField(max_length=20, choices=PRODUCT_TYPE_CHOICES, default='product')
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    unit = models.CharField(max_length=20, choices=UNIT_CHOICES, default='piece', blank=True)
    stock_quantity = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    image = models.ImageField(upload_to='products/', null=True, blank=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Product'
        verbose_name_plural = 'Products'
        indexes = [models.Index(fields=['user', 'category'])]
    
    def __str__(self):
        return f"{self.name} (Rs. {self.price})"
    
    @property
    def is_low_stock(self):
        # Services don't have stock
        if self.product_type == 'service':
            return False
        return self.stock_quantity < 10
    
    @property
    def is_service(self):
        return self.product_type == 'service'
    
    @property
    def is_product(self):
        return self.product_type == 'product'


class Sale(models.Model):
    """Sale/Bill model for tracking transactions"""
    PAYMENT_CHOICES = [
        ('cash', 'Cash'),
        ('upi', 'UPI'),
        ('card', 'Card'),
    ]
    
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='sales')
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True, related_name='sales', db_index=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_CHOICES)
    is_paid = models.BooleanField(default=True)
    added_to_udhar = models.BooleanField(default=False)
    sale_date = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    notes = models.TextField(blank=True)
    
    # Offer fields
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    class Meta:
        ordering = ['-sale_date']
        verbose_name = 'Sale'
        verbose_name_plural = 'Sales'
        indexes = [models.Index(fields=['user', '-sale_date'])]
    
    def __str__(self):
        customer_name = self.customer.name if self.customer else 'Walk-in'
        return f"{customer_name} - Rs. {self.total_amount} ({self.sale_date.date()})"


class SaleItem(models.Model):
    """Individual items in a sale/bill"""
    sale = models.ForeignKey(Sale, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name='sale_items')
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    price_at_sale = models.DecimalField(max_digits=10, decimal_places=2)
    
    class Meta:
        verbose_name = 'Sale Item'
        verbose_name_plural = 'Sale Items'
    
    def __str__(self):
        return f"{self.product.name} x{self.quantity}"
    
    @property
    def total_amount(self):
        return self.quantity * self.price_at_sale


class Offer(models.Model):
    """Offer/Promotion model"""
    OFFER_TYPE_CHOICES = [
        ('flat', 'Flat Discount'),
        ('percentage', 'Percentage Discount'),
        ('bogo', 'Buy X Get Y'),
    ]
    
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='offers')
    name = models.CharField(max_length=255, default='New Offer')
    description = models.TextField(blank=True)
    offer_type = models.CharField(max_length=20, choices=OFFER_TYPE_CHOICES, default='flat')
    
    # Discount details
    discount_value = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # Amount or Percentage
    min_purchase_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # BOGO details
    buy_quantity = models.IntegerField(default=0, help_text="Buy X items")
    get_quantity = models.IntegerField(default=0, help_text="Get Y items free")
    
    # Applicability
    applicable_products = models.ManyToManyField(Product, blank=True, related_name='offers')
    start_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [models.Index(fields=['user', 'start_date', 'end_date'])]
    
    def __str__(self):
        return self.name
    
    def clean(self):
        """Validate offer data at model level"""
        from django.core.exceptions import ValidationError
        
        # Date validation
        if self.start_date and self.end_date:
            if self.start_date >= self.end_date:
                raise ValidationError("End date must be after start date.")
        
        # Percentage validation
        if self.offer_type == 'percentage':
            if self.discount_value <= 0 or self.discount_value > 100:
                raise ValidationError("Percentage discount must be between 0 and 100.")
        
        # BOGO validation
        if self.offer_type == 'bogo':
            if self.buy_quantity <= 0:
                raise ValidationError("Buy quantity must be greater than 0 for BOGO offers.")
            if self.get_quantity <= 0:
                raise ValidationError("Get quantity must be greater than 0 for BOGO offers.")
    
    @property
    def is_valid(self):
        """Check if offer is currently valid (active and within date range)"""
        now = timezone.now()
        return self.is_active and self.start_date <= now <= self.end_date


class SaleOffer(models.Model):
    """Track offers applied to a sale"""
    sale = models.ForeignKey(Sale, on_delete=models.CASCADE, related_name='applied_offers')
    offer = models.ForeignKey(Offer, on_delete=models.CASCADE, related_name='sale_offers')
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    class Meta:
        verbose_name_plural = 'Sale Offers'



class ShopPhoto(models.Model):
    """Gallery photos for the shop"""
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='shop_photos')
    image = models.ImageField(upload_to='shop_photos/')
    caption = models.CharField(max_length=200, blank=True)
    display_order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['display_order', '-created_at']

    def __str__(self):
        return f"Photo for {self.user.email} - {self.caption or 'No caption'}"

    def save(self, *args, **kwargs):
        if self.image:
            self.image = self.compress_image(self.image)
        super().save(*args, **kwargs)

    def compress_image(self, image):
        try:
            img = Image.open(image)
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            output = BytesIO()
            img.save(output, format='JPEG', quality=75)
            output.seek(0)
            return ContentFile(output.read(), name=os.path.basename(image.name))
        except Exception:
            return image


class UserActivity(models.Model):
    """Track daily user activity for admin monitoring"""
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='activity_logs')
    date = models.DateField()  # Date of activity
    total_active_seconds = models.IntegerField(default=0)  # Total active time in seconds
    login_count = models.IntegerField(default=0)  # Number of logins on that day
    last_activity = models.DateTimeField(auto_now=True)  # Last activity timestamp
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['user', 'date']
        ordering = ['-date', 'user']
        verbose_name = 'User Activity'
        verbose_name_plural = 'User Activities'
        indexes = [models.Index(fields=['user', '-date'])]
    
    def __str__(self):
        return f"{self.user.email} - {self.date}"
    
    @property
    def formatted_active_time(self):
        """Return active time in human-readable format"""
        hours = self.total_active_seconds // 3600
        minutes = (self.total_active_seconds % 3600) // 60
        seconds = self.total_active_seconds % 60
        
        if hours > 0:
            return f"{hours}h {minutes}m {seconds}s"
        elif minutes > 0:
            return f"{minutes}m {seconds}s"
        else:
            return f"{seconds}s"
