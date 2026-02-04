# SUBHLABH - Modern OTP-Based Authentication System

A full-featured Django authentication system with animated 3D UI, email-based OTP verification, and complete user management.

## 🎨 Features

### Authentication Features
- ✅ **Email-Based Authentication** - Sign up and login with email only
- ✅ **OTP Verification** - 6-digit OTP sent via email (Gmail SMTP)
- ✅ **OTP Expiry** - OTP expires after 5 minutes
- ✅ **Resend OTP** - With countdown timer and attempt tracking
- ✅ **Password Reset** - Full password recovery workflow
- ✅ **OTP Attempt Limiting** - Max 5 failed attempts per OTP
- ✅ **Session Management** - 30-day session persistence
- ✅ **Email Logging** - Track all email sends and failures

### UI/UX Features
- ✅ **3D Effects** - Modern 3D card and shadow effects
- ✅ **Smooth Animations** - Fade-in, scale, slide transitions
- ✅ **Fully Responsive** - Works on desktop, tablet, and mobile
- ✅ **Real-time Validation** - Email format and password strength checking
- ✅ **Loading States** - Animated button loaders
- ✅ **Error Handling** - Inline error messages with animations
- ✅ **Password Requirements** - Visual requirement checker
- ✅ **Color-coded Alerts** - Success, error, and warning messages

### Backend Features
- ✅ **Custom User Model** - Email-based user model with verification flag
- ✅ **Django Forms** - Comprehensive form validation
- ✅ **Email Service** - Robust Gmail SMTP integration
- ✅ **Database Models** - CustomUser, OTPVerification, EmailLog
- ✅ **Admin Interface** - Complete Django admin integration
- ✅ **Error Handling** - Graceful error messages and logging

## 📁 Project Structure

```
SubhLabh/
├── env/                           # Python virtual environment
├── manage.py                      # Django management script
├── db.sqlite3                     # SQLite database
│
├── subhlabh/                      # Project configuration
│   ├── settings.py                # Email, OTP, and app settings
│   ├── urls.py                    # Main URL routing
│   ├── wsgi.py                    # WSGI application
│   ├── asgi.py                    # ASGI application
│   └── __init__.py
│
├── customers/                     # Authentication app
│   ├── models.py                  # CustomUser, OTPVerification, EmailLog
│   ├── views.py                   # Auth views with email logic
│   ├── forms.py                   # Form validation
│   ├── urls.py                    # Auth endpoints
│   ├── admin.py                   # Django admin
│   ├── apps.py
│   ├── migrations/                # Database migrations
│   └── __init__.py
│
├── templates/                     # HTML templates
│   ├── base.html                  # Base template
│   └── customers/
│       ├── signup.html            # Sign up page
│       ├── login.html             # Login page
│       ├── verify-otp.html        # OTP verification page
│       ├── create-password.html   # Password creation page
│       ├── forgot-password.html   # Password reset request
│       ├── set-new-password.html  # New password page
│       └── dashboard.html         # User dashboard
│
└── static/                        # Static files
    ├── css/
    │   └── style.css              # Main stylesheet (828 lines)
    └── js/
        └── main.js                # Main JavaScript (524 lines)
```

## 🚀 Setup Instructions

### 1. Virtual Environment (Already Done)
```bash
# Virtual environment is already created at: env/
# Activate it:
env\Scripts\activate  # On Windows
```

### 2. Install Dependencies (Already Done)
```bash
# Django 5.2.7 is already installed
pip list  # Verify installation
```

### 3. Email Configuration (Already Configured)
Settings are in `subhlabh/settings.py`:
```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'subhlabh059@gmail.com'
EMAIL_HOST_PASSWORD = 'your_app_password_here'
DEFAULT_FROM_EMAIL = 'subhlabh059@gmail.com'
```

### 4. Database (Already Migrated)
```bash
# Migrations already applied
python manage.py migrate
```

### 5. Run Development Server
```bash
python manage.py runserver
# Server runs at http://127.0.0.1:8000/
```

## 🔗 URL Routes

| Route | View | Purpose |
|-------|------|---------|
| `/signup/` | SignupView | User registration |
| `/verify-otp/signup/` | VerifyOTPSignupView | Verify email during signup |
| `/create-password/` | CreatePasswordView | Create password after signup |
| `/login/` | LoginView | User login |
| `/verify-otp/login/` | VerifyOTPLoginView | Verify email during login |
| `/forgot-password/` | PasswordResetView | Initiate password reset |
| `/verify-otp/reset/` | VerifyOTPResetView | Verify email for password reset |
| `/set-new-password/` | SetNewPasswordView | Set new password |
| `/resend-otp/` | ResendOTPView | Resend OTP (AJAX) |
| `/logout/` | LogoutView | User logout |
| `/dashboard/` | DashboardView | User dashboard (protected) |

## 📧 Email Configuration

### Gmail Setup (Already Configured)
1. Use `subhlabh059@gmail.com` as sender
2. App Password: `your_app_password_here`
3. This is configured in `settings.py`

### Testing Email Sending
```bash
# Test email functionality
python manage.py shell
>>> from django.core.mail import send_mail
>>> send_mail('Test', 'This is a test', 'subhlabh059@gmail.com', ['recipient@example.com'])
```

