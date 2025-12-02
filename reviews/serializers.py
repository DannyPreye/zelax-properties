from rest_framework import serializers
from accounts.serializers import UserPublicSerializer
from properties.serializers import PropertyListSerializer
from bookings.serializers import BookingSerializer
from .models import Review


class ReviewSerializer(serializers.ModelSerializer):
    """Serializer for review list/detail"""

    reviewer = UserPublicSerializer(read_only=True)
    reviewee = UserPublicSerializer(read_only=True)
    property = PropertyListSerializer(read_only=True)
    booking = BookingSerializer(read_only=True)

    class Meta:
        model = Review
        fields = [
            "id",
            "booking",
            "reviewer",
            "reviewee",
            "property",
            "review_type",
            "rating",
            "cleanliness",
            "accuracy",
            "communication",
            "location",
            "value",
            "comment",
            "is_visible",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "reviewer",
            "reviewee",
            "property",
            "booking",
            "created_at",
            "updated_at",
        ]


class ReviewCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating a review"""

    class Meta:
        model = Review
        fields = [
            "booking",
            "review_type",
            "rating",
            "cleanliness",
            "accuracy",
            "communication",
            "location",
            "value",
            "comment",
        ]

    def validate(self, attrs):
        booking = attrs["booking"]
        reviewer = self.context["request"].user
        review_type = attrs["review_type"]

        # Check if booking is completed
        if booking.status != booking.BookingStatus.COMPLETED:
            raise serializers.ValidationError(
                "Reviews can only be submitted for completed bookings."
            )

        # Check if review already exists
        if Review.objects.filter(
            booking=booking, reviewer=reviewer, review_type=review_type
        ).exists():
            raise serializers.ValidationError(
                "You have already submitted a review for this booking."
            )

        # Validate review type
        if review_type == Review.ReviewType.GUEST_TO_PROPERTY:
            if reviewer != booking.guest:
                raise serializers.ValidationError(
                    "Only the guest can review the property."
                )
        elif review_type == Review.ReviewType.GUEST_TO_HOST:
            if reviewer != booking.guest:
                raise serializers.ValidationError(
                    "Only the guest can review the host."
                )
        elif review_type == Review.ReviewType.HOST_TO_GUEST:
            if reviewer != booking.property_obj.host:
                raise serializers.ValidationError(
                    "Only the host can review the guest."
                )

        return attrs

    def create(self, validated_data):
        booking = validated_data["booking"]
        reviewer = self.context["request"].user
        review_type = validated_data["review_type"]

        # Set reviewee based on review type
        if review_type == Review.ReviewType.GUEST_TO_HOST:
            reviewee = booking.property_obj.host
        elif review_type == Review.ReviewType.HOST_TO_GUEST:
            reviewee = booking.guest
        else:
            # For property reviews, reviewee is the property owner
            reviewee = booking.property_obj.host

        review = Review.objects.create(
            booking=booking,
            reviewer=reviewer,
            reviewee=reviewee,
            property=booking.property_obj,
            **validated_data,
        )
        return review

