from rest_framework import viewsets, generics, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.shortcuts import get_object_or_404
from django.db import models
from accounts.permissions import IsOwner
from properties.models import Property
from .models import Wishlist, WishlistItem
from .serializers import (
    WishlistSerializer,
    WishlistCreateSerializer,
    WishlistItemSerializer,
)


class WishlistViewSet(viewsets.ModelViewSet):
    """ViewSet for wishlist operations"""

    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Get user's wishlists or public wishlists"""
        user = self.request.user
        if self.action == "list":
            # Users see their own wishlists and public wishlists
            return Wishlist.objects.filter(
                models.Q(user=user) | models.Q(is_public=True)
            ).prefetch_related("items__property").distinct()
        return Wishlist.objects.filter(user=user).prefetch_related("items__property")

    def get_serializer_class(self):
        if self.action == "create":
            return WishlistCreateSerializer
        return WishlistSerializer

    def perform_create(self, serializer):
        """Create wishlist with user set to current user"""
        serializer.save()

    @action(
        detail=True,
        methods=["post", "delete"],
        permission_classes=[IsAuthenticated],
        url_path="properties/(?P<property_id>[^/.]+)",
    )
    def manage_property(self, request, pk=None, property_id=None):
        """Add or remove property from wishlist"""
        wishlist = self.get_object()
        # Check ownership
        if wishlist.user != request.user:
            return Response(
                {"error": "You don't have permission to modify this wishlist."},
                status=status.HTTP_403_FORBIDDEN,
            )

        property_obj = get_object_or_404(Property, id=property_id)

        if request.method == "POST":
            # Add property to wishlist
            item, created = WishlistItem.objects.get_or_create(
                wishlist=wishlist, property=property_obj
            )
            if created:
                serializer = WishlistItemSerializer(item)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(
                {"error": "Property already in wishlist."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        elif request.method == "DELETE":
            # Remove property from wishlist
            item = get_object_or_404(WishlistItem, wishlist=wishlist, property=property_obj)
            item.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
