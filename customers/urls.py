from django.urls import path
from django.shortcuts import redirect
from . import views

app_name = 'customers'

urlpatterns = [
    # Authentication
    path('signup/', views.SignupView.as_view(), name='signup'),
    path('verify-otp/signup/', views.VerifyOTPSignupView.as_view(), name='verify-otp-signup'),
    path('create-password/', views.CreatePasswordView.as_view(), name='create-password'),
    
    path('login/', views.LoginView.as_view(), name='login'),
    path('verify-otp/login/', views.VerifyOTPLoginView.as_view(), name='verify-otp-login'),
    
    path('forgot-password/', views.PasswordResetView.as_view(), name='forgot-password'),
    path('verify-otp/reset/', views.VerifyOTPResetView.as_view(), name='verify-otp-reset'),
    path('set-new-password/', views.SetNewPasswordView.as_view(), name='set-new-password'),
    
    # OTP Operations
    path('resend-otp/', views.ResendOTPView.as_view(), name='resend-otp'),
    
    # User
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('profile/edit/', views.ProfileEditView.as_view(), name='profile-edit'),
    path('change-password/', views.ChangePasswordView.as_view(), name='change-password'),
    path('settings/', views.SettingsView.as_view(), name='settings'),
    path('settings/notifications/', views.UpdateNotificationsView.as_view(), name='update-notifications'),
    path('delete-account/confirm/', views.DeleteAccountConfirmView.as_view(), name='delete-account-confirm'),
    path('delete-account/request/', views.RequestAccountDeletionView.as_view(), name='request-account-deletion'),
    path('cancel-deletion/', views.CancelAccountDeletionView.as_view(), name='cancel-account-deletion'),
    
    # Customers
    path('customers/', views.CustomerListView.as_view(), name='customer-list'),
    path('customers/create/', views.CustomerCreateView.as_view(), name='customer-create'),
    path('customers/<int:pk>/', views.CustomerDetailView.as_view(), name='customer-detail'),
    path('customers/<int:pk>/edit/', views.CustomerEditView.as_view(), name='customer-edit'),
    path('customers/<int:pk>/delete/', views.CustomerDeleteView.as_view(), name='customer-delete'),
    path('customers/<int:pk>/pay-udhar/', views.UdharPaymentView.as_view(), name='udhar-payment'),
    
    # Products
    path('products/', views.ProductListView.as_view(), name='product-list'),
    path('products/create/', views.ProductCreateView.as_view(), name='product-create'),
    path('products/<int:pk>/', views.ProductDetailView.as_view(), name='product-detail'),
    path('products/<int:pk>/data/', views.ProductDataView.as_view(), name='product-data'),
    path('products/<int:pk>/edit/', views.ProductEditView.as_view(), name='product-edit'),
    path('products/<int:pk>/delete/', views.ProductDeleteView.as_view(), name='product-delete'),
    path('products/import/', views.ProductImportView.as_view(), name='product-import'),
    path('products/export/', views.ProductExportView.as_view(), name='product-export'),
    path('products/template/', views.ProductTemplateView.as_view(), name='product-template'),
    # Offers
    path('offers/', views.OfferListView.as_view(), name='offer-list'),
    path('offers/create/', views.OfferCreateView.as_view(), name='offer-create'),
    path('offers/<int:pk>/edit/', views.OfferEditView.as_view(), name='offer-edit'),
    path('offers/<int:pk>/delete/', views.OfferDeleteView.as_view(), name='offer-delete'),
    
    # Sales/Billing
    path('billing/', views.BillingView.as_view(), name='billing'),
    path('sales/', views.SalesHistoryView.as_view(), name='sales-history'),
    path('sales/download/', views.SalesHistoryView.as_view(), name='sales-download'),
    path('sales/<int:pk>/details/', views.SaleDetailView.as_view(), name='sale-detail'),
    path('sales/<int:pk>/delete/', views.SaleDeleteView.as_view(), name='sale-delete'),
    path('sales/<int:pk>/print/', views.SalePrintView.as_view(), name='sale-print'),
    
    # Reports
    path('reports/', views.ReportsView.as_view(), name='reports'),
    
    # API Endpoints
    path('api/products/search/', views.ProductSearchAPI.as_view(), name='api-product-search'),
    path('api/customers/search/', views.CustomerSearchAPI.as_view(), name='api-customer-search'),
    
    # Legal Pages
    path('terms/', views.TermsOfServiceView.as_view(), name='terms_of_service'),
    path('privacy/', views.PrivacyPolicyView.as_view(), name='privacy_policy'),

    # Shop Branding
    path('profile/branding/', views.BrandingView.as_view(), name='branding'),
    
    # Redirect root to dashboard or login
    path('', lambda r: redirect('customers:dashboard') if r.user.is_authenticated else redirect('customers:login'), name='index'),
]