## 🔐 Security Features

- **OTP Validation** - Automatic expiry after 5 minutes
- **Attempt Limiting** - Maximum 5 failed OTP attempts
- **CSRF Protection** - Django CSRF middleware enabled
- **Session Security** - Secure session configuration
- **Password Requirements**:
  - Minimum 8 characters
  - At least 1 uppercase letter
  - At least 1 digit
- **Email Logging** - All email sends/failures logged

## 📱 Responsive Design

- **Desktop (1024px+)** - Full 2-column layout with logo section
- **Tablet (768px-1024px)** - Single column with stacked logo
- **Mobile (< 768px)** - Optimized for small screens

## 🎨 Color Scheme

| Color | Usage | Value |
|-------|-------|-------|
| Primary | Main brand color | #4A90E2 |
| Secondary | Gradient start | #667eea |
| Accent | Gradient end | #764ba2 |
| Success | Positive actions | #2ecc71 |
| Error | Error messages | #e74c3c |
| Warning | Warning alerts | #f39c12 |

## 🛠️ Database Models

### CustomUser
```python
- email (unique)
- first_name, last_name
- is_verified (default: False)
- phone_number (optional)
- created_at, updated_at
- last_login_at (tracks last login)
```

### OTPVerification
```python
- email
- otp_code (6 digits)
- purpose (signup, login, reset)
- is_verified (default: False)
- expires_at (5 minutes from creation)
- attempt_count (max 5)
- created_at
```

### EmailLog
```python
- email
- subject
- purpose (signup, login, reset, resend)
- is_sent
- error_message (if failed)
- created_at
```

## 📝 Usage Examples

### Test Signup
1. Go to `http://127.0.0.1:8000/signup/`
2. Enter email: `test@example.com`
3. Click "Send OTP"
4. Check email for OTP code (sent via Gmail)
5. Enter OTP on verification page
6. Create password
7. Account created ✓

### Test Login
1. Go to `http://127.0.0.1:8000/login/`
2. Enter registered email
3. Click "Send OTP"
4. Verify OTP
5. Logged in ✓

### Test Password Reset
1. Go to `http://127.0.0.1:8000/forgot-password/`
2. Enter registered email
3. Verify OTP
4. Set new password
5. Login with new password ✓

## 🔧 Configuration

### OTP Settings (in `settings.py`)
```python
OTP_EXPIRY_TIME = 300  # 5 minutes in seconds
OTP_LENGTH = 6          # 6-digit OTP
```

### Session Settings (in `settings.py`)
```python
SESSION_COOKIE_AGE = 86400 * 30  # 30 days
SESSION_SAVE_EVERY_REQUEST = True
```

## 📦 Dependencies

- **Django 5.2.7** - Web framework
- **Python 3.13+** - Runtime
- **SQLite3** - Database (included with Python)

## 🐛 Troubleshooting

### OTP Not Sending?
- Check `EmailLog` in Django admin for errors
- Verify Gmail credentials in `settings.py`
- Check SMTP logs for connection issues
- Ensure Less Secure Apps are allowed (Gmail account)

### Migration Errors?
```bash
python manage.py makemigrations customers
python manage.py migrate
```

### Database Issues?
```bash
# Reset database (WARNING: Deletes all data)
rm db.sqlite3
python manage.py migrate
```

### Server Not Starting?
```bash
# Check for port conflicts
netstat -ano | findstr :8000

# Run on different port
python manage.py runserver 8001
```

## 📊 Admin Interface

Access Django admin at: `http://127.0.0.1:8000/admin/`

**Models Available:**
- CustomUser - User management
- OTPVerification - OTP tracking
- EmailLog - Email send history

## 🎯 Features Implemented

- [x] Email-based signup/login
- [x] 6-digit OTP verification
- [x] 5-minute OTP expiry
- [x] Resend OTP with countdown
- [x] Password strength validation
- [x] Password reset workflow
- [x] Session management
- [x] Email logging
- [x] 3D animated UI
- [x] Responsive design
- [x] Form validation
- [x] Error handling
- [x] Dashboard page
- [x] Google login button (UI only)
- [x] Admin interface

## 📄 License

This is a demo project for the Subhlabh Customer Management System.

## 👨‍💻 Developer Notes

- All views use class-based views for better organization
- Email service is abstracted in `EmailService` class
- Forms include comprehensive validation
- OTP validation logic in `OTPVerification` model
- CSS uses CSS variables for easy theming
- JavaScript organized into classes for maintainability

## 🎓 Learning Resources

- Django Forms: https://docs.djangoproject.com/en/5.2/topics/forms/
- Custom User Model: https://docs.djangoproject.com/en/5.2/topics/auth/customizing/#substituting-a-custom-user-model
- Class-Based Views: https://docs.djangoproject.com/en/5.2/topics/class-based-views/
- Email Backend: https://docs.djangoproject.com/en/5.2/topics/email/

## 📞 Support

For issues or questions, check the code comments and Django documentation.

---

**Version:** 1.0.0  
**Last Updated:** October 24, 2025  
**Status:** ✅ Fully Functional
