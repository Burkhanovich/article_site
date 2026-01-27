"""
Context processors for users app.
"""


def notifications(request):
    """
    Add notification-related context to all templates.
    """
    context = {
        'unread_notification_count': 0,
    }

    if request.user.is_authenticated:
        from .models import Notification
        context['unread_notification_count'] = Notification.get_unread_count(request.user)

    return context
