from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from accounts.models import User


class Notification(models.Model):
    """Notification model for user notifications"""

    class NotificationType(models.TextChoices):
        BOOKING_CONFIRMATION = "booking_confirmation", "Booking Confirmation"
        BOOKING_REQUEST = "booking_request", "Booking Request"
        BOOKING_CANCELLED = "booking_cancelled", "Booking Cancelled"
        MESSAGE = "message", "Message"
        REVIEW = "review", "Review"
        PAYMENT_CONFIRMATION = "payment_confirmation", "Payment Confirmation"
        PAYMENT_FAILED = "payment_failed", "Payment Failed"
        PROPERTY_APPROVED = "property_approved", "Property Approved"
        PROPERTY_REJECTED = "property_rejected", "Property Rejected"

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="notifications"
    )
    type = models.CharField(max_length=50, choices=NotificationType.choices)
    title = models.CharField(max_length=200)
    message = models.TextField()
    is_read = models.BooleanField(default=False)

    # Generic foreign key for related objects
    content_type = models.ForeignKey(
        ContentType, on_delete=models.CASCADE, null=True, blank=True
    )
    object_id = models.PositiveIntegerField(null=True, blank=True)
    related_object = GenericForeignKey("content_type", "object_id")

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "is_read"]),
            models.Index(fields=["user", "type", "is_read"]),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.title}"

    def mark_as_read(self):
        """Mark notification as read"""
        self.is_read = True
        self.save()


class NotificationPreference(models.Model):
    """Notification preferences for users"""

    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="notification_preferences"
    )
    email_enabled = models.BooleanField(default=True)
    push_enabled = models.BooleanField(default=True)
    booking_notifications = models.BooleanField(default=True)
    message_notifications = models.BooleanField(default=True)
    review_notifications = models.BooleanField(default=True)
    payment_notifications = models.BooleanField(default=True)
    property_notifications = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s Notification Preferences"
