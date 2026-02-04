from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from .models import UserProfile, ShopPhoto, CustomUser, Offer
from PIL import Image
import os


class UserProfileForm(forms.ModelForm):
    """Form for updating user profile including profile picture and shop logo"""
    
    class Meta:
        model = UserProfile
        fields = ['shop_name', 'shop_category', 'profile_picture', 'shop_logo', 'phone', 'address', 'city', 'state', 'pincode']
        widgets = {
            'shop_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your shop name'
            }),
            'shop_category': forms.Select(attrs={
                'class': 'form-control'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter phone number'
            }),
            'address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Enter shop address'
            }),
            'city': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'City'
            }),
            'state': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'State'
            }),
            'pincode': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Pincode'
            }),
        }

    def clean_profile_picture(self):
        profile_picture = self.cleaned_data.get('profile_picture')
        
        if profile_picture:
            # Validate file size (max 2MB)
            if profile_picture.size > 2 * 1024 * 1024:  # 2MB
                raise ValidationError('Profile picture size should be less than 2MB.')
            
            # Validate file type
            valid_extensions = ['.jpg', '.jpeg', '.png', '.webp']
            ext = os.path.splitext(profile_picture.name)[1].lower()
            if ext not in valid_extensions:
                raise ValidationError(f'Unsupported file extension. Supported formats: {", ".join(valid_extensions)}')
            
            # Validate image dimensions
            try:
                img = Image.open(profile_picture)
                if img.width < 100 or img.height < 100:
                    raise ValidationError('Profile picture should be at least 100x100 pixels.')
            except Exception:
                raise ValidationError('Invalid image file.')
        
        return profile_picture

    def clean_shop_logo(self):
        shop_logo = self.cleaned_data.get('shop_logo')
        
        if shop_logo:
            # Validate file size (max 3MB)
            if shop_logo.size > 3 * 1024 * 1024:  # 3MB
                raise ValidationError('Shop logo size should be less than 3MB.')
            
            # Validate file type
            valid_extensions = ['.jpg', '.jpeg', '.png', '.svg', '.webp']
            ext = os.path.splitext(shop_logo.name)[1].lower()
            if ext not in valid_extensions:
                raise ValidationError(f'Unsupported file extension. Supported formats: {", ".join(valid_extensions)}')
            
            # Validate image dimensions
            try:
                img = Image.open(shop_logo)
                if img.width < 100 or img.height < 100:
                    raise ValidationError('Shop logo should be at least 100x100 pixels.')
            except Exception:
                raise ValidationError('Invalid image file.')
        
        return shop_logo


class ShopPhotoForm(forms.ModelForm):
    """Form for uploading shop photos"""
    
    class Meta:
        model = ShopPhoto
        fields = ['image', 'caption']
        widgets = {
            'caption': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Add a caption for this photo (optional)'
            }),
        }

    def clean_image(self):
        image = self.cleaned_data.get('image')
        
        if image:
            # Validate file size (max 2MB)
            if image.size > 2 * 1024 * 1024:  # 2MB
                raise ValidationError('Shop photo size should be less than 2MB.')
            
            # Validate file type
            valid_extensions = ['.jpg', '.jpeg', '.png', '.webp']
            ext = os.path.splitext(image.name)[1].lower()
            if ext not in valid_extensions:
                raise ValidationError(f'Unsupported file extension. Supported formats: {", ".join(valid_extensions)}')
            
            # Validate image dimensions
            try:
                img = Image.open(image)
                if img.width < 100 or img.height < 100:
                    raise ValidationError('Shop photo should be at least 100x100 pixels.')
            except Exception:
                raise ValidationError('Invalid image file.')
        
        return image


