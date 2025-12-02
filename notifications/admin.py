from django.contrib import admin
from .models import Notification, NotificationPreference


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    """Admin interface for Notification model"""

    list_display = [
        "id",
        "user",
        "type",
        "title",
        "is_read",
        "created_at",
    ]
    list_filter = ["type", "is_read", "created_at"]
    search_fields = ["user__username", "title", "message"]
    readonly_fields = ["created_at"]


@admin.register(NotificationPreference)
class NotificationPreferenceAdmin(admin.ModelAdmin):
    """Admin interface for NotificationPreference model"""

    list_display = [
        "user",
        "email_enabled",
        "push_enabled",
        "booking_notifications",
        "message_notifications",
    ]
    search_fields = ["user__username"]
