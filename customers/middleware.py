"""Activity tracking middleware for monitoring user sessions"""
from django.utils import timezone
from datetime import datetime, timedelta


class ActivityTrackingMiddleware:
    """
    Middleware to track user activity time.
    
    Tracks how long authenticated users are active on the site by:
    - Recording session start times
    - Calculating time between requests
    - Updating UserActivity model with daily totals
    """
    
    # Consider user inactive after 5 minutes of no requests
    INACTIVE_THRESHOLD = 300  # seconds
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Process request before view
        if request.user.is_authenticated:
            self.track_activity(request)
        
        response = self.get_response(request)
        return response
    
    def track_activity(self, request):
        """Track user activity and update UserActivity model"""
        from customers.models import UserActivity
        
        user = request.user
        now = timezone.now()
        today = now.date()
        
        # Get or create today's activity record
        activity, created = UserActivity.objects.get_or_create(
            user=user,
            date=today,
            defaults={'login_count': 1}
        )
        
        # Get last activity time from session
        last_activity_str = request.session.get('last_activity')
        
        if last_activity_str:
            try:
                # Parse the stored timestamp
                last_activity = datetime.fromisoformat(last_activity_str)
                
                # Make it timezone-aware if it isn't
                if timezone.is_naive(last_activity):
                    last_activity = timezone.make_aware(last_activity)
                
                # Calculate time since last activity
                time_diff = (now - last_activity).total_seconds()
                
                # Only count if within inactive threshold
                if time_diff <= self.INACTIVE_THRESHOLD:
                    activity.total_active_seconds += int(time_diff)
                    activity.save(update_fields=['total_active_seconds', 'last_activity'])
            except (ValueError, TypeError):
                # If parsing fails, just update last activity
                pass
        else:
            # First activity of the session, increment login count
            if not created:
                activity.login_count += 1
                activity.save(update_fields=['login_count', 'last_activity'])
        
        # Update last activity time in session
        request.session['last_activity'] = now.isoformat()
