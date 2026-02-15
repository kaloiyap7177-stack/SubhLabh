from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.cache import cache
from customers.models import Customer, Product, Sale, SaleItem, Offer, UserProfile, OTPVerification
from decimal import Decimal
import json
import time

User = get_user_model()

class CoreFlowsTest(TestCase):
    def setUp(self):
        # Create User
        self.user = User.objects.create_user(
            username='testuser', 
            email='test@example.com', 
            password='password123',
            is_verified=True
        )
        self.client = Client()
        self.client.login(email='test@example.com', password='password123')
        
        # Create Profile
        UserProfile.objects.create(user=self.user, shop_name="Test Shop")
        
        # Create Customer
        self.customer = Customer.objects.create(
            user=self.user,
            name="Test Customer",
            phone="9876543210"
        )
        
        # Create Product (Stock 10)
        self.product = Product.objects.create(
            user=self.user,
            name="Test Product",
            category="grocery",
            price=Decimal("100.00"),
            stock_quantity=Decimal("10.00"),
            product_type="product"
        )
        
        # Create Service
        self.service = Product.objects.create(
            user=self.user,
            name="Test Service",
            price=Decimal("500.00"),
            product_type="service"
        )

    def test_dashboard_stats_and_cache(self):
        """Test that dashboard loads key metrics and updates them after a sale (checking cache invalidation)"""
        
        # 1. Initial Load
        response = self.client.get('/dashboard/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['total_customers'], 1)
        self.assertEqual(response.context['today_sales'], Decimal('0'))
        
        # 2. Make a Sale
        sale = Sale.objects.create(
            user=self.user,
            customer=self.customer,
            total_amount=Decimal("100.00"),
            payment_method="cash",
            is_paid=True
        )
        SaleItem.objects.create(
            sale=sale,
            product=self.product,
            quantity=Decimal("1.00"),
            price_at_sale=Decimal("100.00")
        )
        
        # 3. Check Dashboard Agains (Is Cache Invalidated?)
        # If the view caches for 5 mins and doesn't invalidate on sale, this will fail/show old data
        response = self.client.get('/dashboard/')
        self.assertEqual(response.status_code, 200)
        
        # This assertion checks if the cache was properly invalidated/updated
        # If it returns 0, it means we have a stale cache bug
        self.assertEqual(response.context['today_sales'], Decimal("100.00"), "Dashboard showing stale data after sale!")

    def test_billing_logic_stock_updates(self):
        """Test billing flow ensuring stock is reduced correctly"""
        
        # 1. Sell 2 items
        data = {
            'customer_id': self.customer.id,
            'payment_method': 'cash',
            'items': [
                {'product_id': self.product.id, 'quantity': 2, 'price': 100}
            ]
        }
        
        response = self.client.post(
            '/billing/', 
            json.dumps(data), 
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['success'])
        
        # Verify Stock (10 - 2 = 8)
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock_quantity, Decimal("8.00"))
        
        # 2. Sell Service (Should not affect stock)
        data_service = {
            'items': [
                {'product_id': self.service.id, 'quantity': 1, 'price': 500}
            ]
        }
        response = self.client.post(
            '/billing/', 
            json.dumps(data_service), 
            content_type='application/json'
        )
        self.assertTrue(response.json()['success'])
        
    def test_billing_insufficient_stock(self):
        """Test that selling more than available stock fails"""
        
        # Try to sell 15 (Stock is 10)
        data = {
            'items': [
                {'product_id': self.product.id, 'quantity': 15, 'price': 100}
            ]
        }
        
        response = self.client.post(
            '/billing/', 
            json.dumps(data), 
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        resp_json = response.json()
        self.assertFalse(resp_json['success'])
        self.assertIn('Insufficient stock', resp_json['message'])

    def test_credit_transaction(self):
        """Test credit sale logic"""
        
        initial_credit = self.customer.credit_amount
        
        data = {
            'customer_id': self.customer.id,
            'payment_method': 'cash',
            'is_paid': False,  # Udhar
            'items': [
                {'product_id': self.product.id, 'quantity': 1, 'price': 100}
            ]
        }
        
        response = self.client.post(
            '/billing/', 
            json.dumps(data), 
            content_type='application/json'
        )
        self.assertTrue(response.json()['success'])
        
        # Verify Customer Udhar Increased
        self.customer.refresh_from_db()
        self.assertEqual(self.customer.credit_amount, initial_credit + Decimal("100.00"))
        
        # Verify Sale marked as not paid
        sale_id = response.json()['sale_id']
        sale = Sale.objects.get(pk=sale_id)
        self.assertFalse(sale.is_paid)
        self.assertTrue(sale.added_to_credit)

    def test_report_aggregations(self):
        """Test if reports are calculating totals correctly"""
        
        # Create sales directly
        today = timezone.now()
        
        # Sale 1: 500
        s1 = Sale.objects.create(user=self.user, total_amount=Decimal("500.00"), payment_method="cash", sale_date=today)
        SaleItem.objects.create(sale=s1, product=self.product, quantity=1, price_at_sale=500)
        
        # Sale 2: 300
        s2 = Sale.objects.create(user=self.user, total_amount=Decimal("300.00"), payment_method="upi", sale_date=today)
        SaleItem.objects.create(sale=s2, product=self.product, quantity=1, price_at_sale=300)
        
        response = self.client.get('/reports/')
        self.assertEqual(response.status_code, 200)
        
        # Check Today's Sales
        self.assertEqual(response.context['today_sales'], Decimal("800.00"))
