# Type stubs for Django models
# This file helps type checkers understand Django's dynamic model fields

from typing import Any
from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    id: int
    email: str
    is_verified: bool
    phone_number: str
    created_at: Any
    updated_at: Any
    last_login_at: Any
    first_name: str
    last_name: str

class UserProfile(models.Model):
    id: int
    user: CustomUser
    shop_name: str
    shop_category: str
    profile_picture: Any
    phone: str
    address: str
    city: str
    state: str
    pincode: str
    created_at: Any
    updated_at: Any

class Customer(models.Model):
    id: int
    user: CustomUser
    name: str
    phone: str
    address: str
    notes: str
    udhar_amount: Any
    total_purchased: Any
    total_visits: int
    created_at: Any
    updated_at: Any

class Product(models.Model):
    id: int
    user: CustomUser
    name: str
    category: str
    price: Any
    stock_quantity: int
    description: str
    is_active: bool
    created_at: Any
    updated_at: Any
    is_low_stock: bool

class Sale(models.Model):
    id: int
    user: CustomUser
    customer: Customer | None
    total_amount: Any
    payment_method: str
    is_paid: bool
    added_to_udhar: bool
    sale_date: Any
    created_at: Any
    updated_at: Any
    notes: str

class SaleItem(models.Model):
    id: int
    sale: Sale
    product: Product
    quantity: int
    price_at_sale: Any
    total_amount: Any

class OTPVerification(models.Model):
    id: int
    email: str
    otp_code: str
    purpose: str
    is_verified: bool
    created_at: Any
    expires_at: Any
    attempt_count: int
    max_attempts: int

class EmailLog(models.Model):
    id: int
    email: str
    subject: str
    purpose: str
    is_sent: bool
    error_message: str
    created_at: Any
