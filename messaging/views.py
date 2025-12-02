from rest_framework import viewsets, generics, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from .models import MessageThread, Message
from .serializers import (
    MessageThreadSerializer,
    MessageThreadCreateSerializer,
    MessageSerializer,
    MessageCreateSerializer,
)


class MessageThreadViewSet(viewsets.ModelViewSet):
    """ViewSet for message thread operations"""

    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Get threads where user is a participant"""
        return MessageThread.objects.filter(
            participants=self.request.user
        ).prefetch_related("participants", "messages").distinct()

    def get_serializer_class(self):
        if self.action == "create":
            return MessageThreadCreateSerializer
        return MessageThreadSerializer

    def perform_create(self, serializer):
        """Create thread with current user as participant"""
        serializer.save()

    @action(
        detail=True,
        methods=["get", "post"],
        permission_classes=[IsAuthenticated],
        url_path="messages",
    )
    def messages(self, request, pk=None):
        """Get or create messages in a thread"""
        thread = self.get_object()
        # Ensure user is a participant
        if request.user not in thread.participants.all():
            return Response(
                {"error": "You don't have permission to access this thread."},
                status=status.HTTP_403_FORBIDDEN,
            )

        if request.method == "GET":
            messages = thread.messages.select_related("sender").all()
            serializer = MessageSerializer(messages, many=True)
            # Mark messages as read
            thread.messages.filter(is_read=False).exclude(
                sender=request.user
            ).update(is_read=True)
            return Response(serializer.data)

        elif request.method == "POST":
            serializer = MessageCreateSerializer(
                data=request.data, context={"thread": thread, "request": request}
            )
            if serializer.is_valid():
                message = serializer.save()
                # Update thread updated_at
                thread.save()
                return Response(
                    MessageSerializer(message).data, status=status.HTTP_201_CREATED
                )
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MessageViewSet(viewsets.ModelViewSet):
    """ViewSet for message operations"""

    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        thread_id = self.kwargs.get("thread_id")
        return Message.objects.filter(thread_id=thread_id).select_related("sender")

    def get_serializer_class(self):
        if self.action == "create":
            return MessageCreateSerializer
        return MessageSerializer

    def perform_create(self, serializer):
        thread_id = self.kwargs.get("thread_id")
        thread = get_object_or_404(MessageThread, id=thread_id)
        # Ensure user is a participant
        if self.request.user not in thread.participants.all():
            raise PermissionError(
                "You don't have permission to send messages in this thread."
            )
        serializer.save(thread=thread, sender=self.request.user)
