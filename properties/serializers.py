from rest_framework import serializers
from accounts.serializers import UserPublicSerializer
from .models import Property, PropertyPhoto, Availability, BlockedDate


class PropertyPhotoSerializer(serializers.ModelSerializer):
    """Serializer for property photos"""

    class Meta:
        model = PropertyPhoto
        fields = ["id", "image", "is_primary", "order"]
        read_only_fields = ["id"]


class PropertyListSerializer(serializers.ModelSerializer):
    """Serializer for property list view"""

    primary_photo = serializers.SerializerMethodField()
    host = UserPublicSerializer(read_only=True)
    average_rating = serializers.SerializerMethodField()
    review_count = serializers.SerializerMethodField()

    class Meta:
        model = Property
        fields = [
            "id",
            "title",
            "property_type",
            "city",
            "country",
            "base_price",
            "primary_photo",
            "host",
            "average_rating",
            "review_count",
            "max_guests",
            "bedrooms",
            "beds",
            "bathrooms",
        ]

    def get_primary_photo(self, obj):
        primary = obj.photos.filter(is_primary=True).first()
        if primary:
            return PropertyPhotoSerializer(primary).data
        # Return first photo if no primary
        first_photo = obj.photos.first()
        if first_photo:
            return PropertyPhotoSerializer(first_photo).data
        return None

    def get_average_rating(self, obj):
        # This will be calculated from reviews
        return None

    def get_review_count(self, obj):
        # This will be calculated from reviews
        return 0


class PropertyDetailSerializer(serializers.ModelSerializer):
    """Serializer for property detail view"""

    photos = PropertyPhotoSerializer(many=True, read_only=True)
    host = UserPublicSerializer(read_only=True)
    amenities = serializers.JSONField()

    class Meta:
        model = Property
        fields = [
            "id",
            "title",
            "description",
            "property_type",
            "host",
            "address",
            "city",
            "country",
            "latitude",
            "longitude",
            "amenities",
            "house_rules",
            "cancellation_policy",
            "base_price",
            "cleaning_fee",
            "service_fee",
            "max_guests",
            "bedrooms",
            "beds",
            "bathrooms",
            "instant_booking",
            "min_stay",
            "max_stay",
            "status",
            "photos",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "host", "created_at", "updated_at"]


class PropertyCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating properties"""

    amenities = serializers.JSONField()

    class Meta:
        model = Property
        fields = [
            "title",
            "description",
            "property_type",
            "address",
            "city",
            "country",
            "latitude",
            "longitude",
            "amenities",
            "house_rules",
            "cancellation_policy",
            "base_price",
            "cleaning_fee",
            "service_fee",
            "max_guests",
            "bedrooms",
            "beds",
            "bathrooms",
            "instant_booking",
            "min_stay",
            "max_stay",
        ]

    def create(self, validated_data):
        validated_data["host"] = self.context["request"].user
        return super().create(validated_data)


class AvailabilitySerializer(serializers.ModelSerializer):
    """Serializer for availability calendar"""

    class Meta:
        model = Availability
        fields = ["id", "date", "is_available", "price_override"]
        read_only_fields = ["id"]


class BlockedDateSerializer(serializers.ModelSerializer):
    """Serializer for blocked dates"""

    class Meta:
        model = BlockedDate
        fields = ["id", "start_date", "end_date", "reason"]
        read_only_fields = ["id"]

    def validate(self, attrs):
        if attrs["end_date"] < attrs["start_date"]:
            raise serializers.ValidationError(
                "End date must be after start date."
            )
        return attrs

