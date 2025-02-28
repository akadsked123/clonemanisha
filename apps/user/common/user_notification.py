from apps.user.models import Notification

def create_notification(recipient, message, status, sender, notification_url):
    notification = Notification.objects.create(
        recipient=recipient,
        sender=sender,
        message=message,
        status=status,
        notification_url=notification_url
    )
    return notification
