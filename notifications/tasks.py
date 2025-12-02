from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from .models import Notification, NotificationPreference


@shared_task
def send_email_notification(notification_id):
    """Send email notification"""
    try:
        notification = Notification.objects.get(id=notification_id)
        user = notification.user

        # Check user preferences
        try:
            preferences = user.notification_preferences
            if not preferences.email_enabled:
                return
        except NotificationPreference.DoesNotExist:
            pass

        # Send email
        send_mail(
            subject=notification.title,
            message=notification.message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )
    except Notification.DoesNotExist:
        pass


@shared_task
def create_notification(
    user_id, notification_type, title, message, content_type_id=None, object_id=None
):
    """Create notification"""
    from accounts.models import User

    try:
        user = User.objects.get(id=user_id)
        notification = Notification.objects.create(
            user=user,
            type=notification_type,
            title=title,
            message=message,
        )

        # Set related object if provided
        if content_type_id and object_id:
            content_type = ContentType.objects.get(id=content_type_id)
            notification.content_type = content_type
            notification.object_id = object_id
            notification.save()

        # Send email notification if enabled
        try:
            preferences = user.notification_preferences
            if preferences.email_enabled:
                send_email_notification.delay(notification.id)
        except NotificationPreference.DoesNotExist:
            # Send email by default if no preferences set
            send_email_notification.delay(notification.id)

        return notification.id
    except User.DoesNotExist:
        return None


@shared_task
def send_booking_reminder(booking_id):
    """Send booking reminder"""
    from bookings.models import Booking

    try:
        booking = Booking.objects.get(id=booking_id)
        # Create notification for guest
        create_notification.delay(
            user_id=booking.guest.id,
            notification_type=Notification.NotificationType.BOOKING_CONFIRMATION,
            title="Upcoming Booking Reminder",
            message=f"Your booking at {booking.property_obj.title} starts on {booking.check_in}.",
            content_type_id=ContentType.objects.get_for_model(Booking).id,
            object_id=booking.id,
        )
    except Booking.DoesNotExist:
        pass

