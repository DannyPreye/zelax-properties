from rest_framework import serializers
from accounts.serializers import UserPublicSerializer
from bookings.serializers import BookingSerializer
from .models import MessageThread, Message


class MessageSerializer(serializers.ModelSerializer):
    """Serializer for messages"""

    sender = UserPublicSerializer(read_only=True)

    class Meta:
        model = Message
        fields = ["id", "sender", "content", "is_read", "created_at"]
        read_only_fields = ["id", "sender", "is_read", "created_at"]


class MessageCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating messages"""

    class Meta:
        model = Message
        fields = ["content"]

    def create(self, validated_data):
        thread = self.context["thread"]
        sender = self.context["request"].user
        return Message.objects.create(
            thread=thread, sender=sender, **validated_data
        )


class MessageThreadSerializer(serializers.ModelSerializer):
    """Serializer for message threads"""

    participants = UserPublicSerializer(many=True, read_only=True)
    booking = BookingSerializer(read_only=True)
    last_message = serializers.SerializerMethodField()
    unread_count = serializers.SerializerMethodField()

    class Meta:
        model = MessageThread
        fields = [
            "id",
            "booking",
            "participants",
            "last_message",
            "unread_count",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def get_last_message(self, obj):
        last_msg = obj.last_message
        if last_msg:
            return MessageSerializer(last_msg).data
        return None

    def get_unread_count(self, obj):
        user = self.context.get("request").user
        return obj.messages.filter(is_read=False).exclude(sender=user).count()


class MessageThreadCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating message threads"""

    participant_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = MessageThread
        fields = ["booking", "participant_id"]

    def create(self, validated_data):
        participant_id = validated_data.pop("participant_id")
        user = self.context["request"].user
        thread = MessageThread.objects.create(**validated_data)
        thread.participants.add(user, participant_id)
        return thread




