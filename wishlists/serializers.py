from rest_framework import serializers
from properties.serializers import PropertyListSerializer
from .models import Wishlist, WishlistItem


class WishlistItemSerializer(serializers.ModelSerializer):
    """Serializer for wishlist items"""

    property = PropertyListSerializer(read_only=True)

    class Meta:
        model = WishlistItem
        fields = ["id", "property", "added_at"]
        read_only_fields = ["id", "added_at"]


class WishlistSerializer(serializers.ModelSerializer):
    """Serializer for wishlists"""

    items = WishlistItemSerializer(many=True, read_only=True)
    item_count = serializers.SerializerMethodField()

    class Meta:
        model = Wishlist
        fields = ["id", "name", "is_public", "items", "item_count", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]

    def get_item_count(self, obj):
        return obj.items.count()


class WishlistCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating wishlists"""

    class Meta:
        model = Wishlist
        fields = ["name", "is_public"]

    def create(self, validated_data):
        validated_data["user"] = self.context["request"].user
        return super().create(validated_data)




