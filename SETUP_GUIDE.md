# Subhlabh - Quick Setup Guide

## ✅ What's Already Done

1. **Virtual Environment** - Created and activated
2. **Django Installation** - Django 5.2.7 installed
3. **Project Structure** - Complete Django project setup
4. **Database** - SQLite configured and migrated
5. **Email Configuration** - Gmail SMTP configured
6. **All Models** - CustomUser, OTPVerification, EmailLog created
7. **All Views** - 12 complete authentication views
8. **All Templates** - 7 HTML templates with responsive design
9. **All Styling** - 828 lines of CSS with 3D effects
10. **All JavaScript** - 524 lines of interactive JS

## 🚀 Quick Start

### 1. Activate Virtual Environment
```bash
env\Scripts\activate  # On Windows PowerShell
```

### 2. Start Development Server
```bash
python manage.py runserver
```

Server will run at: `http://127.0.0.1:8000/`

### 3. Access the Application
- **Signup:** http://127.0.0.1:8000/signup/
- **Login:** http://127.0.0.1:8000/login/
- **Dashboard:** http://127.0.0.1:8000/dashboard/ (after login)
- **Admin:** http://127.0.0.1:8000/admin/

## 📧 Email Testing

The system uses Gmail SMTP with:
- **Email:** subhlabh059@gmail.com
- **App Password:** your_app_password_here

OTP emails will be sent automatically when users sign up or login.

## 🔑 Admin Access

To create a superuser for admin access:
```bash
python manage.py createsuperuser
# Follow prompts to create admin account
```

Then access admin at: http://127.0.0.1:8000/admin/

## 📋 User Workflow

### Sign Up
1. Visit `/signup/`
2. Enter email
3. Receive OTP via email
4. Verify OTP
5. Create password
6. Account created ✓

### Login
1. Visit `/login/`
2. Enter email
3. Receive OTP via email
4. Verify OTP
5. Logged in ✓

### Password Reset
1. Visit `/forgot-password/`
2. Enter registered email
3. Verify OTP
4. Set new password
5. Ready to login ✓

## 🎨 Features Showcase

### UI/UX
- Animated 3D cards with shadow effects
- Smooth fade-in and slide animations
- Real-time form validation
- Loading button states
- Responsive mobile design
- Color-coded alert messages

### Security
- 6-digit OTP verification
- 5-minute OTP expiry
- Maximum 5 failed attempts
- CSRF protection
- Secure password hashing
- Session management

### Backend
- Email logging
- OTP attempt tracking
- Custom user model
- Django admin integration
- Comprehensive error handling

## 📁 Key Files

| File | Purpose |
|------|---------|
| `subhlabh/settings.py` | Configuration, email setup |
| `customers/models.py` | Data models (107 lines) |
| `customers/views.py` | Authentication logic (572 lines) |
| `customers/forms.py` | Form validation (187 lines) |
| `templates/customers/*.html` | 7 HTML templates |
| `static/css/style.css` | Styling (828 lines) |
| `static/js/main.js` | Interactivity (524 lines) |

## 🔧 Configuration

### Email Settings (settings.py)
```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'subhlabh059@gmail.com'
EMAIL_HOST_PASSWORD = 'your_app_password_here'
```

### OTP Settings (settings.py)
```python
OTP_EXPIRY_TIME = 300  # 5 minutes
OTP_LENGTH = 6         # 6 digits
```

## 📊 Database Models

### CustomUser
- Email-based authentication
- Verification status tracking
- Phone number storage
- Login timestamp tracking

### OTPVerification
- 6-digit OTP storage
- Purpose tracking (signup/login/reset)
- Automatic expiry
- Attempt counting

### EmailLog
- Email send/failure tracking
- Audit trail
- Error message storage

## 🎯 API Endpoints

| Method | URL | Purpose |
|--------|-----|---------|
| GET | `/signup/` | Signup form |
| POST | `/signup/` | Process signup |
| GET | `/login/` | Login form |
| POST | `/login/` | Process login |
| POST | `/verify-otp/signup/` | Verify signup OTP |
| POST | `/verify-otp/login/` | Verify login OTP |
| POST | `/resend-otp/` | AJAX resend OTP |
| GET | `/dashboard/` | User dashboard |
| GET | `/logout/` | User logout |

## 🐛 Troubleshooting

### Server won't start?
```bash
# Check if port 8000 is in use
netstat -ano | findstr :8000

# Run on different port
python manage.py runserver 8001
```

### OTP not sending?
```bash
# Check email log in admin
# Verify Gmail account allows less secure apps
# Check if internet connection is working
```

### Static files not loading?
```bash
python manage.py collectstatic
```

### Database errors?
```bash
python manage.py migrate
```

## 💡 Development Tips

1. **Use Django Shell** for testing:
   ```bash
   python manage.py shell
   ```

2. **View Logs** for debugging:
   - Check Django admin > Email Logs
   - Check OTP Verification for attempt tracking

3. **Test Email** functionality:
   ```python
   from customers.models import OTPVerification
   otp = OTPVerification.create_otp('test@example.com')
   print(otp.otp_code)
   ```

4. **Live Reload** - Django auto-reloads on file changes

## 📱 Browser Compatibility

- Chrome/Chromium ✓
- Firefox ✓
- Safari ✓
- Edge ✓
- Mobile browsers ✓

## 🎨 Customization

### Change Colors
Edit `static/css/style.css` CSS variables:
```css
:root {
    --primary: #4A90E2;
    --secondary: #667eea;
    --accent: #764ba2;
    /* ... more colors */
}
```

### Change Email Template
Edit `customers/views.py` `EmailService.send_otp_email()` method

### Change OTP Length
In `settings.py`:
```python
OTP_LENGTH = 8  # Change from 6 to 8
```

## 📚 Documentation

- Django Docs: https://docs.djangoproject.com/
- Forms: https://docs.djangoproject.com/en/5.2/topics/forms/
- Auth: https://docs.djangoproject.com/en/5.2/topics/auth/
- Email: https://docs.djangoproject.com/en/5.2/topics/email/
- Models: https://docs.djangoproject.com/en/5.2/topics/db/models/

## ✨ Next Steps

1. **Test signup/login** with your email
2. **Explore admin interface** at `/admin/`
3. **Customize colors/branding** as needed
4. **Deploy to production** when ready
5. **Implement OAuth** for Google login
6. **Add customer management** features

## 📞 Need Help?

- Check README.md for detailed documentation
- Review code comments for specific logic
- Check Django official documentation
- Test in Django shell for debugging

---

**Status:** ✅ Ready for Use  
**Last Updated:** October 24, 2025  
**Maintenance:** Actively Maintained
