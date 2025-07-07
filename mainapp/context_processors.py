# yourapp/context_processors.py

from .models import Notification  # Replace with your actual app name

def notification_context(request):
    """
    Context processor to add notification data to all templates
    """
    context = {
        'notifications': None,
        'unread_count': 0,
        'unread_notifications': None,
        'recent_notifications': None,
    }
    
    if request.user.is_authenticated:
        # Get all notifications for the user
        notifications = Notification.objects.filter(user=request.user)
        
        # Get unread notifications and count
        unread_notifications = notifications.filter(is_read=False)
        unread_count = unread_notifications.count()
        
        # Get recent notifications (last 10)
        recent_notifications = notifications.order_by('-created_at')[:10]
        
        context.update({
            'notifications': notifications,
            'unread_count': unread_count,
            'unread_notifications': unread_notifications,
            'recent_notifications': recent_notifications,
        })
    
    return context

def notification_stats(request):
    """
    Lightweight context processor that only provides notification stats
    """
    if request.user.is_authenticated:
        unread_count = Notification.objects.filter(
            user=request.user, 
            is_read=False
        ).count()
        
        return {
            'notification_unread_count': unread_count,
            'has_notifications': unread_count > 0
        }
    
    return {
        'notification_unread_count': 0,
        'has_notifications': False
    }