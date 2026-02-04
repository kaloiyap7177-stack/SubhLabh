from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from datetime import timedelta
import random
import string

# Create your models here.

class CustomUser(AbstractUser):
    """Custom User model with email-based authentication"""
    email = models.EmailField(unique=True)
    is_verified = models.BooleanField(default=False)
    phone_number = models.CharField(max_length=20, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_login_at = models.DateTimeField(null=True, blank=True)
    
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
