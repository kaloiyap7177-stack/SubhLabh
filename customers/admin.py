from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group
from .models import (
    CustomUser, OTPVerification, EmailLog,
    UserProfile, Customer, Product, Sale, SaleItem,
    ShopPhoto, SaleOffer, UserActivity
)

# Unregister Group (from Authentication and Authorization)
try:
    admin.site.unregister(Group)
except admin.sites.NotRegistered:
    pass


# @admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email', 'phone_number')}),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        ('Important dates', {'fields': ('last_login', 'last_login_at', 'date_joined', 'created_at', 'updated_at')}),
        ('Verification', {'fields': ('is_verified',)}),
    )
    list_display = ('email', 'first_name', 'last_name', 'is_verified', 'is_active', 'created_at')
    list_filter = ('is_verified', 'is_active', 'created_at')
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at', 'last_login_at')


# @admin.register(OTPVerification)
class OTPVerificationAdmin(admin.ModelAdmin):
    list_display = ('email', 'purpose', 'is_verified', 'created_at', 'expires_at')
    list_filter = ('purpose', 'is_verified', 'created_at')
    search_fields = ('email',)
    readonly_fields = ('otp_code', 'created_at', 'expires_at')
    ordering = ('-created_at',)


# @admin.register(EmailLog)
class EmailLogAdmin(admin.ModelAdmin):
    list_display = ('email', 'subject', 'purpose', 'is_sent', 'created_at')
    list_filter = ('purpose', 'is_sent', 'created_at')
    search_fields = ('email', 'subject')
    readonly_fields = ('created_at', 'error_message')
    ordering = ('-created_at',)


# @admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'shop_name', 'shop_category', 'city', 'created_at')
    list_filter = ('shop_category', 'created_at')
    search_fields = ('user__email', 'shop_name', 'phone')
    readonly_fields = ('created_at', 'updated_at')


# @admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone', 'credit_amount', 'total_purchased', 'created_at')
    list_filter = ('created_at', 'credit_amount')
    search_fields = ('name', 'phone', 'address')
    readonly_fields = ('created_at', 'updated_at')


# @admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'stock_quantity', 'is_active', 'created_at')
    list_filter = ('category', 'is_active', 'created_at')
    search_fields = ('name', 'description')
    readonly_fields = ('created_at', 'updated_at')


class SaleItemInline(admin.TabularInline):
    model = SaleItem
    extra = 0
    fields = ('product', 'quantity', 'price_at_sale')


# @admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'total_amount', 'payment_method', 'is_paid', 'sale_date')
    list_filter = ('payment_method', 'is_paid', 'sale_date')
    search_fields = ('customer__name', 'notes')
    readonly_fields = ('created_at', 'updated_at', 'sale_date')
    inlines = [SaleItemInline]


# @admin.register(SaleItem)
class SaleItemAdmin(admin.ModelAdmin):
    list_display = ('sale', 'product', 'quantity', 'price_at_sale')
    list_filter = ('sale__sale_date', 'product__category')
    search_fields = ('sale__id', 'product__name')


# @admin.register(ShopPhoto)
class ShopPhotoAdmin(admin.ModelAdmin):
    list_display = ('user', 'caption', 'display_order', 'created_at')
    list_filter = ('user', 'created_at')
    search_fields = ('user__email', 'caption')


# @admin.register(SaleOffer)
class SaleOfferAdmin(admin.ModelAdmin):
    list_display = ('sale', 'offer', 'discount_amount')
    list_filter = ('offer',)


@admin.register(UserActivity)
class UserActivityAdmin(admin.ModelAdmin):
    """Admin interface for User Activity tracking"""
    list_display = ('user_full_name', 'user_email', 'formatted_time', 'date')
    list_filter = ('date', 'user')
    search_fields = ('user__email', 'user__first_name', 'user__last_name')
    readonly_fields = ('user', 'date', 'total_active_seconds', 'formatted_time', 
                      'login_count', 'last_activity', 'created_at', 'updated_at')
    ordering = ('-date', 'user')
    date_hierarchy = 'date'
    
    def user_full_name(self, obj):
        """Display user full name"""
        return f"{obj.user.first_name} {obj.user.last_name}".strip() or obj.user.username
    user_full_name.short_description = 'Name'
    user_full_name.admin_order_field = 'user__first_name'
    
    def user_email(self, obj):
        """Display user email"""
        return obj.user.email
    user_email.short_description = 'Email'
    user_email.admin_order_field = 'user__email'
    
    def formatted_time(self, obj):
        """Display active time in human-readable format"""
        return obj.formatted_active_time
    formatted_time.short_description = 'Active Time'
    formatted_time.admin_order_field = 'total_active_seconds'
    
    def has_add_permission(self, request):
        """Prevent manual creation of activity records"""
        return False
    
    def has_delete_permission(self, request, obj=None):
        """Only superusers can delete activity records"""
        return request.user.is_superuser
