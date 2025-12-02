from django.contrib import admin
from .models import MessageThread, Message


@admin.register(MessageThread)
class MessageThreadAdmin(admin.ModelAdmin):
    """Admin interface for MessageThread model"""

    list_display = ["id", "booking", "created_at", "updated_at"]
    list_filter = ["created_at", "updated_at"]
    filter_horizontal = ["participants"]
    search_fields = ["participants__username"]


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    """Admin interface for Message model"""

    list_display = ["id", "thread", "sender", "is_read", "created_at"]
    list_filter = ["is_read", "created_at"]
    search_fields = ["sender__username", "content"]
    readonly_fields = ["created_at"]
