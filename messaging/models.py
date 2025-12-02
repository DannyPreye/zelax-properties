from django.db import models
from accounts.models import User
from bookings.models import Booking


class MessageThread(models.Model):
    """Message thread model for conversations"""

    booking = models.ForeignKey(
        Booking, on_delete=models.CASCADE, related_name="message_threads", null=True, blank=True
    )
    participants = models.ManyToManyField(User, related_name="message_threads")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]
        indexes = [models.Index(fields=["updated_at"])]

    def __str__(self):
        participants_list = ", ".join(
            [user.username for user in self.participants.all()]
        )
        return f"Thread: {participants_list}"

    @property
    def last_message(self):
        """Get the last message in the thread"""
        return self.messages.order_by("-created_at").first()


class Message(models.Model):
    """Message model for individual messages"""

    thread = models.ForeignKey(
        MessageThread, on_delete=models.CASCADE, related_name="messages"
    )
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sent_messages")
    content = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]
        indexes = [
            models.Index(fields=["thread", "created_at"]),
            models.Index(fields=["sender", "is_read"]),
        ]

    def __str__(self):
        return f"{self.sender.username}: {self.content[:50]}"

    def mark_as_read(self):
        """Mark message as read"""
        self.is_read = True
        self.save()
