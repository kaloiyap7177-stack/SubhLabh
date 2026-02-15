from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.utils import timezone
from customers.models import Customer
from decimal import Decimal
import json

User = get_user_model()

class CustomerModuleTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser_c', 
            email='test_c@example.com', 
            password='password123',
            is_verified=True
        )
        self.client = Client()
        self.client.login(email='test_c@example.com', password='password123')

    def test_customer_creation_dashboard_update(self):
        """Test customer creation and dashboard cache invalidation"""
        # 1. Initial Dashboard Load
        response = self.client.get('/dashboard/')
        self.assertEqual(response.context['total_customers'], 0)
        
        # 2. Create Customer
        response = self.client.post('/customers/create/', {
            'name': 'New Customer',
            'phone': '1234567890',
            'address': 'Test Address',
            'notes': 'Test Note'
        })
        self.assertEqual(response.status_code, 302) # Redirect to list
        
        # 3. Check Dashboard again
        response = self.client.get('/dashboard/')
        # If cache invalidation is missing, this might still show 0 depending on cache duration
        # We want to ensure it shows 1
        self.assertEqual(response.context['total_customers'], 1, "Dashboard not updating after customer creation")

    def test_customer_creation_duplicate(self):
        """Test duplicate phone number check"""
        Customer.objects.create(user=self.user, name="Existing", phone="1234567890")
        
        response = self.client.post('/customers/create/', {
            'name': 'Duplicate',
            'phone': '1234567890'
        })
        
        # Should stay on form and show warning (200 OK with warning, not redirect)
        self.assertEqual(response.status_code, 200)
        # Check for warning message storage (using Django's messages)
        messages = list(response.context['messages'])
        self.assertTrue(any("already exists" in str(m) for m in messages))
        self.assertEqual(Customer.objects.count(), 1)

    def test_credit_payment_validation(self):
        """Test validation for credit payments"""
        customer = Customer.objects.create(
            user=self.user, 
            name="Debtor", 
            phone="999",
            credit_amount=Decimal("500.00")
        )
        url = f'/customers/{customer.id}/pay-credit/'
        
        # 1. Try paying negative amount
        self.client.post(url, {'amount': '-50'})
        customer.refresh_from_db()
        self.assertEqual(customer.credit_amount, Decimal("500.00"))
        
        # 2. Try paying more than outstanding
        self.client.post(url, {'amount': '600'})
        customer.refresh_from_db()
        self.assertEqual(customer.credit_amount, Decimal("500.00"))
        
        # 3. Pay partial valid amount
        self.client.post(url, {'amount': '200'})
        customer.refresh_from_db()
        self.assertEqual(customer.udhar_amount, Decimal("300.00"))

    def test_customer_deletion_dashboard_update(self):
        """Test customer deletion and dashboard logic"""
        customer = Customer.objects.create(user=self.user, name="To Delete", phone="000")
        
        # Verify count is 1
        response = self.client.get('/dashboard/')
        self.assertEqual(response.context['total_customers'], 1)
        
        # Delete
        self.client.post(f'/customers/{customer.id}/delete/')
        
        # Verify count is 0
        response = self.client.get('/dashboard/')
        self.assertEqual(response.context['total_customers'], 0, "Dashboard not updating after deletion")

