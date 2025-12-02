from rest_framework import serializers
from accounts.serializers import UserPublicSerializer
from properties.serializers import PropertyListSerializer
from .models import Booking


class BookingSerializer(serializers.ModelSerializer):
    """Serializer for booking list/detail"""

    property_obj = PropertyListSerializer(read_only=True)
    guest = UserPublicSerializer(read_only=True)
    nights = serializers.ReadOnlyField()
    is_past = serializers.ReadOnlyField()
    is_upcoming = serializers.ReadOnlyField()
    is_current = serializers.ReadOnlyField()

    class Meta:
        model = Booking
        fields = [
            "id",
            "property_obj",
            "guest",
            "check_in",
            "check_out",
            "guest_count",
            "status",
            "base_price",
            "cleaning_fee",
            "service_fee",
            "security_deposit",
            "total_price",
            "cancellation_policy",
            "cancelled_at",
            "cancellation_refund",
            "nights",
            "is_past",
            "is_upcoming",
            "is_current",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "guest",
            "status",
            "base_price",
            "cleaning_fee",
            "service_fee",
            "security_deposit",
            "total_price",
            "cancellation_policy",
            "cancelled_at",
            "cancellation_refund",
            "created_at",
            "updated_at",
        ]


class BookingCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating a booking"""

    class Meta:
        model = Booking
        fields = [
            "property_obj",
            "check_in",
            "check_out",
            "guest_count",
        ]

    def validate(self, attrs):
        property_obj = attrs["property_obj"]
        check_in = attrs["check_in"]
        check_out = attrs["check_out"]
        guest_count = attrs["guest_count"]

        # Validate dates
        if check_out <= check_in:
            raise serializers.ValidationError(
                "Check-out date must be after check-in date."
            )

        # Validate minimum stay
        nights = (check_out - check_in).days
        if nights < property_obj.min_stay:
            raise serializers.ValidationError(
                f"Minimum stay is {property_obj.min_stay} nights."
            )

        # Validate maximum stay
        if nights > property_obj.max_stay:
            raise serializers.ValidationError(
                f"Maximum stay is {property_obj.max_stay} nights."
            )

        # Validate guest capacity
        if guest_count > property_obj.max_guests:
            raise serializers.ValidationError(
                f"Maximum {property_obj.max_guests} guests allowed."
            )

        # Check for conflicts
        conflicting_bookings = Booking.objects.filter(
            property_obj=property_obj,
            status__in=[
                Booking.BookingStatus.PENDING,
                Booking.BookingStatus.CONFIRMED,
            ],
        )

        for booking in conflicting_bookings:
            if not (check_out <= booking.check_in or check_in >= booking.check_out):
                raise serializers.ValidationError(
                    "This property is already booked for the selected dates."
                )

        return attrs

    def create(self, validated_data):
        validated_data["guest"] = self.context["request"].user
        booking = Booking(**validated_data)
        booking.calculate_price()
        booking.save()
        return booking


class PriceCalculationSerializer(serializers.Serializer):
    """Serializer for price calculation"""

    property_id = serializers.IntegerField()
    check_in = serializers.DateField()
    check_out = serializers.DateField()
    guest_count = serializers.IntegerField()

    def validate(self, attrs):
        from properties.models import Property

        property_obj = Property.objects.get(id=attrs["property_id"])
        check_in = attrs["check_in"]
        check_out = attrs["check_out"]

        if check_out <= check_in:
            raise serializers.ValidationError(
                "Check-out date must be after check-in date."
            )

        nights = (check_out - check_in).days
        if nights < property_obj.min_stay:
            raise serializers.ValidationError(
                f"Minimum stay is {property_obj.min_stay} nights."
            )

        if nights > property_obj.max_stay:
            raise serializers.ValidationError(
                f"Maximum stay is {property_obj.max_stay} nights."
            )

        return attrs