class MultipleShopPhotoForm(forms.Form):
    """Form for uploading multiple shop photos at once"""
    images = forms.FileField(
        widget=forms.FileInput(),
        help_text='Select up to 5 images (JPG, PNG, WEBP). Maximum 2MB each.',
        label='Shop Photos'
    )

    def clean_images(self):
        images = self.cleaned_data.get('images')
        cleaned_images = []
        
        if images:
            # Handle multiple file uploads
            if isinstance(images, list):
                files = images
            else:
                files = [images]
            
            if len(files) > 5:
                raise ValidationError('You can upload up to 5 photos at once.')
            
            for image in files:
                # Validate file size (max 2MB)
                if image.size > 2 * 1024 * 1024:  # 2MB
                    raise ValidationError(f'Image {image.name} size should be less than 2MB.')
                
                # Validate file type
                valid_extensions = ['.jpg', '.jpeg', '.png', '.webp']
                ext = os.path.splitext(image.name)[1].lower()
                if ext not in valid_extensions:
                    raise ValidationError(f'Unsupported file extension for {image.name}. Supported formats: {", ".join(valid_extensions)}')
                
                # Validate image dimensions
                try:
                    img = Image.open(image)
                    if img.width < 100 or img.height < 100:
                        raise ValidationError(f'Image {image.name} should be at least 100x100 pixels.')
                except Exception:
                    raise ValidationError(f'Invalid image file: {image.name}')
                
                cleaned_images.append(image)
        
        return cleaned_images


# Forms required by views.py

class SignupForm(UserCreationForm):
    email = forms.EmailField(required=True)
    phone_number = forms.CharField(max_length=20, required=False)
    
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'phone_number', 'password1', 'password2')
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.phone_number = self.cleaned_data.get('phone_number', '')
        if commit:
            user.save()
        return user


class LoginForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput())
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Enter your email'})
        self.fields['password'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Enter your password'})


class OTPVerificationForm(forms.Form):
    otp = forms.CharField(max_length=10, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter OTP'}))


class PasswordResetForm(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter your email'}))


class SetNewPasswordForm(forms.Form):
    new_password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Enter new password'}),
        label='New Password'
    )
    new_password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm new password'}),
        label='Confirm New Password'
    )
    
    def clean(self):
        cleaned_data = super().clean()
        new_password1 = cleaned_data.get('new_password1')
        new_password2 = cleaned_data.get('new_password2')
        
        if new_password1 and new_password2 and new_password1 != new_password2:
            raise ValidationError('Passwords do not match')
        
        return cleaned_data


class CreatePasswordForm(forms.Form):
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Enter password'}),
        label='Password'
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm password'}),
        label='Confirm Password'
    )
    
    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')
        
        if password1 and password2 and password1 != password2:
            raise ValidationError('Passwords do not match')
        
        return cleaned_data


class OfferForm(forms.ModelForm):
    """Form for creating and editing offers"""
    
    class Meta:
        model = Offer
        fields = ['name', 'description', 'offer_type', 'discount_value', 'min_purchase_amount', 'buy_quantity', 'get_quantity', 'start_date', 'end_date', 'applicable_products', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Offer name'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Description', 'rows': 3}),
            'offer_type': forms.Select(attrs={'class': 'form-control'}),
            'discount_value': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Discount value'}),
            'min_purchase_amount': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Minimum purchase amount'}),
            'buy_quantity': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Buy quantity (for BOGO)'}),
            'get_quantity': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Get quantity (for BOGO)'}),
            'start_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'end_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        offer_type = cleaned_data.get('offer_type')
        discount_value = cleaned_data.get('discount_value')
        buy_quantity = cleaned_data.get('buy_quantity')
        get_quantity = cleaned_data.get('get_quantity')
        
        # Date validation
        if start_date and end_date:
            if start_date >= end_date:
                raise ValidationError("End date must be after start date.")
        
        # Percentage validation
        if offer_type == 'percentage' and discount_value:
            if discount_value <= 0 or discount_value > 100:
                self.add_error('discount_value', "Percentage discount must be between 0 and 100.")
        
        # Flat discount validation
        if offer_type == 'flat' and discount_value:
            if discount_value <= 0:
                self.add_error('discount_value', "Flat discount must be greater than 0.")
        
        # BOGO validation
        if offer_type == 'bogo':
            if not buy_quantity or buy_quantity <= 0:
                self.add_error('buy_quantity', "Buy quantity is required and must be greater than 0 for BOGO offers.")
            if not get_quantity or get_quantity <= 0:
                self.add_error('get_quantity', "Get quantity is required and must be greater than 0 for BOGO offers.")
        
        return cleaned_data