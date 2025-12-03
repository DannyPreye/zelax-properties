from rest_framework import serializers
from accounts.serializers import UserPublicSerializer
from bookings.serializers import BookingSerializer
from .models import Payment, Payout


class PaymentSerializer(serializers.ModelSerializer):
    """Serializer for payments"""

    user = UserPublicSerializer(read_only=True)
    booking = BookingSerializer(read_only=True)

    class Meta:
        model = Payment
        fields = [
            "id",
            "booking",
            "user",
            "amount",
            "currency",
            "payment_method",
            "transaction_reference",
            "status",
            "paystack_reference",
            "metadata",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "user",
            "transaction_reference",
            "status",
            "paystack_reference",
            "metadata",
            "created_at",
            "updated_at",
        ]


class PaymentInitializeSerializer(serializers.Serializer):
    """Serializer for initializing Paystack payment"""

    booking_id = serializers.IntegerField()
    email = serializers.EmailField()

    def validate_booking_id(self, value):
        from bookings.models import Booking

        try:
            booking = Booking.objects.get(id=value)
            if booking.guest != self.context["request"].user:
                raise serializers.ValidationError(
                    "You can only pay for your own bookings."
                )
            if booking.status != Booking.BookingStatus.CONFIRMED:
                raise serializers.ValidationError(
                    "Only confirmed bookings can be paid for."
                )
            return value
        except Booking.DoesNotExist:
            raise serializers.ValidationError("Booking not found.")


class PaymentVerifySerializer(serializers.Serializer):
    """Serializer for verifying Paystack payment"""

    reference = serializers.CharField()


class PayoutSerializer(serializers.ModelSerializer):
    """Serializer for payouts"""

    host = UserPublicSerializer(read_only=True)

    class Meta:
        model = Payout
        fields = [
            "id",
            "host",
            "amount",
            "currency",
            "status",
            "transaction_reference",
            "paystack_reference",
            "processed_at",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "host",
            "status",
            "transaction_reference",
            "paystack_reference",
            "processed_at",
            "created_at",
            "updated_at",
        ]


class PayoutRequestSerializer(serializers.Serializer):
    """Serializer for requesting payout"""

    amount = serializers.DecimalField(max_digits=10, decimal_places=2)




