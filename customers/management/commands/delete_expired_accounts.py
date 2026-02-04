from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth import get_user_model
from datetime import timedelta
from customers.models import UserProfile, Customer, Product, Sale, Offer, EmailLog

User = get_user_model()

class Command(BaseCommand):
    help = 'Permanently delete accounts that have been pending deletion for more than 30 days'

    def handle(self, *args, **options):
        # Calculate the threshold date (30 days ago)
        threshold_date = timezone.now() - timedelta(days=30)
        
        # Find users pending deletion older than 30 days
        users_to_delete = User.objects.filter(
            is_pending_deletion=True,
            deletion_requested_at__lte=threshold_date
        )
        
        count = users_to_delete.count()
        
        if count == 0:
            self.stdout.write(self.style.SUCCESS('No expired accounts found to delete.'))
            return
            
        self.stdout.write(self.style.WARNING(f'Found {count} accounts eligible for deletion.'))
        
        for user in users_to_delete:
            try:
                # Log the deletion
                self.stdout.write(f'Deleting user: {user.email} (Requested: {user.deletion_requested_at})')
                
                # Delete related data explicitly if needed (Django cascade usually handles this)
                # Note: Django's on_delete=models.CASCADE in models ensures related data is deleted
                # We are relying on that for Sales, Customers, Products, etc.
                
                # Delete the user
                user.delete()
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error deleting user {user.email}: {str(e)}'))
        
        self.stdout.write(self.style.SUCCESS(f'Successfully deleted {count} expired accounts.'))
