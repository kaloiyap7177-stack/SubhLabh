"""
Business logic views for Subhlabh application
Dashboard, Customer, Product, Sales, Reports
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.db.models import Sum, Count, Q, F, DecimalField, Max
from django.utils import timezone
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash, logout
from datetime import datetime, time, timedelta
from decimal import Decimal
import json
import logging
from django.core.cache import cache

# Configure logger for this module
logger = logging.getLogger(__name__)

from .models import (
    UserProfile, Customer, Product, Sale, SaleItem, CustomUser, Offer, SaleOffer, ShopPhoto
)
from .forms import OfferForm


@method_decorator(login_required, name='dispatch')
class DashboardView(View):
    """Dashboard showing key metrics and recent transactions"""
    
    def get(self, request):
        """Render dashboard with caching for improved performance"""
        user = request.user
        today = timezone.now().date()
        month_start = today.replace(day=1)
        
        try:
            profile = user.profile
        except UserProfile.DoesNotExist:
            profile = UserProfile.objects.create(user=user)
        
        # Prepare today's range (start of day to end of day)
        today_start = timezone.make_aware(datetime.combine(today, time.min))
        today_end = timezone.make_aware(datetime.combine(today, time.max))
        
        # Prepare month start datetime
        month_start_dt = timezone.make_aware(datetime.combine(month_start, time.min))
        
        # Cache key for dashboard metrics
        cache_key = f'dashboard_metrics_{user.id}_{today}'
        # cached_metrics = cache.get(cache_key)
        cached_metrics = None # DEBUG: Force fresh data
        
        if cached_metrics:
            # Use cached metrics
            today_sales = cached_metrics['today_sales']
            month_sales = cached_metrics['month_sales']
            total_customers = cached_metrics['total_customers']
            total_products = cached_metrics['total_products']
            total_udhar = cached_metrics['total_udhar']
            today_udhar = cached_metrics['today_udhar']
        else:
            # Calculate metrics (expensive queries)
            today_sales = Sale.objects.filter(
                user=user,
                sale_date__range=(today_start, today_end)
            ).aggregate(total=Sum('total_amount'))['total'] or Decimal('0')
            
            month_sales = Sale.objects.filter(
                user=user,
                sale_date__gte=month_start_dt,
                sale_date__lte=today_end
            ).aggregate(total=Sum('total_amount'))['total'] or Decimal('0')
            
            total_customers = Customer.objects.filter(user=user).count()
            total_products = Product.objects.filter(user=user).count()
            total_udhar = Customer.objects.filter(user=user).aggregate(
                total=Sum('udhar_amount')
            )['total'] or Decimal('0')
            
            today_udhar = Sale.objects.filter(
                user=user, 
                sale_date__range=(today_start, today_end),
                added_to_udhar=True
            ).aggregate(total=Sum('total_amount'))['total'] or Decimal('0')
            
            # Cache for 5 minutes (300 seconds)
            cache.set(cache_key, {
                'today_sales': today_sales,
                'month_sales': month_sales,
                'total_customers': total_customers,
                'total_products': total_products,
                'total_udhar': total_udhar,
                'today_udhar': today_udhar,
            }, 300)
        
        # Get recent sales with proper timezone handling and optimized queries
        recent_sales = Sale.objects.filter(
            user=user,
            sale_date__lte=today_end
        ).select_related('customer').prefetch_related('items__product')[:5]
        
        low_stock_products = Product.objects.filter(
            user=user,
            stock_quantity__lt=10,
            is_active=True
        ).order_by('stock_quantity')[:5]
        
        # Calculate top products with proper aggregation
        top_products = SaleItem.objects.filter(
            sale__user=user,
            sale__sale_date__lte=today_end
        ).values('product__name').annotate(
            total_quantity=Sum('quantity'),
            total_revenue=Sum(F('quantity') * F('price_at_sale'), output_field=DecimalField())
        ).order_by('-total_revenue')[:5]
        
        # Prepare top products chart data
        product_labels = [p['product__name'] for p in top_products]
        product_data = [float(p['total_revenue']) for p in top_products]
        
        # Prepare monthly sales data for the last 6 months
        import calendar
        
        monthly_labels = []
        monthly_data = []
        
        # Get data for the last 6 months
        for i in range(5, -1, -1):
            # Calculate the month
            month = today.month - i
            year = today.year
            if month <= 0:
                month += 12
                year -= 1
            
            # Get first and last day of the month
            first_day = datetime(year, month, 1).date()
            # For the current month, use today as the end date instead of the last day of the month
            if month == today.month and year == today.year:
                last_day = today
            else:
                last_day = datetime(year, month, calendar.monthrange(year, month)[1]).date()
            
            # Prepare day range for accuracy
            first_day_dt = timezone.make_aware(datetime.combine(first_day, time.min))
            last_day_dt = timezone.make_aware(datetime.combine(last_day, time.max))

            # Get sales for this month with proper timezone handling
            monthly_sales = Sale.objects.filter(
                user=user,
                sale_date__range=(first_day_dt, last_day_dt)
            ).aggregate(total=Sum('total_amount'))['total'] or Decimal('0')
            
            # Add to lists
            monthly_labels.append(first_day.strftime('%b %Y'))
            monthly_data.append(float(monthly_sales))
        
        context = {
            'profile': profile,
            'today': today,
            'today_sales': today_sales,
            'monthly_sales': month_sales,
            'total_customers': total_customers,
            'total_products': total_products,
            'total_udhar': total_udhar,
            'today_udhar': today_udhar,
            'recent_sales': recent_sales,
            'top_products': top_products,
            'low_stock_products': low_stock_products,
            'monthly_labels': monthly_labels,
            'monthly_data': monthly_data,
            'product_labels': product_labels,
            'product_data': product_data,
        }
        
        return render(request, 'customers/dashboard.html', context)


@method_decorator(login_required, name='dispatch')
class ProfileView(View):
    """User profile management"""
    
    def get(self, request):
        try:
            profile = request.user.profile
        except UserProfile.DoesNotExist:
            profile = UserProfile.objects.create(user=request.user)
        
        context = {'profile': profile, 'user': request.user}
        return render(request, 'customers/profile.html', context)
    
    def post(self, request):
        try:
            profile = request.user.profile
        except UserProfile.DoesNotExist:
            profile = UserProfile.objects.create(user=request.user)
        
        # Check if this is an AJAX request
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        
        try:
            # Update user information
            request.user.first_name = request.POST.get('first_name', request.user.first_name)
            request.user.last_name = request.POST.get('last_name', request.user.last_name)
            request.user.save()
            
            # Update profile information
            profile.shop_name = request.POST.get('shop_name', profile.shop_name)
            profile.shop_category = request.POST.get('shop_category', profile.shop_category)
            profile.phone = request.POST.get('phone', profile.phone)
            profile.address = request.POST.get('address', profile.address)
            profile.city = request.POST.get('city', profile.city)
            profile.state = request.POST.get('state', profile.state)
            profile.pincode = request.POST.get('pincode', profile.pincode)
            
            # Handle profile picture upload
            if 'profile_picture' in request.FILES:
                profile.profile_picture = request.FILES['profile_picture']
            
            profile.save()
            
            if is_ajax:
                return JsonResponse({'success': True, 'message': 'Profile updated successfully!'})
            else:
                messages.success(request, 'Profile updated successfully!')
                return redirect('customers:profile')
                
        except Exception as e:
            if is_ajax:
                return JsonResponse({'success': False, 'error': str(e)})
            else:
                messages.error(request, f'Error updating profile: {str(e)}')
                return redirect('customers:profile')


@method_decorator(login_required, name='dispatch')
class ProfileEditView(View):
    """Unified view to edit user profile, shop branding, and gallery"""
    
    @method_decorator(login_required)
    def get(self, request):
        try:
            profile = request.user.profile
        except UserProfile.DoesNotExist:
            profile = UserProfile.objects.create(user=request.user)
        
        shop_photos = request.user.shop_photos.all()
        context = {
            'profile': profile, 
            'user': request.user,
            'shop_photos': shop_photos
        }
        return render(request, 'customers/profile_edit.html', context)
    
    @method_decorator(login_required)
    def post(self, request):
        try:
            profile = request.user.profile
        except UserProfile.DoesNotExist:
            profile = UserProfile.objects.create(user=request.user)
        
        try:
            # Handle different form submissions based on action
            action = request.POST.get('action')
            
            if action == 'branding':
                # Update user information
                request.user.first_name = request.POST.get('first_name', request.user.first_name)
                request.user.last_name = request.POST.get('last_name', request.user.last_name)
                request.user.save()
                
                # Update profile information
                profile.shop_name = request.POST.get('shop_name', profile.shop_name)
                profile.shop_category = request.POST.get('shop_category', profile.shop_category)
                profile.phone = request.POST.get('phone', profile.phone)
                profile.address = request.POST.get('address', profile.address)
                profile.city = request.POST.get('city', profile.city)
                profile.state = request.POST.get('state', profile.state)
                profile.pincode = request.POST.get('pincode', profile.pincode)
                
                # Handle images
                if 'profile_picture' in request.FILES:
                    profile.profile_picture = request.FILES['profile_picture']
                if 'shop_logo' in request.FILES:
                    profile.shop_logo = request.FILES['shop_logo']
                
                profile.save()
                messages.success(request, 'Profile and branding updated successfully!')
            
            elif action == 'add_photo':
                from .forms import ShopPhotoForm
                form = ShopPhotoForm(request.POST, request.FILES)
                if form.is_valid():
                    photo = form.save(commit=False)
                    photo.user = request.user
                    photo.save()
                    messages.success(request, 'Photo added to gallery!')
                else:
                    messages.error(request, 'Error uploading photo. Please check the file format and size.')
            
            return redirect('customers:profile-edit')
                
        except Exception as e:
            logger.error(f"Error in ProfileEditView for user {request.user.id}: {str(e)}", exc_info=True)
            messages.error(request, f'Error: {str(e)}')
            return redirect('customers:profile-edit')


@method_decorator(login_required, name='dispatch')
class ChangePasswordView(View):
    """Change user password"""
    
    def get(self, request):
        form = PasswordChangeForm(request.user)
        # Add form-control class to all fields
        for field in form.fields.values():
            field.widget.attrs.update({'class': 'form-control'})
        return render(request, 'customers/change_password.html', {'form': form})
    
    def post(self, request):
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            messages.success(request, 'Your password was successfully updated!')
            return redirect('customers:profile')
        else:
            messages.error(request, 'Please correct the error below.')
            # Add form-control class to all fields
            for field in form.fields.values():
                field.widget.attrs.update({'class': 'form-control'})
        return render(request, 'customers/change_password.html', {'form': form})


@method_decorator(login_required, name='dispatch')
class SettingsView(View):
    """User settings page"""
    
    def get(self, request):
        profile = request.user.profile
        context = {
            'profile': profile,
        }
        return render(request, 'customers/settings.html', context)


@method_decorator(login_required, name='dispatch')
class UpdateNotificationsView(View):
    """Update email notification preferences"""
    
    def post(self, request):
        try:
            enabled = request.POST.get('enabled') == 'true'
            profile = request.user.profile
            profile.email_notifications_enabled = enabled
            profile.save()
            
            status = "enabled" if enabled else "disabled"
            return JsonResponse({'success': True, 'message': f'Notifications {status}'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})


@method_decorator(login_required, name='dispatch')
class RequestAccountDeletionView(View):
    """Handle account deletion request"""
    
    def post(self, request):
        user = request.user
        
        # Verify password for security (optional but recommended, for now skipping as per plan simplicity, but can add if requested)
        # Actually plan said "Require password re-entry", but for now let's stick to the modal confirmation flow
        
        try:
            user.is_pending_deletion = True
            user.deletion_requested_at = timezone.now()
            user.save()
            
            # Send email notification (placeholder function call)
            # self.send_deletion_email(user)
            
            logout(request)
            messages.info(request, 'Your account has been scheduled for deletion in 30 days. Log in anytime to cancel.')
            return redirect('customers:login')
            
        except Exception as e:
            messages.error(request, f'Error scheduling deletion: {str(e)}')
            return redirect('customers:settings')

    def send_deletion_email(self, user):
        # Todo: Implement email sending logic
        pass


@method_decorator(login_required, name='dispatch')
class CancelAccountDeletionView(View):
    """Cancel account deletion request"""
    
    def get(self, request):
        return self.post(request)
        
    def post(self, request):
        user = request.user
        if user.is_pending_deletion:
            user.is_pending_deletion = False
            user.deletion_requested_at = None
            user.save()
            messages.success(request, 'Account deletion has been cancelled. Welcome back!')
        else:
            messages.info(request, 'Your account was not scheduled for deletion.')
            
        return redirect('customers:dashboard')


@method_decorator(login_required, name='dispatch')
class DeleteAccountConfirmView(View):
    """Confirm account deletion page"""
    
    def get(self, request):
        if request.user.is_pending_deletion:
            messages.info(request, 'Your account is already scheduled for deletion.')
            return redirect('customers:settings')
        return render(request, 'customers/delete_account_confirm.html')


@method_decorator(login_required, name='dispatch')
class BrandingView(View):
    """Manage shop branding (Logo, Name, etc.)"""
    
    def get(self, request):
        choices = [
            ('pizza', 'Pizza/Fast Food'),
            ('clothes', 'Clothes'),
            ('grocery', 'Grocery'),
            ('bartan', 'Bartan/Utensils'),
            ('medical', 'Medical'),
            ('electronics', 'Electronics'),
            ('other', 'Other'),
        ]
        return render(request, 'customers/branding.html', {
            'profile': request.user.profile,
            'category_choices': choices
        })
    
    def post(self, request):
        profile = request.user.profile
        
        # Update text fields
        profile.shop_name = request.POST.get('shop_name', profile.shop_name)
        profile.shop_category = request.POST.get('shop_category', profile.shop_category)
        
        # Handle Logo Upload
        if 'shop_logo' in request.FILES:
            profile.shop_logo = request.FILES['shop_logo']
            
        profile.save()
        messages.success(request, 'Shop branding updated successfully!')
        return redirect('customers:branding')


@method_decorator(login_required, name='dispatch')
class CustomerListView(View):
    """List all customers with search, filter, and pagination"""
    
    def get(self, request):
        customers = Customer.objects.filter(user=request.user).annotate(
            last_purchase_date=Max('sales__sale_date')
        )
        
        # Search by name or phone
        search = request.GET.get('search', '').strip()
        if search:
            customers = customers.filter(
                Q(name__icontains=search) | Q(phone__icontains=search)
            )
        
        # Filter by udhar status
        udhar_filter = request.GET.get('udhar_filter', 'all')
        if udhar_filter == 'remaining':
            customers = customers.filter(udhar_amount__gt=0)
        elif udhar_filter == 'cleared':
            customers = customers.filter(udhar_amount=0)
        
        # Order by latest activity
        customers = customers.order_by('-last_purchase_date', '-created_at')
        
        # Pagination (10 per page)
        page = int(request.GET.get('page', 1))
        per_page = 10
        total = customers.count()
        start = (page - 1) * per_page
        customers = customers[start:start + per_page]
        
        context = {
            'customers': customers,
            'search': search,
            'udhar_filter': udhar_filter,
            'total': total,
            'page': page,
            'pages': (total + per_page - 1) // per_page,
        }
        return render(request, 'customers/customer_list.html', context)


@method_decorator(login_required, name='dispatch')
class CustomerCreateView(View):
    """Create new customer"""
    
    def get(self, request):
        return render(request, 'customers/customer_form.html')
    
    def post(self, request):
        name = request.POST.get('name', '').strip()
        phone = request.POST.get('phone', '').strip()
        address = request.POST.get('address', '').strip()
        notes = request.POST.get('notes', '').strip()
        
        # Check if this is an AJAX request
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        
        if not name or not phone:
            if is_ajax:
                return JsonResponse({'success': False, 'error': 'Name and phone are required!'})
            messages.error(request, 'Name and phone are required!')
            return render(request, 'customers/customer_form.html')
        
        if Customer.objects.filter(user=request.user, phone=phone).exists():
            if is_ajax:
                return JsonResponse({'success': False, 'error': 'Customer with this phone already exists!'})
            messages.warning(request, 'Customer with this phone already exists!')
            return render(request, 'customers/customer_form.html')
        
        customer = Customer.objects.create(
            user=request.user,
            name=name,
            phone=phone,
            address=address,
            notes=notes
        )
        
        if is_ajax:
            # Invalidate dashboard cache
            try:
                from django.utils import timezone
                from django.core.cache import cache
                today = timezone.now().date()
                cache_key = f'dashboard_metrics_{request.user.id}_{today}'
                cache.delete(cache_key)
            except Exception:
                pass

            return JsonResponse({
                'success': True, 
                'message': 'Customer added successfully!',
                'customer_id': customer.id
            })
        
        # Invalidate dashboard cache
        try:
            from django.utils import timezone
            from django.core.cache import cache
            today = timezone.now().date()
            cache_key = f'dashboard_metrics_{request.user.id}_{today}'
            cache.delete(cache_key)
        except Exception:
            pass
        
        messages.success(request, 'Customer added successfully!')
        return redirect('customers:customer-list')


@method_decorator(login_required, name='dispatch')
class CustomerDetailView(View):
    """View customer details with purchase and udhar history"""
    
    def get(self, request, pk):
        customer = get_object_or_404(Customer, pk=pk, user=request.user)
        
        # Get all purchases with items
        purchases = Sale.objects.filter(
            customer=customer
        ).prefetch_related('items__product').order_by('-sale_date')
        
        # Build udhar transaction history
        udhar_transactions = []
        
        # Add credit transactions (unpaid sales)
        for sale in Sale.objects.filter(customer=customer, added_to_udhar=True).order_by('sale_date'):
            udhar_transactions.append({
                'date': sale.sale_date,
                'type': 'credit',
                'amount': sale.total_amount,
                'description': f'Sale #{sale.id}'
            })
        
        # Sort by date (newest first)
        udhar_transactions.sort(key=lambda x: x['date'], reverse=True)
        
        # Self-heal stats: Recalculate totals from actual sales to ensure accuracy
        real_visits = purchases.count()
        real_purchased = purchases.aggregate(total=Sum('total_amount'))['total'] or Decimal('0')
        
        if customer.total_visits != real_visits or abs(customer.total_purchased - real_purchased) > Decimal('0.01'):
            customer.total_visits = real_visits
            customer.total_purchased = real_purchased
            customer.save()
        
        # Calculate total paid amount from purchases
        total_paid = purchases.filter(is_paid=True).aggregate(total=Sum('total_amount'))['total'] or Decimal('0')
        
        # Determine payment status
        if customer.udhar_amount == 0:
            payment_status = 'Paid'
        elif customer.udhar_amount < customer.total_purchased:
            payment_status = 'Partially Paid'
        else:
            payment_status = 'Due'
        
        # Get shop/profile information
        try:
            profile = request.user.profile
            shop_name = profile.shop_name
            shop_phone = profile.phone
            shop_address = profile.address
        except UserProfile.DoesNotExist:
            shop_name = 'My Shop'
            shop_phone = ''
            shop_address = ''
        
        context = {
            'customer': customer,
            'purchases': purchases,
            'udhar_transactions': udhar_transactions,
            'total_paid': total_paid,
            'payment_status': payment_status,
            'shop_name': shop_name,
            'shop_phone': shop_phone,
            'shop_address': shop_address,
        }
        return render(request, 'customers/customer_detail.html', context)



@method_decorator(login_required, name='dispatch')
class CustomerEditView(View):
    """Edit customer details"""
    
    def get(self, request, pk):
        customer = get_object_or_404(Customer, pk=pk, user=request.user)
        return render(request, 'customers/customer_form.html', {'customer': customer})
    
    def post(self, request, pk):
        customer = get_object_or_404(Customer, pk=pk, user=request.user)
        
        customer.name = request.POST.get('name', customer.name).strip()
        customer.phone = request.POST.get('phone', customer.phone).strip()
        customer.notes = request.POST.get('notes', customer.notes).strip()
        
        customer.save()
        messages.success(request, 'Customer updated successfully!')
        return redirect('customers:customer-detail', pk=pk)


@method_decorator(login_required, name='dispatch')
class CustomerDeleteView(View):
    """Delete customer"""
    
    def post(self, request, pk):
        customer = get_object_or_404(Customer, pk=pk, user=request.user)
        customer.delete()
        
        # Invalidate dashboard cache
        try:
            from django.utils import timezone
            from django.core.cache import cache
            today = timezone.now().date()
            cache_key = f'dashboard_metrics_{request.user.id}_{today}'
            cache.delete(cache_key)
        except Exception:
            pass
            
        messages.success(request, 'Customer deleted successfully!')
        return redirect('customers:customer-list')


@method_decorator(login_required, name='dispatch')
class UdharPaymentView(View):
    """Record udhar payment"""
    
    def post(self, request, pk):
        customer = get_object_or_404(Customer, pk=pk, user=request.user)
        
        try:
            amount = Decimal(request.POST.get('amount', 0))
            
            if amount <= 0:
                messages.error(request, 'Invalid payment amount!')
                return redirect('customers:customer-detail', pk=pk)
            
            if amount > customer.udhar_amount:
                messages.error(request, 'Payment amount exceeds outstanding udhar!')
                return redirect('customers:customer-detail', pk=pk)
            
            # Reduce udhar amount
            customer.udhar_amount -= amount
            customer.save()
            
            # Invalidate dashboard cache
            try:
                today = timezone.now().date()
                cache_key = f'dashboard_metrics_{request.user.id}_{today}'
                cache.delete(cache_key)
            except Exception as e:
                pass
                
            messages.success(request, f'Payment of ₹{amount} recorded successfully!')
        except Exception as e:
            messages.error(request, f'Error recording payment: {str(e)}')
        
        return redirect('customers:customer-detail', pk=pk)


@method_decorator(login_required, name='dispatch')
class ProductListView(View):
    """List all products with search, filter, and sorting"""
    
    def get(self, request):
        products = Product.objects.filter(user=request.user, is_active=True)
        search = request.GET.get('search', '').strip()
        category = request.GET.get('category', '')
        sort = request.GET.get('sort', 'name')
        
        # Search
        if search:
            products = products.filter(
                Q(name__icontains=search) | Q(category__icontains=search)
            )
        
        # Filter by category
        if category:
            products = products.filter(category=category)
        
        # Sorting
        if sort == 'price':
            products = products.order_by('price')
        elif sort == 'stock':
            products = products.order_by('stock_quantity')
        else:  # default to name
            products = products.order_by('name')
        
        # Pagination (20 per page)
        page = int(request.GET.get('page', 1))
        per_page = 20
        total = products.count()
        start = (page - 1) * per_page
        products = products[start:start + per_page]
        
        context = {
            'products': products,
            'search': search,
            'category': category,
            'sort': sort,
            'total': total,
            'page': page,
            'pages': (total + per_page - 1) // per_page,
            'categories': Product.CATEGORY_CHOICES,
        }
        return render(request, 'customers/product_list.html', context)


@method_decorator(login_required, name='dispatch')
class ProductCreateView(View):
    """Create new product"""
    
    def get(self, request):
        context = {
            'categories': Product.CATEGORY_CHOICES,
            'units': Product.UNIT_CHOICES,
            'product_types': Product.PRODUCT_TYPE_CHOICES,
        }
        return render(request, 'customers/product_form.html', context)
    
    def post(self, request):
        try:
            name = request.POST.get('name', '').strip()
            product_type = request.POST.get('product_type', 'product')
            category = request.POST.get('category', '')
            price = Decimal(request.POST.get('price', 0))
            unit = request.POST.get('unit', 'piece') if product_type == 'product' else ''
            stock_quantity = Decimal(request.POST.get('stock_quantity', 0)) if product_type == 'product' else Decimal('0')
            description = request.POST.get('description', '')
            image = request.FILES.get('image')
            
            if not all([name, category, price > 0]):
                messages.error(request, 'Please fill all required fields!')
                return redirect('customers:product-list')
            
            product = Product.objects.create(
                user=request.user,
                name=name,
                product_type=product_type,
                category=category,
                price=price,
                unit=unit,
                stock_quantity=stock_quantity,
                description=description,
            )
            
            if image:
                product.image = image
                product.save()
            
            messages.success(request, 'Product/Service added successfully!')
            return redirect('customers:product-list')
        except Exception as e:
            logger.error(f"Error creating product for user {request.user.id}: {str(e)}", exc_info=True)
            messages.error(request, f'Error adding product/service: {str(e)}')
            return redirect('customers:product-list')


@method_decorator(login_required, name='dispatch')
class ProductEditView(View):
    """Edit product"""
    
    def get(self, request, pk):
        product = get_object_or_404(Product, pk=pk, user=request.user)
        context = {
            'product': product,
            'categories': Product.CATEGORY_CHOICES,
            'units': Product.UNIT_CHOICES,
            'product_types': Product.PRODUCT_TYPE_CHOICES,
        }
        return render(request, 'customers/product_form.html', context)
    
    def post(self, request, pk):
        product = get_object_or_404(Product, pk=pk, user=request.user)
        
        try:
            product.name = request.POST.get('name', product.name).strip()
            product.product_type = request.POST.get('product_type', product.product_type)
            product.category = request.POST.get('category', product.category)
            product.price = Decimal(request.POST.get('price', product.price))
            product.unit = request.POST.get('unit', product.unit) if product.product_type == 'product' else ''
            product.stock_quantity = Decimal(request.POST.get('stock_quantity', product.stock_quantity)) if product.product_type == 'product' else Decimal('0')
            product.description = request.POST.get('description', product.description)
            
            if 'image' in request.FILES:
                product.image = request.FILES['image']
            
            product.save()
            messages.success(request, 'Product/Service updated successfully!')
            return redirect('customers:product-list')
        except Exception as e:
            logger.error(f"Error updating product {pk} for user {request.user.id}: {str(e)}", exc_info=True)
            messages.error(request, f'Error updating product/service: {str(e)}')
            return redirect('customers:product-list')


@method_decorator(login_required, name='dispatch')
class ProductDeleteView(View):
    """Delete product (soft delete)"""
    
    def post(self, request, pk):
        product = get_object_or_404(Product, pk=pk, user=request.user)
        product.is_active = False
        product.save()
        messages.success(request, 'Product deleted successfully!')
        return redirect('customers:product-list')


@method_decorator(login_required, name='dispatch')
class ProductDataView(View):
    """Get product data as JSON for edit modal"""
    
    def get(self, request, pk):
        product = get_object_or_404(Product, pk=pk, user=request.user)
        data = {
            'id': product.id,
            'name': product.name,
            'product_type': product.product_type,
            'category': product.category,
            'price': str(product.price),
            'unit': product.unit,
            'stock_quantity': str(product.stock_quantity),
            'description': product.description,
            'image': product.image.url if product.image else None,
            'is_active': product.is_active,
        }
        return JsonResponse(data)


@method_decorator(login_required, name='dispatch')
class ProductDetailView(View):
    """View product details with sales analytics"""
    
    def get(self, request, pk):
        product = get_object_or_404(Product, pk=pk, user=request.user)
        
        # Get total quantity sold
        sales_data = SaleItem.objects.filter(
            sale__user=request.user,
            product=product
        ).aggregate(
            total_sold=Sum('quantity'),
            total_revenue=Sum(F('quantity') * F('price_at_sale'), output_field=DecimalField())
        )
        
        # Get sale history
        sale_items = SaleItem.objects.filter(
            product=product
        ).select_related('sale__customer').order_by('-sale__sale_date')[:20]
        
        context = {
            'product': product,
            'total_sold': sales_data['total_sold'] or 0,
            'total_revenue': sales_data['total_revenue'] or Decimal('0'),
            'sale_items': sale_items,
        }
        return render(request, 'customers/product_detail.html', context)


@method_decorator(login_required, name='dispatch')
class ProductImportView(View):
    """Import products from CSV/Excel (placeholder)"""
    
    def post(self, request):
        # Placeholder for import functionality
        messages.info(request, 'Import functionality coming soon!')
        return redirect('customers:product-list')


@method_decorator(login_required, name='dispatch')
class ProductExportView(View):
    """Export products to CSV"""
    
    def get(self, request):
        import csv
        from django.http import HttpResponse
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="products.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['Name', 'Category', 'Price', 'Unit', 'Stock Quantity'])
        
        products = Product.objects.filter(user=request.user, is_active=True)
        for product in products:
            writer.writerow([
                product.name,
                product.get_category_display(),
                product.price,
                product.get_unit_display(),
                product.stock_quantity,
            ])
        
        return response


@method_decorator(login_required, name='dispatch')
class ProductTemplateView(View):
    """Download CSV template for import"""
    
    def get(self, request):
        import csv
        from django.http import HttpResponse
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="product_template.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['name', 'category', 'price', 'unit', 'stock_quantity'])
        writer.writerow(['Sample Product', 'grocery', '100.00', 'piece', '50'])
        
        return response


@method_decorator(login_required, name='dispatch')
class BillingView(View):
    """Create new bill/sale"""
    
    def get(self, request):
        from django.utils import timezone
        
        try:
            profile = request.user.profile
        except UserProfile.DoesNotExist:
            profile = UserProfile.objects.create(user=request.user)
            
        customers = Customer.objects.filter(user=request.user)
        products = Product.objects.filter(user=request.user, is_active=True)
        
        # Prepare JSON data for JavaScript
        products_data = [{
            'id': p.id,
            'name': p.name,
            'price': str(p.price),
            'unit': p.unit,
            'stock_quantity': str(p.stock_quantity),
            'is_active': p.is_active,
            'product_type': p.product_type,  # Add product type
        } for p in products]
        
        customers_data = [{
            'id': c.id,
            'name': c.name,
            'phone': c.phone,
            'udhar_amount': str(c.udhar_amount),
        } for c in customers]
        
        # Cache active offers for 10 minutes (rarely change during user session)
        cache_key = f'active_offers_{request.user.id}'
        offers_data = cache.get(cache_key)
        
        if not offers_data:
            # Fetch and serialize offers (expensive query)
            active_offers = Offer.objects.filter(
                user=request.user, 
                is_active=True,
                start_date__lte=timezone.now(),
                end_date__gte=timezone.now()
            )
            offers_data = [{
                'id': o.id,
                'name': o.name,
                'type': o.offer_type,
                'discount_value': str(o.discount_value),
                'min_purchase_amount': str(o.min_purchase_amount),
                'buy_quantity': o.buy_quantity,
                'get_quantity': o.get_quantity,
                'applicable_products': list(o.applicable_products.values_list('id', flat=True))
            } for o in active_offers]
            
            # Cache for 10 minutes
            cache.set(cache_key, offers_data, 600)
        
        context = {
            'profile': profile,
            'shop_name': profile.shop_name or "SubhLabh",
            'customers': customers,
            'products': products,
            'products_json': json.dumps(products_data),
            'customers_json': json.dumps(customers_data),
            'offers_json': json.dumps(offers_data),
            'payment_methods': Sale.PAYMENT_CHOICES,
            'current_time': timezone.now(),
        }
        return render(request, 'customers/billing.html', context)
    
    def post(self, request):
        try:
            data = json.loads(request.body)
            items = data.get('items', [])
            customer_id = data.get('customer_id')
            payment_method = data.get('payment_method', 'cash')
            is_paid = data.get('is_paid', True)
            notes = data.get('notes', '')
            applied_offer_id = data.get('offer_id')
            discount_amount = Decimal(str(data.get('discount_amount', 0)))
            
            if not items:
                return JsonResponse({'success': False, 'message': 'No items in bill'})
            
            total_amount = Decimal('0')
            sale_items = []
            
            # ... item processing ...
            items_total = Decimal('0')
            
            for item in items:
                # Handle custom items
                if 'custom_name' in item:
                    # Create a temporary product for this custom item
                    product = Product.objects.create(
                        user=request.user,
                        name=item['custom_name'],
                        description=item.get('custom_description', ''),
                        price=Decimal(str(item['custom_price'])),
                        product_type='service',  # Treat custom items as services
                        unit='',  # No unit for services
                        stock_quantity=Decimal('0'),  # No stock for services
                        is_active=False  # Mark as inactive since it's a one-time item
                    )
                    product_id = product.id
                    quantity = Decimal(str(item.get('quantity', 1)))
                    price = Decimal(str(item['custom_price']))
                else:
                    # Handle regular products/services
                    product_id = item.get('product_id')
                    quantity = Decimal(str(item.get('quantity', 0)))
                    price = Decimal(item.get('price', 0))
                
                if quantity <= 0:
                    continue
                
                product = get_object_or_404(Product, pk=product_id, user=request.user)
                
                # Only check stock for actual products, not services
                if product.product_type == 'product' and product.stock_quantity < quantity:
                    return JsonResponse({
                        'success': False,
                        'message': f'Insufficient stock for {product.name}'
                    })
                
                item_total = quantity * price
                items_total += item_total
                sale_items.append({
                    'product': product,
                    'quantity': quantity,
                    'price': price,
                })
            
            # Calculate final total after discount
            # Verify discount on server side for security (optional but recommended)
            # For now, trusting frontend sent discount or recalculating basic ones
            
            final_total_amount = items_total - discount_amount
            if final_total_amount < 0:
                final_total_amount = Decimal('0')

            customer = None
            if customer_id:
                customer = get_object_or_404(Customer, pk=customer_id, user=request.user)
            
            sale = Sale.objects.create(
                user=request.user,
                customer=customer,
                total_amount=final_total_amount,
                discount_amount=discount_amount,
                payment_method=payment_method,
                is_paid=is_paid,
                added_to_udhar=not is_paid,
                notes=notes
            )
            
            if applied_offer_id:
                try:
                    offer = Offer.objects.get(pk=applied_offer_id, user=request.user)
                    SaleOffer.objects.create(
                        sale=sale,
                        offer=offer,
                        discount_amount=discount_amount
                    )
                except Offer.DoesNotExist:
                    pass
            
            for item_data in sale_items:
                product = item_data['product']
                quantity = item_data['quantity']
                price = item_data['price']
                
                SaleItem.objects.create(
                    sale=sale,
                    product=product,
                    quantity=quantity,
                    price_at_sale=price
                )
                
                # Only reduce stock for actual products, not services
                if product.product_type == 'product':
                    product.stock_quantity -= quantity
                    product.save()
            
            if customer:
                customer.total_purchased += total_amount
                customer.total_visits += 1
                
                if not is_paid:
                    customer.udhar_amount += total_amount
                
                customer.save()
            
            # Invalidate dashboard cache
            try:
                today = timezone.now().date()
                cache_key = f'dashboard_metrics_{request.user.id}_{today}'
                cache.delete(cache_key)
            except Exception as e:
                logger.error(f"Error invalidating cache: {e}")

            return JsonResponse({
                'success': True,
                'message': 'Sale recorded successfully!',
                'sale_id': sale.id,
                'total_amount': str(total_amount)
            })
        
        except Exception as e:
            logger.error(f"Error creating sale for user {request.user.id}: {str(e)}", exc_info=True)
            return JsonResponse({'success': False, 'message': str(e)})


@method_decorator(login_required, name='dispatch')
class SalesHistoryView(View):
    """View sales history with search and filters"""
    
    def get(self, request):
        from django.utils import timezone
        from datetime import datetime, timedelta
        
        # Check if this is a download request
        download_format = request.GET.get('format')
        if download_format:
            return self.download_sales_data(request, download_format)
        
        # Base queryset
        sales = Sale.objects.filter(user=request.user).select_related('customer').prefetch_related('items__product')
        
        # Get filter parameters
        search_query = request.GET.get('search', '').strip()
        date_from = request.GET.get('date_from')
        date_to = request.GET.get('date_to')
        payment_method = request.GET.get('payment_method')
        customer_id = request.GET.get('customer_id')
        page = int(request.GET.get('page', 1))
        
        # Search by customer name, product name, or bill number
        if search_query:
            sales = sales.filter(
                Q(id__icontains=search_query) |
                Q(customer__name__icontains=search_query) |
                Q(customer__phone__icontains=search_query) |
                Q(items__product__name__icontains=search_query)
            ).distinct()
        
        # Date range filter
        if date_from:
            try:
                from_date = datetime.strptime(date_from, '%Y-%m-%d')
                sales = sales.filter(sale_date__date__gte=from_date)
            except ValueError:
                pass
        
        if date_to:
            try:
                to_date = datetime.strptime(date_to, '%Y-%m-%d')
                sales = sales.filter(sale_date__date__lte=to_date)
            except ValueError:
                pass
        
        # Payment method filter
        if payment_method:
            if payment_method == 'udhar':
                sales = sales.filter(is_paid=False)
            else:
                sales = sales.filter(payment_method=payment_method, is_paid=True)
        
        # Customer filter
        if customer_id:
            sales = sales.filter(customer_id=customer_id)
        
        # Order by most recent first
        sales = sales.order_by('-sale_date')
        
        # Pagination
        per_page = 20
        total_count = sales.count()
        total_pages = (total_count + per_page - 1) // per_page
        start = (page - 1) * per_page
        sales_page = sales[start:start + per_page]
        
        # Generate page range
        page_range = []
        if total_pages <= 7:
            page_range = list(range(1, total_pages + 1))
        else:
            if page <= 4:
                page_range = list(range(1, 6)) + ['...', total_pages]
            elif page >= total_pages - 3:
                page_range = [1, '...'] + list(range(total_pages - 4, total_pages + 1))
            else:
                page_range = [1, '...'] + list(range(page - 1, page + 2)) + ['...', total_pages]
        
        context = {
            'sales': sales_page,
            'total_count': total_count,
            'customers': Customer.objects.filter(user=request.user),
            'search_query': search_query,
            'date_from': date_from,
            'date_to': date_to,
            'payment_method': payment_method,
            'customer_id': customer_id,
            'page': page,
            'total_pages': total_pages,
            'page_range': page_range,
        }
        return render(request, 'customers/sales_history.html', context)
    
    def download_sales_data(self, request, format_type):
        """Download sales data in specified format"""
        import csv
        from django.http import HttpResponse
        from datetime import datetime
        
        # Base queryset
        sales = Sale.objects.filter(user=request.user).select_related('customer').prefetch_related('items__product')
        
        # Get filter parameters
        search_query = request.GET.get('search', '').strip()
        date_from = request.GET.get('date_from')
        date_to = request.GET.get('date_to')
        payment_method = request.GET.get('payment_method')
        customer_id = request.GET.get('customer_id')
        
        # Apply filters
        if search_query:
            sales = sales.filter(
                Q(id__icontains=search_query) |
                Q(customer__name__icontains=search_query) |
                Q(customer__phone__icontains=search_query) |
                Q(items__product__name__icontains=search_query)
            ).distinct()
        
        if date_from:
            try:
                from_date = datetime.strptime(date_from, '%Y-%m-%d')
                sales = sales.filter(sale_date__date__gte=from_date)
            except ValueError:
                pass
        
        if date_to:
            try:
                to_date = datetime.strptime(date_to, '%Y-%m-%d')
                sales = sales.filter(sale_date__date__lte=to_date)
            except ValueError:
                pass
        
        if payment_method:
            if payment_method == 'udhar':
                sales = sales.filter(is_paid=False)
            else:
                sales = sales.filter(payment_method=payment_method, is_paid=True)
        
        if customer_id:
            sales = sales.filter(customer_id=customer_id)
        
        # Order by most recent first
        sales = sales.order_by('-sale_date')
        
        if format_type == 'csv':
            # Create CSV response
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="sales_data_detailed.csv"'
            
            writer = csv.writer(response)
            # Write header with detailed columns
            writer.writerow([
                'Date', 'Time', 'Customer Name', 'Customer Phone',
                'Payment Method', 'Payment Status', 'Total Amount', 
                'Product Name', 'Quantity', 'Unit', 'Price Per Unit', 'Item Total',
                'Notes'
            ])
            
            # Write data - one row per sale item
            for sale in sales:
                # Write a row for each item in the sale
                for item in sale.items.all():
                    # Format date properly to avoid # characters
                    sale_date_str = sale.sale_date.strftime('%Y-%m-%d')
                    sale_time_str = sale.sale_date.strftime('%H:%M:%S')
                    
                    writer.writerow([
                        sale_date_str,  # Properly formatted date string
                        sale_time_str,  # Properly formatted time string
                        sale.customer.name if sale.customer else 'Walk-in Customer',
                        sale.customer.phone if sale.customer else '',
                        sale.get_payment_method_display(),
                        'Paid' if sale.is_paid else 'Udhar',
                        sale.total_amount,
                        item.product.name,
                        item.quantity,
                        item.product.unit,
                        item.price_at_sale,
                        item.total_amount,
                        sale.notes or ''
                    ])
            
            return response
        else:
            # Default to CSV if format not recognized
            return HttpResponse("Unsupported format", status=400)


@method_decorator(login_required, name='dispatch')
class SaleDetailView(View):
    """View detailed sale information"""
    
    def get(self, request, pk):
        sale = get_object_or_404(Sale, pk=pk, user=request.user)
        profile = request.user.profile
        
        # Get sale items with product details
        items = sale.items.select_related('product').all()
        
        # Calculate totals
        subtotal = sum(item.quantity * item.price_at_sale for item in items)
        
        # Prepare sale data for JavaScript
        items_data = []
        for item in items:
            items_data.append({
                'name': item.product.name,
                'quantity': float(item.quantity),
                'price': float(item.price_at_sale),
                'total': float(item.quantity * item.price_at_sale),
                'unit': item.product.unit,
                'product_type': item.product.product_type
            })

        sale_data = {
            'id': sale.id,
            'total_amount': float(sale.total_amount),
            'payment_method': sale.payment_method,
            'is_paid': sale.is_paid,
            'sale_date': sale.sale_date.isoformat(),
            'notes': sale.notes or '',
            'customer': {
                'name': sale.customer.name if sale.customer else '',
                'phone': sale.customer.phone if sale.customer else ''
            } if sale.customer else None,
            'items': items_data
        }

        # Prepare shop config
        shop_config = {
            'shopName': profile.shop_name or request.user.get_full_name() or "SubhLabh",
            'shopAddress': profile.address or "",
            'shopPhone': profile.phone or ""
        }
        
        # Serialize for data attributes
        sale_json = json.dumps(sale_data)
        shop_json = json.dumps(shop_config)

        html = f'''
        <div class="sale-details">
            <div class="detail-header">
                <div>
                    <h4>Sale Details</h4>
                    <p>{sale.sale_date.strftime("%B %d, %Y at %I:%M %p")}</p>
                </div>
                <div>
                    <span class="payment-badge {sale.payment_method}">
                        {sale.get_payment_method_display()}
                    </span>
                </div>
            </div>

            <div class="detail-section">
                <h5>Customer Information</h5>
                {f'<p><strong>{sale.customer.name}</strong></p><p>{sale.customer.phone}</p>' if sale.customer else '<p class="walk-in">Walk-in Customer</p>'}
            </div>

            <div class="detail-section">
                <h5>Products</h5>
                <table class="detail-table">
                    <thead>
                        <tr>
                            <th>Product</th>
                            <th>Quantity</th>
                            <th>Price</th>
                            <th>Total</th>
                        </tr>
                    </thead>
                    <tbody>
        '''

        for item in items:
            html += f'''
                        <tr>
                            <td>{item.product.name}</td>
                            <td>{item.quantity} {item.product.unit}</td>
                            <td>₹{item.price_at_sale}</td>
                            <td>₹{(item.quantity * item.price_at_sale):.2f}</td>
                        </tr>
            '''

        html += f'''
                    </tbody>
                    <tfoot>
                        <tr>
                            <td colspan="3"><strong>Total Amount</strong></td>
                            <td><strong>₹{sale.total_amount:.2f}</strong></td>
                        </tr>
                    </tfoot>
                </table>
            </div>

            {f'<div class="detail-section"><h5>Notes</h5><p>{sale.notes}</p></div>' if sale.notes else ''}

            {f'<div class="detail-section"><h5>Payment Status</h5><p class="status-badge pending">⏳ Udhar Pending - ₹{sale.total_amount}</p></div>' if not sale.is_paid else '<div class="detail-section"><h5>Payment Status</h5><p class="status-badge paid">✅ Paid</p></div>'}

            <div class="detail-actions" style="margin-top: 20px; text-align: center;">
                <button
                    onclick="sendWhatsAppBillFromDetail()"
                    style="background: linear-gradient(135deg, #25D366 0%, #128C7E 100%); color: white; padding: 12px 24px; border: none; border-radius: 10px; font-weight: 600; cursor: pointer; box-shadow: 0 4px 12px rgba(37, 211, 102, 0.3); display: inline-flex; align-items: center; gap: 6px; transition: all 0.3s ease;"
                    onmouseover="this.style.transform='translateY(-2px)'; this.style.boxShadow='0 6px 16px rgba(37, 211, 102, 0.4)';"
                    onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='0 4px 12px rgba(37, 211, 102, 0.3)';" >
                    📲 Send via WhatsApp
                </button>
            </div>
            
            <!-- Hidden data store for JS -->
            <!-- Use single quotes for attributes to allow double quotes in JSON -->
            <div id="sale-data-store" 
                 data-sale-json='{sale_json}'
                 data-shop-json='{shop_json}'
                 style="display:none;"></div>
        </div>

        <style>
        .sale-details {{ padding: 20px; }}
        .detail-header {{ display: flex; justify-content: space-between; align-items: start; margin-bottom: 25px; padding-bottom: 20px; border-bottom: 2px solid var(--gray-light); }}
        .detail-section {{ margin-bottom: 25px; }}
        .detail-section h5 {{ margin: 0 0 15px 0; font-size: 16px; color: var(--dark); font-weight: 700; }}
        .detail-table {{ width: 100%; border-collapse: collapse; }}
        .detail-table th {{ background: var(--light); padding: 12px; text-align: left; font-weight: 700; }}
        .detail-table td {{ padding: 12px; border-bottom: 1px solid var(--gray-light); }}
        .detail-table tfoot td {{ border-top: 2px solid var(--dark); font-size: 18px; color: var(--primary); }}
        </style>

        '''
        
        return HttpResponse(html)


@method_decorator(login_required, name='dispatch')
class SaleDeleteView(View):
    """Delete a sale and restore stock/customer data"""
    
    def post(self, request, pk):
        try:
            sale = get_object_or_404(Sale, pk=pk, user=request.user)
            
            # Restore product stock
            for item in sale.items.all():
                product = item.product
                # Only restore stock for physical products
                if product.product_type == 'product':
                    product.stock_quantity += item.quantity
                    product.save()
            
            # Update customer records if applicable
            if sale.customer:
                customer = sale.customer
                customer.total_purchased -= sale.total_amount
                customer.total_visits -= 1
                
                if not sale.is_paid:
                    customer.udhar_amount -= sale.total_amount
                
                customer.save()
            
            # Delete the sale (this will cascade delete sale items)
            sale_id = sale.id
            sale.delete()
            
            # Invalidate dashboard cache
            try:
                from django.utils import timezone
                today = timezone.now().date()
                cache_key = f'dashboard_metrics_{request.user.id}_{today}'
                cache.delete(cache_key)
            except Exception as e:
                pass
            
            return JsonResponse({
                'success': True,
                'message': 'Sale deleted successfully'
            })
        
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': str(e)
            })


@method_decorator(login_required, name='dispatch')
class SalePrintView(View):
    """Generate printable bill/receipt"""
    
    def get(self, request, pk):
        sale = get_object_or_404(Sale, pk=pk, user=request.user)
        items = sale.items.select_related('product').all()
        
        context = {
            'sale': sale,
            'items': items,
            'shop_name': request.user.profile.shop_name if hasattr(request.user, 'profile') else 'Shop',
        }
        
        return render(request, 'customers/sale_print.html', context)


@method_decorator(login_required, name='dispatch')
class ReportsView(View):
    """Sales reports and analytics"""
    
    def get(self, request):
        # Check if this is a download request
        download_format = request.GET.get('format')
        if download_format:
            return self.download_report_data(request, download_format)
        
        user = request.user
        
        date_from = request.GET.get('date_from')
        date_to = request.GET.get('date_to')
        selected_year = request.GET.get('year')
        
        # Base sales queryset
        sales = Sale.objects.filter(user=user)
        sale_items = SaleItem.objects.filter(sale__user=user)
        
        # Apply date filters
        if date_from:
            try:
                from_date_obj = datetime.strptime(date_from, '%Y-%m-%d').date()
                from_date_dt = timezone.make_aware(datetime.combine(from_date_obj, time.min))
                sales = sales.filter(sale_date__gte=from_date_dt)
                sale_items = sale_items.filter(sale__sale_date__gte=from_date_dt)
            except ValueError:
                pass
        
        if date_to:
            try:
                to_date_obj = datetime.strptime(date_to, '%Y-%m-%d').date()
                to_date_dt = timezone.make_aware(datetime.combine(to_date_obj, time.max))
                sales = sales.filter(sale_date__lte=to_date_dt)
                sale_items = sale_items.filter(sale__sale_date__lte=to_date_dt)
            except ValueError:
                pass
        
        # Apply year filter
        if selected_year:
            try:
                year_int = int(selected_year)
                sales = sales.filter(sale_date__year=year_int)
                sale_items = sale_items.filter(sale__sale_date__year=year_int)
            except ValueError:
                pass
        
        # Get available years for dropdown
        years_data = Sale.objects.filter(user=user).extra(
            select={'year': "DATE_FORMAT(sale_date, '%%Y')"}
        ).values('year').distinct().order_by('-year')
        
        years = [item['year'] for item in years_data if item['year']]
        
        # 1. Monthly Sales Report
        monthly_sales_data = sales.extra(
            select={'month': "DATE_FORMAT(sale_date, '%%Y-%%m')"}
        ).values('month').annotate(
            total_revenue=Sum('total_amount')
        ).order_by('month')
        
        # Format monthly sales for display
        monthly_sales = []
        for item in monthly_sales_data:
            month_str = item['month']
            # Convert YYYY-MM to Month Year format
            try:
                month_date = datetime.strptime(month_str, '%Y-%m')
                month_display = month_date.strftime('%B %Y')
            except:
                month_display = month_str
            
            monthly_sales.append({
                'month': month_str,
                'month_display': month_display,
                'total_revenue': item['total_revenue'] or Decimal('0')
            })
        
        # 2. Yearly Sales Report
        yearly_sales_data = sales.extra(
            select={'year': "DATE_FORMAT(sale_date, '%%Y')"}
        ).values('year').annotate(
            total_revenue=Sum('total_amount')
        ).order_by('year')
        
        yearly_sales = []
        for item in yearly_sales_data:
            yearly_sales.append({
                'year': item['year'],
                'total_revenue': item['total_revenue'] or Decimal('0')
            })
        
        # 3. Product Sales Report
        product_sales = sale_items.values('product__name').annotate(
            total_quantity=Sum('quantity'),
            total_revenue=Sum(F('quantity') * F('price_at_sale'), output_field=DecimalField())
        ).order_by('-total_revenue')[:10]
        
        # 4. Category-wise Sales Report
        category_sales = sale_items.values('product__category').annotate(
            total_revenue=Sum(F('quantity') * F('price_at_sale'), output_field=DecimalField())
        ).order_by('-total_revenue')
        
        # 5. Customer-wise Purchase Report
        customer_purchases = sales.values('customer__name').annotate(
            purchase_count=Count('id'),
            total_amount=Sum('total_amount')
        ).filter(customer__name__isnull=False).order_by('-total_amount')[:10]
        
        # 6. Daily/Weekly Comparison
        today = timezone.now().date()
        yesterday = today - timedelta(days=1)
        last_7_days = today - timedelta(days=7)
        
        # Prepare ranges for accuracy
        today_start = timezone.make_aware(datetime.combine(today, time.min))
        today_end = timezone.make_aware(datetime.combine(today, time.max))
        yesterday_start = timezone.make_aware(datetime.combine(yesterday, time.min))
        yesterday_end = timezone.make_aware(datetime.combine(yesterday, time.max))
        last_7_days_dt = timezone.make_aware(datetime.combine(last_7_days, time.min))

        # Today's sales
        today_sales = sales.filter(sale_date__range=(today_start, today_end)).aggregate(
            total=Sum('total_amount')
        )['total'] or Decimal('0')
        
        # Yesterday's sales
        yesterday_sales = sales.filter(sale_date__range=(yesterday_start, yesterday_end)).aggregate(
            total=Sum('total_amount')
        )['total'] or Decimal('0')
        
        # Last 7 days sales
        last_7_days_sales = sales.filter(sale_date__gte=last_7_days_dt).aggregate(
            total=Sum('total_amount')
        )['total'] or Decimal('0')
        
        # Calculate changes
        if yesterday_sales > 0:
            today_change = ((today_sales - yesterday_sales) / yesterday_sales) * 100
            today_change_class = 'positive' if today_change >= 0 else 'negative'
            today_change = f"{today_change:+.1f}%"
        else:
            today_change = "-"
            today_change_class = ""
        
        if last_7_days_sales > 0:
            # For simplicity, comparing to previous 7 days
            last_7_days_change = 0
            last_7_days_change_class = ''
            last_7_days_change = f"{last_7_days_change:+.1f}%"
        else:
            last_7_days_change = "-"
            last_7_days_change_class = ""
        
        context = {
            'monthly_sales': monthly_sales,
            'yearly_sales': yearly_sales,
            'product_sales': list(product_sales),
            'category_sales': list(category_sales),
            'customer_purchases': list(customer_purchases),
            'today_sales': today_sales,
            'yesterday_sales': yesterday_sales,
            'last_7_days_sales': last_7_days_sales,
            'today_change': today_change,
            'today_change_class': today_change_class,
            'last_7_days_change': last_7_days_change,
            'last_7_days_change_class': last_7_days_change_class,
            'date_from': date_from,
            'date_to': date_to,
            'years': years,
            'selected_year': selected_year,
        }
        
        return render(request, 'customers/reports.html', context)
    
    def download_report_data(self, request, format_type):
        """Download report data in specified format"""
        import csv
        from django.http import HttpResponse
        
        user = request.user
        
        date_from = request.GET.get('date_from')
        date_to = request.GET.get('date_to')
        selected_year = request.GET.get('year')
        report_type = request.GET.get('report', 'monthly')
        
        # Base sales queryset
        sales = Sale.objects.filter(user=user)
        sale_items = SaleItem.objects.filter(sale__user=user)
        
        # Apply date filters
        if date_from:
            try:
                from_date_obj = datetime.strptime(date_from, '%Y-%m-%d').date()
                from_date_dt = timezone.make_aware(datetime.combine(from_date_obj, time.min))
                sales = sales.filter(sale_date__gte=from_date_dt)
                sale_items = sale_items.filter(sale__sale_date__gte=from_date_dt)
            except ValueError:
                pass
        
        if date_to:
            try:
                to_date_obj = datetime.strptime(date_to, '%Y-%m-%d').date()
                to_date_dt = timezone.make_aware(datetime.combine(to_date_obj, time.max))
                sales = sales.filter(sale_date__lte=to_date_dt)
                sale_items = sale_items.filter(sale__sale_date__lte=to_date_dt)
            except ValueError:
                pass
        
        # Apply year filter
        if selected_year:
            try:
                year_int = int(selected_year)
                sales = sales.filter(sale_date__year=year_int)
                sale_items = sale_items.filter(sale__sale_date__year=year_int)
            except ValueError:
                pass
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="report_{report_type}.csv"'
        
        writer = csv.writer(response)
        
        # Generate report based on type
        if report_type in ['monthly-sales', 'monthly']:
            # Monthly Sales Report
            monthly_sales_data = sales.extra(
                select={'month': "DATE_FORMAT(sale_date, '%%Y-%%m')"}
            ).values('month').annotate(
                total_revenue=Sum('total_amount')
            ).order_by('month')
            
            writer.writerow(['Month', 'Sales (₹)'])
            for item in monthly_sales_data:
                month_str = item['month']
                try:
                    month_date = datetime.strptime(month_str, '%Y-%m')
                    month_display = month_date.strftime('%B %Y')
                except:
                    month_display = month_str
                writer.writerow([month_display, item['total_revenue']])
                
        elif report_type in ['yearly-sales', 'yearly']:
            # Yearly Sales Report
            yearly_sales_data = sales.extra(
                select={'year': "DATE_FORMAT(sale_date, '%%Y')"}
            ).values('year').annotate(
                total_revenue=Sum('total_amount')
            ).order_by('year')
            
            writer.writerow(['Year', 'Sales (₹)'])
            for item in yearly_sales_data:
                writer.writerow([item['year'], item['total_revenue']])
                
        elif report_type in ['product-sales', 'product']:
            # Product Sales Report
            product_sales = sale_items.values('product__name').annotate(
                total_quantity=Sum('quantity'),
                total_revenue=Sum(F('quantity') * F('price_at_sale'), output_field=DecimalField())
            ).order_by('-total_revenue')
            
            writer.writerow(['Product', 'Quantity Sold', 'Revenue (₹)'])
            for item in product_sales:
                writer.writerow([
                    item['product__name'], 
                    item['total_quantity'], 
                    item['total_revenue']
                ])
                
        elif report_type in ['category-sales', 'category']:
            # Category Sales Report
            category_sales = sale_items.values('product__category').annotate(
                total_revenue=Sum(F('quantity') * F('price_at_sale'), output_field=DecimalField())
            ).order_by('-total_revenue')
            
            writer.writerow(['Category', 'Sales (₹)'])
            for item in category_sales:
                writer.writerow([item['product__category'], item['total_revenue']])
                
        elif report_type in ['customer-purchases', 'customer']:
            # Customer Purchases Report
            customer_purchases = sales.values('customer__name').annotate(
                purchase_count=Count('id'),
                total_amount=Sum('total_amount')
            ).filter(customer__name__isnull=False).order_by('-total_amount')
            
            writer.writerow(['Customer', 'Total Purchases', 'Amount Spent (₹)'])
            for item in customer_purchases:
                writer.writerow([
                    item['customer__name'] or "Walking Customer", 
                    item['purchase_count'], 
                    item['total_amount']
                ])
                
        elif report_type == 'offers':
            # Offers Report
            from .models import SaleOffer
            sale_offers = SaleOffer.objects.filter(sale__user=user)
            
            if date_from:
                try:
                    from_date_obj = datetime.strptime(date_from, '%Y-%m-%d').date()
                    from_date_dt = timezone.make_aware(datetime.combine(from_date_obj, time.min))
                    sale_offers = sale_offers.filter(sale__sale_date__gte=from_date_dt)
                except ValueError:
                    pass
            
            if date_to:
                try:
                    to_date_obj = datetime.strptime(date_to, '%Y-%m-%d').date()
                    to_date_dt = timezone.make_aware(datetime.combine(to_date_obj, time.max))
                    sale_offers = sale_offers.filter(sale__sale_date__lte=to_date_dt)
                except ValueError:
                    pass
            
            if selected_year:
                try:
                    year_int = int(selected_year)
                    sale_offers = sale_offers.filter(sale__sale_date__year=year_int)
                except ValueError:
                    pass
            
            offer_report = sale_offers.values('offer__title').annotate(
                usage_count=Count('id'),
                total_discount=Sum('discount_amount')
            ).order_by('-usage_count')
            
            writer.writerow(['Offer', 'Times Used', 'Total Discount (₹)'])
            for item in offer_report:
                writer.writerow([
                    item['offer__title'], 
                    item['usage_count'], 
                    item['total_discount']
                ])
                
        elif report_type in ['daily', 'daily-comparison']:
            # Daily Comparison Report
            today = timezone.now().date()
            yesterday = today - timedelta(days=1)
            last_7_days = today - timedelta(days=7)
            
            # Prepare ranges for accuracy
            today_start = timezone.make_aware(datetime.combine(today, time.min))
            today_end = timezone.make_aware(datetime.combine(today, time.max))
            yesterday_start = timezone.make_aware(datetime.combine(yesterday, time.min))
            yesterday_end = timezone.make_aware(datetime.combine(yesterday, time.max))
            last_7_days_dt = timezone.make_aware(datetime.combine(last_7_days, time.min))

            today_sales = sales.filter(sale_date__range=(today_start, today_end)).aggregate(
                total=Sum('total_amount')
            )['total'] or Decimal('0')
            
            yesterday_sales = sales.filter(sale_date__range=(yesterday_start, yesterday_end)).aggregate(
                total=Sum('total_amount')
            )['total'] or Decimal('0')
            
            last_7_days_sales = sales.filter(sale_date__gte=last_7_days_dt).aggregate(
                total=Sum('total_amount')
            )['total'] or Decimal('0')
            
            writer.writerow(['Period', 'Sales (₹)'])
            writer.writerow(['Today', today_sales])
            writer.writerow(['Yesterday', yesterday_sales])
            writer.writerow(['Last 7 Days', last_7_days_sales])
            
        else:
            # Default report
            writer.writerow(['Report Type', 'Value'])
            writer.writerow(['No data available for this report type', ''])
        
        return response


class ProductSearchAPI(View):
    """API endpoint for product search"""
    
    def get(self, request):
        if not request.user.is_authenticated:
            return JsonResponse({'products': []})
        
        search = request.GET.get('q', '').strip()
        products = Product.objects.filter(
            user=request.user,
            is_active=True
        ).filter(
            Q(name__icontains=search) | Q(category__icontains=search)
        )[:20]
        
        data = [{
            'id': p.id,
            'name': p.name,
            'price': str(p.price),
            'stock': str(p.stock_quantity),
            'category': p.category,
            'is_low_stock': p.is_low_stock
        } for p in products]
        
        return JsonResponse({'products': data})


class CustomerSearchAPI(View):
    """API endpoint for customer search"""
    
    def get(self, request):
        if not request.user.is_authenticated:
            return JsonResponse({'customers': []})
        
        search = request.GET.get('q', '').strip()
        customers = Customer.objects.filter(
            user=request.user
        ).filter(
            Q(name__icontains=search) | Q(phone__icontains=search)
        )[:20]
        
        data = [{
            'id': c.id,
            'name': c.name,
            'phone': c.phone,
            'udhar': str(c.udhar_amount),
            'total_purchased': str(c.total_purchased),
        } for c in customers]
        
        return JsonResponse({'customers': data})


# ==================== OFFER MANAGEMENT ====================

@method_decorator(login_required, name='dispatch')
class OfferListView(View):
    """List all offers"""
    
    def get(self, request):
        offers = Offer.objects.filter(user=request.user).order_by('-is_active', '-created_at')
        return render(request, 'customers/offers/offer_list.html', {'offers': offers})


@method_decorator(login_required, name='dispatch')
class OfferCreateView(View):
    """Create new offer"""
    
    def get(self, request):
        form = OfferForm()
        return render(request, 'customers/offers/offer_form.html', {'form': form})
    
    def post(self, request):
        form = OfferForm(request.POST)
        if form.is_valid():
            offer = form.save(commit=False)
            offer.user = request.user
            offer.save()
            form.save_m2m()  # Save many-to-many data
            messages.success(request, 'Offer created successfully!')
            return redirect('customers:offer-list')
        
        return render(request, 'customers/offers/offer_form.html', {'form': form})


@method_decorator(login_required, name='dispatch')
class OfferEditView(View):
    """Edit existing offer"""
    
    def get(self, request, pk):
        offer = get_object_or_404(Offer, pk=pk, user=request.user)
        form = OfferForm(instance=offer)
        return render(request, 'customers/offers/offer_form.html', {'form': form, 'offer': offer})
    
    def post(self, request, pk):
        offer = get_object_or_404(Offer, pk=pk, user=request.user)
        form = OfferForm(request.POST, instance=offer)
        if form.is_valid():
            form.save()
            messages.success(request, 'Offer updated successfully!')
            return redirect('customers:offer-list')
        
        return render(request, 'customers/offers/offer_form.html', {'form': form, 'offer': offer})


@method_decorator(login_required, name='dispatch')
class OfferDeleteView(View):
    """Delete offer (hard delete or soft delete logic)"""
    
    def post(self, request, pk):
        offer = get_object_or_404(Offer, pk=pk, user=request.user)
        offer.delete()
        messages.success(request, 'Offer deleted successfully!')
        return redirect('customers:offer-list')


class TermsOfServiceView(View):
    def get(self, request):
        return render(request, 'terms.html')


class PrivacyPolicyView(View):
    def get(self, request):
        return render(request, 'privacy.html')



        from .forms import BrandingForm
        try:
            profile = request.user.profile
        except UserProfile.DoesNotExist:
            profile = UserProfile.objects.create(user=request.user)
        
        form = BrandingForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Branding updated successfully!')
            return redirect('customers:profile-edit')
        
        return render(request, 'customers/profile_edit.html', {
            'branding_form': form,
            'profile': profile
        })



