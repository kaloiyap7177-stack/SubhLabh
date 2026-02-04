from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.core.mail import EmailMessage
from django.contrib import messages
from django.utils import timezone
from django.conf import settings
from django.http import JsonResponse
from datetime import timedelta
import json

from .forms import (
    SignupForm, LoginForm, OTPVerificationForm,
    PasswordResetForm, SetNewPasswordForm, CreatePasswordForm, OfferForm
)
from .models import OTPVerification, EmailLog, CustomUser

User = get_user_model()


class EmailService:
    """Service to handle email sending for OTP"""
    
    @staticmethod
    def send_otp_email(email, otp_code, purpose='signup'):
        """
        Send OTP via email
        Args:
            email: recipient email
            otp_code: 6-digit OTP
            purpose: 'signup', 'login', or 'reset'
        """
        subject_map = {
            'signup': 'Verify Your Email - Subhlabh Signup',
            'login': 'Login Verification - Subhlabh',
            'reset': 'Password Reset - Subhlabh'
        }
        
        subject = subject_map.get(purpose, 'Verification Code - Subhlabh')
        
        # Email body with HTML
        html_message = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }}
                .container {{ max-width: 500px; margin: 0 auto; padding: 20px; }}
                .header {{ text-align: center; margin-bottom: 30px; }}
                .logo {{ font-size: 28px; font-weight: bold; color: #4A90E2; }}
                .content {{ background: #f8f9fa; padding: 30px; border-radius: 10px; }}
                .otp-section {{ text-align: center; margin: 30px 0; }}
                .otp-code {{ font-size: 36px; letter-spacing: 5px; font-weight: bold; color: #4A90E2; font-family: 'Courier New', monospace; }}
                .message {{ color: #555; line-height: 1.6; }}
                .footer {{ text-align: center; color: #999; font-size: 12px; margin-top: 30px; }}
                .expiry {{ color: #e74c3c; font-weight: bold; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <div class="logo">SUBHLABH</div>
                </div>
                <div class="content">
                    <p class="message">Hello,</p>
                    <p class="message">Your verification code for Subhlabh is:</p>
                    <div class="otp-section">
                        <div class="otp-code">{otp_code}</div>
                    </div>
                    <p class="message">This code will expire in <span class="expiry">5 minutes</span>.</p>
                    <p class="message">If you didn't request this code, please ignore this email.</p>
                    <p class="message">Never share your OTP with anyone.</p>
                </div>
                <div class="footer">
                    <p>&copy; 2024 Subhlabh. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        try:
            email_msg = EmailMessage(
                subject=subject,
                body=html_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[email]
            )
            email_msg.content_subtype = 'html'
            email_msg.send(fail_silently=False)
            
            # Log the email
            EmailLog.objects.create(
                email=email,
                subject=subject,
                purpose=purpose,
                is_sent=True
            )
            return True, 'OTP sent successfully'
        except Exception as e:
            # Log the error
            EmailLog.objects.create(
                email=email,
                subject=subject,
                purpose=purpose,
                is_sent=False,
                error_message=str(e)
            )
            return False, f'Error sending email: {str(e)}'


class SignupView(View):
    """Handle user signup with email"""
    
    def get(self, request):
        form = SignupForm()
        return render(request, 'customers/signup.html', {'form': form})
    
    def post(self, request):
        email = request.POST.get('email', '').lower()
        full_name = request.POST.get('full_name', '')
        
        # Manual validation
        errors = []
        if not email:
            errors.append('Email is required.')
        if not full_name:
            errors.append('Full Name is required.')
            
        if errors:
            for error in errors:
                messages.error(request, error)
            form = SignupForm()
            context = {'form': form, 'email_value': email, 'full_name_value': full_name}
            return render(request, 'customers/signup.html', context)

        # Check if user already exists
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Account with this email already exists. Please login.')
            return redirect('customers:login')

        # Create OTP
        otp_obj = OTPVerification.create_otp(
            email=email,
            purpose='signup',
            otp_expiry_time=settings.OTP_EXPIRY_TIME
        )
        
        # Send OTP email
        success, message = EmailService.send_otp_email(
            email=email,
            otp_code=otp_obj.otp_code,
            purpose='signup'
        )
        
        if success:
            request.session['signup_email'] = email
            # Store full name in session to use during account creation
            request.session['signup_full_name'] = full_name
            messages.success(request, f'OTP sent to {email}')
            return redirect('customers:verify-otp-signup')
        else:
            messages.error(request, message)
            context = {'form': SignupForm(), 'email_value': email, 'full_name_value': full_name}
            return render(request, 'customers/signup.html', context)


class VerifyOTPSignupView(View):
    """Verify OTP during signup"""
    
    def get(self, request):
        email = request.session.get('signup_email')
        if not email:
            return redirect('customers:signup')
        
        form = OTPVerificationForm()
        context = {'form': form, 'email': email}
        return render(request, 'customers/verify-otp.html', context)
    
    def post(self, request):
        email = request.session.get('signup_email')
        if not email:
            messages.error(request, 'Invalid session. Please signup again.')
            return redirect('customers:signup')
        
        # Manual validation
        otp_code = request.POST.get('otp', '').strip()
        
        if not otp_code:
            messages.error(request, 'Please enter OTP.')
            context = {'form': OTPVerificationForm(), 'email': email}
            return render(request, 'customers/verify-otp.html', context)
            
        try:
            otp_obj = OTPVerification.objects.get(
                email=email,
                purpose='signup',
                is_verified=False
            )
            
            if otp_obj.is_expired():
                messages.error(request, 'OTP has expired. Please request a new one.')
                return redirect('customers:signup')
            
            if not otp_obj.is_valid():
                messages.error(request, 'Too many failed attempts. Please request a new OTP.')
                return redirect('customers:signup')
            
            if otp_obj.otp_code == otp_code:
                otp_obj.is_verified = True
                otp_obj.save()
                request.session['verified_email'] = email
                request.session['otp_purpose'] = 'signup'
                messages.success(request, 'Email verified successfully!')
                return redirect('customers:create-password')
            else:
                otp_obj.increment_attempts()
                remaining = otp_obj.max_attempts - otp_obj.attempt_count
                messages.error(request, f'Invalid OTP. {remaining} attempts remaining.')
        
        except OTPVerification.DoesNotExist:
            messages.error(request, 'No OTP found. Please request a new one.')
            return redirect('customers:signup')
    
        context = {'form': OTPVerificationForm(), 'email': email, 'otp_value': otp_code}
        return render(request, 'customers/verify-otp.html', context)


class CreatePasswordView(View):
    """Create password after email verification during signup"""
    
    def get(self, request):
        email = request.session.get('verified_email')
        if not email:
            messages.error(request, 'Please verify your email first.')
            return redirect('customers:signup')
        
        form = CreatePasswordForm()
        context = {'form': form, 'email': email}
        return render(request, 'customers/create-password.html', context)
    
    def post(self, request):
        email = request.session.get('verified_email')
        
        if not email:
            messages.error(request, 'Please verify your email first.')
            return redirect('customers:signup')
        
        # Get form data - support both password1/password2 (Django form) and password/confirm_password (manual)
        password = request.POST.get('password1') or request.POST.get('password')
        confirm_password = request.POST.get('password2') or request.POST.get('confirm_password')
        
        # Manual validation
        errors = []
        if not password:
            errors.append('Password is required.')
        if not confirm_password:
            errors.append('Confirm password is required.')
        if password and confirm_password and password != confirm_password:
            errors.append('Passwords do not match.')
        if password and len(password) < 8:
            errors.append('Password must be at least 8 characters long.')
        
        if errors:
            for error in errors:
                messages.error(request, error)
            form = CreatePasswordForm()
            context = {
                'form': form, 
                'email': email,
                'password_value': password,
                'confirm_password_value': confirm_password,
                'first_name_value': request.POST.get('first_name', ''),
                'last_name_value': request.POST.get('last_name', '')
            }
            return render(request, 'customers/create-password.html', context)
        
        try:
            # Create username from email
            username = email.split('@')[0]
            # Make username unique if exists
            base_username = username
            counter = 1
            while User.objects.filter(username=username).exists():
                username = f"{base_username}{counter}"
                counter += 1
            
            # Create user
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=request.POST.get('first_name', request.session.get('signup_full_name', '')),
                last_name=request.POST.get('last_name', ''),
                is_verified=True
            )
            
            # Clean up session
            if 'signup_email' in request.session:
                del request.session['signup_email']
            if 'verified_email' in request.session:
                del request.session['verified_email']
            if 'signup_full_name' in request.session:
                del request.session['signup_full_name']
            if 'otp_purpose' in request.session:
                del request.session['otp_purpose']
            
            messages.success(request, 'Account created successfully! You can now login.')
            return redirect('customers:login')
        
        except Exception as e:
            messages.error(request, f'Error creating account: {str(e)}')
            form = CreatePasswordForm()
            context = {
                'form': form, 
                'email': email,
                'password_value': password,
                'confirm_password_value': confirm_password,
                'first_name_value': request.POST.get('first_name', ''),
                'last_name_value': request.POST.get('last_name', '')
            }
            return render(request, 'customers/create-password.html', context)


class LoginView(View):
    """Handle user login with email and password"""
    
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('customers:dashboard')
        form = LoginForm()
        return render(request, 'customers/login.html', {'form': form})
    
    def post(self, request):
        email = request.POST.get('email', '').lower()
        password = request.POST.get('password', '')
        
        if not email or not password:
            messages.error(request, 'Please enter both email and password.')
            context = {'form': LoginForm(), 'email_value': email}
            return render(request, 'customers/login.html', context)
            
        # Authenticate user with Django's authenticate function
        authenticated_user = authenticate(request, email=email, password=password)
        
        if authenticated_user is not None:
            # Check if user is verified
            if not authenticated_user.is_verified:
                messages.error(request, 'Your account is not verified. Please verify your email.')
                request.session['login_email'] = email
                return redirect('customers:verify-otp-login')
            
            # Login successful
            login(request, authenticated_user)
            
            # Check for account recovery
            if getattr(authenticated_user, 'is_pending_deletion', False):
                authenticated_user.is_pending_deletion = False
                authenticated_user.deletion_requested_at = None
                authenticated_user.save(update_fields=['is_pending_deletion', 'deletion_requested_at'])
                messages.success(request, f'Welcome back! Your account deletion request has been cancelled.')
            else:
                messages.success(request, f'Welcome back, {authenticated_user.first_name or authenticated_user.email}!')
            
            authenticated_user.last_login_at = timezone.now()
            authenticated_user.save(update_fields=['last_login_at'])
            
            return redirect('customers:dashboard')
        else:
            # Invalid email or password
            messages.error(request, 'Invalid email or password.')
            context = {'form': LoginForm(), 'email_value': email}
            return render(request, 'customers/login.html', context)


class VerifyOTPLoginView(View):
    """Verify OTP during login"""
    
    def get(self, request):
        email = request.session.get('login_email')
        if not email:
            return redirect('customers:login')
        
        form = OTPVerificationForm()
        context = {'form': form, 'email': email, 'purpose': 'login'}
        return render(request, 'customers/verify-otp.html', context)
    
    def post(self, request):
        email = request.session.get('login_email')
        if not email:
            messages.error(request, 'Invalid session. Please login again.')
            return redirect('customers:login')
        
        otp_code = request.POST.get('otp', '').strip()
        
        if not otp_code:
            messages.error(request, 'Please enter OTP.')
            context = {'form': OTPVerificationForm(), 'email': email, 'purpose': 'login'}
            return render(request, 'customers/verify-otp.html', context)
            
        try:
            otp_obj = OTPVerification.objects.get(
                email=email,
                purpose='login',
                is_verified=False
            )
            
            if otp_obj.is_expired():
                messages.error(request, 'OTP has expired. Please request a new one.')
                return redirect('customers:login')
            
            if not otp_obj.is_valid():
                messages.error(request, 'Too many failed attempts. Please request a new OTP.')
                return redirect('customers:login')
            
            if otp_obj.otp_code == otp_code:
                otp_obj.is_verified = True
                otp_obj.save()
                
                # Authenticate and login user
                user = User.objects.get(email=email)
                login(request, user)
                user.last_login_at = timezone.now()
                user.save(update_fields=['last_login_at'])
                
                # Clean up session
                if 'login_email' in request.session:
                    del request.session['login_email']
                
                messages.success(request, f'Welcome back, {user.first_name or user.email}!')
                return redirect('customers:dashboard')
            else:
                otp_obj.increment_attempts()
                remaining = otp_obj.max_attempts - otp_obj.attempt_count
                messages.error(request, f'Invalid OTP. {remaining} attempts remaining.')
        
        except OTPVerification.DoesNotExist:
            messages.error(request, 'No OTP found. Please request a new one.')
            return redirect('customers:login')
    
        context = {'form': OTPVerificationForm(), 'email': email, 'purpose': 'login', 'otp_value': otp_code}
        return render(request, 'customers/verify-otp.html', context)


class PasswordResetView(View):
    """Initiate password reset"""
    
    def get(self, request):
        form = PasswordResetForm()
        return render(request, 'customers/forgot-password.html', {'form': form})
    
    def post(self, request):
        email = request.POST.get('email', '').lower()
        
        if not email:
            messages.error(request, 'Please enter your email address.')
            context = {'form': PasswordResetForm(), 'email_value': email}
            return render(request, 'customers/forgot-password.html', context)
            
        # Check if user exists
        if not User.objects.filter(email=email).exists():
            messages.error(request, 'No account found with this email address.')
            context = {'form': PasswordResetForm(), 'email_value': email}
            return render(request, 'customers/forgot-password.html', context)
        
        # Create OTP for password reset
        otp_obj = OTPVerification.create_otp(
            email=email,
            purpose='reset',
            otp_expiry_time=settings.OTP_EXPIRY_TIME
        )
        
        # Send OTP email
        success, message = EmailService.send_otp_email(
            email=email,
            otp_code=otp_obj.otp_code,
            purpose='reset'
        )
        
        if success:
            request.session['reset_email'] = email
            messages.success(request, f'OTP sent to {email}')
            return redirect('customers:verify-otp-reset')
        else:
            messages.error(request, message)
            context = {'form': PasswordResetForm(), 'email_value': email}
            return render(request, 'customers/forgot-password.html', context)


class VerifyOTPResetView(View):
    """Verify OTP during password reset"""
    
    def get(self, request):
        email = request.session.get('reset_email')
        if not email:
            return redirect('customers:forgot-password')
        
        form = OTPVerificationForm()
        context = {'form': form, 'email': email, 'purpose': 'reset'}
        return render(request, 'customers/verify-otp.html', context)
    
    def post(self, request):
        email = request.session.get('reset_email')
        if not email:
            messages.error(request, 'Invalid session. Please start over.')
            return redirect('customers:forgot-password')
        
        # Manual validation
        otp_code = request.POST.get('otp', '').strip()
        
        if not otp_code:
            messages.error(request, 'Please enter OTP.')
            context = {'form': OTPVerificationForm(), 'email': email, 'purpose': 'reset'}
            return render(request, 'customers/verify-otp.html', context)
            
        try:
            otp_obj = OTPVerification.objects.get(
                email=email,
                purpose='reset',
                is_verified=False
            )
            
            if otp_obj.is_expired():
                messages.error(request, 'OTP has expired. Please request a new one.')
                return redirect('customers:forgot-password')
            
            if not otp_obj.is_valid():
                messages.error(request, 'Too many failed attempts. Please request a new OTP.')
                return redirect('customers:forgot-password')
            
            if otp_obj.otp_code == otp_code:
                otp_obj.is_verified = True
                otp_obj.save()
                request.session['verified_reset_email'] = email
                messages.success(request, 'Email verified! Please set your new password.')
                return redirect('customers:set-new-password')
            else:
                otp_obj.increment_attempts()
                remaining = otp_obj.max_attempts - otp_obj.attempt_count
                messages.error(request, f'Invalid OTP. {remaining} attempts remaining.')
        
        except OTPVerification.DoesNotExist:
            messages.error(request, 'No OTP found. Please request a new one.')
            return redirect('customers:forgot-password')
    
        context = {'form': OTPVerificationForm(), 'email': email, 'purpose': 'reset', 'otp_value': otp_code}
        return render(request, 'customers/verify-otp.html', context)


class SetNewPasswordView(View):
    """Set new password after OTP verification during password reset"""
    
    def get(self, request):
        email = request.session.get('verified_reset_email')
        if not email:
            messages.error(request, 'Please verify your email first.')
            return redirect('customers:forgot-password')
        
        form = SetNewPasswordForm()
        context = {'form': form, 'email': email}
        return render(request, 'customers/set-new-password.html', context)
    
    def post(self, request):
        email = request.session.get('verified_reset_email')
        if not email:
            messages.error(request, 'Please verify your email first.')
            return redirect('customers:forgot-password')
        
        # Get form data - support both password1/password2 (Django form) and password/confirm_password (manual)
        password = request.POST.get('new_password1') or request.POST.get('password')
        confirm_password = request.POST.get('new_password2') or request.POST.get('confirm_password')
        
        # Manual validation
        errors = []
        if not password:
            errors.append('Password is required.')
        if not confirm_password:
            errors.append('Confirm password is required.')
        if password and confirm_password and password != confirm_password:
            errors.append('Passwords do not match.')
        if password and len(password) < 8:
            errors.append('Password must be at least 8 characters long.')
        
        if errors:
            for error in errors:
                messages.error(request, error)
            form = SetNewPasswordForm()
            context = {
                'form': form, 
                'email': email,
                'password_value': password,
                'confirm_password_value': confirm_password
            }
            return render(request, 'customers/set-new-password.html', context)
            
        try:
            user = User.objects.get(email=email)
            user.set_password(password)
            user.save()
            
            # Clean up session
            if 'reset_email' in request.session:
                del request.session['reset_email']
            if 'verified_reset_email' in request.session:
                del request.session['verified_reset_email']
            
            messages.success(request, 'Password updated successfully! Please login with your new password.')
            return redirect('customers:login')
        
        except User.DoesNotExist:
            messages.error(request, 'User not found.')
        except Exception as e:
            messages.error(request, f'Error updating password: {str(e)}')
        
        form = SetNewPasswordForm()
        context = {
            'form': form, 
            'email': email,
            'password_value': password,
            'confirm_password_value': confirm_password
        }
        return render(request, 'customers/set-new-password.html', context)


class ResendOTPView(View):
    """Resend OTP"""
    
    def post(self, request):
        email = request.POST.get('email')
        purpose = request.POST.get('purpose', 'signup')
        
        if not email:
            return JsonResponse({'success': False, 'message': 'Email not provided'})
        
        try:
            # Get the latest OTP for this email and purpose
            otp_obj = OTPVerification.objects.filter(
                email=email,
                purpose=purpose
            ).latest('created_at')
            
            # Check if OTP is still valid (not verified)
            if otp_obj.is_verified:
                return JsonResponse({'success': False, 'message': 'OTP already used'})
            
            # Resend the OTP
            success, message = EmailService.send_otp_email(
                email=email,
                otp_code=otp_obj.otp_code,
                purpose=purpose
            )
            
            if success:
                # Reset attempts
                otp_obj.attempt_count = 0
                otp_obj.expires_at = timezone.now() + timedelta(seconds=settings.OTP_EXPIRY_TIME)
                otp_obj.save()
                
                return JsonResponse({
                    'success': True,
                    'message': f'OTP resent to {email}',
                    'expires_at': otp_obj.expires_at.timestamp()
                })
            else:
                return JsonResponse({'success': False, 'message': message})
        
        except OTPVerification.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'No OTP found'})


class LogoutView(View):
    """Handle user logout"""
    
    def get(self, request):
        logout(request)
        messages.success(request, 'You have been logged out.')
        return redirect('customers:login')
    
    def post(self, request):
        logout(request)
        messages.success(request, 'You have been logged out.')
        return redirect('customers:login')






# Business logic views are imported from app_views.py to avoid duplication


# Import business logic views
from .app_views import (
    DashboardView, ProfileView, ChangePasswordView, SettingsView,
    UpdateNotificationsView, DeleteAccountConfirmView, RequestAccountDeletionView, CancelAccountDeletionView,
    BrandingView,
    CustomerListView, CustomerCreateView, CustomerDetailView, CustomerEditView, CustomerDeleteView,
    UdharPaymentView,
    ProductListView, ProductCreateView, ProductDetailView, ProductDataView, ProductEditView, ProductDeleteView,
    ProductImportView, ProductExportView, ProductTemplateView,
    BillingView, SalesHistoryView, SaleDetailView, SaleDeleteView, SalePrintView,
    ReportsView,
    ProfileEditView,
    ProductSearchAPI, CustomerSearchAPI,
    OfferListView, OfferCreateView, OfferEditView, OfferDeleteView,
    TermsOfServiceView, PrivacyPolicyView
)
