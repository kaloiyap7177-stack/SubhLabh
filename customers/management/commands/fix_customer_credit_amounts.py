from django.core.management.base import BaseCommand
from customers.models import Customer, Sale
from decimal import Decimal
from django.db.models import Sum

class Command(BaseCommand):
    help = 'Recalculate customer credit amounts based on unpaid sales'

    def handle(self, *args, **options):
        self.stdout.write('Starting customer credit amount recalculation...')
        
        customers_fixed = 0
        total_adjustments = 0
        
        for customer in Customer.objects.all():
            # Calculate the correct credit amount based on unpaid sales
            correct_credit = Sale.objects.filter(
                customer=customer,
                is_paid=False
            ).aggregate(total=Sum('total_amount'))['total'] or Decimal('0')
            
            # If the current credit amount is different from what it should be
            if customer.credit_amount != correct_credit:
                old_amount = customer.credit_amount
                customer.credit_amount = correct_credit
                
                # Ensure non-negative values
                if customer.credit_amount < 0:
                    customer.credit_amount = Decimal('0')
                
                customer.save()
                
                customers_fixed += 1
                
                self.stdout.write(
                    f'Fixed {customer.name}: {old_amount} -> {customer.credit_amount}'
                )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully fixed {customers_fixed} customers.'
            )
        )