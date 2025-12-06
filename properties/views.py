from rest_framework import viewsets, status, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.parsers import MultiPartParser, FormParser
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.shortcuts import get_object_or_404
from accounts.permissions import IsHost, IsOwner
from .models import Property, PropertyPhoto, Availability, BlockedDate
from .serializers import (
    PropertyListSerializer,
    PropertyDetailSerializer,
    PropertyCreateUpdateSerializer,
    PropertyPhotoSerializer,
    AvailabilitySerializer,
    BlockedDateSerializer,
)
from .filters import PropertyFilter


class PropertyViewSet(viewsets.ModelViewSet):
    """ViewSet for property CRUD operations"""

    queryset = Property.objects.all()
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = PropertyFilter
    search_fields = ["title", "description", "city", "country"]
    ordering_fields = ["created_at", "base_price"]
    ordering = ["-created_at"]

    def get_serializer_class(self):
        if self.action == "list":
            return PropertyListSerializer
        elif self.action in ["create", "update", "partial_update"]:
            return PropertyCreateUpdateSerializer
        return PropertyDetailSerializer

    def get_permissions(self):
        """Set permissions based on action"""
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsHost()]
        return [AllowAny()]

    def get_queryset(self):
        """Filter queryset based on status"""
        queryset = super().get_queryset()
        # Only show active properties to non-owners
        if self.action == "list" and not (
            self.request.user.is_authenticated
            and self.request.user.is_host
        ):
            queryset = queryset.filter(status=Property.PropertyStatus.ACTIVE)
        return queryset.select_related("host").prefetch_related("photos")

    @action(
        detail=True,
        methods=["get"],
        permission_classes=[AllowAny],
        url_path="availability",
    )
    def availability(self, request, pk=None):
        """Get availability calendar for a property"""
        property_obj = self.get_object()
        start_date = request.query_params.get("start_date")
        end_date = request.query_params.get("end_date")

        availability = property_obj.availability.all()
        if start_date:
            availability = availability.filter(date__gte=start_date)
        if end_date:
            availability = availability.filter(date__lte=end_date)

        serializer = AvailabilitySerializer(availability, many=True)
        return Response(serializer.data)

    @action(
        detail=True,
        methods=["post"],
        permission_classes=[IsAuthenticated, IsHost],
        url_path="photos",
        parser_classes=[MultiPartParser, FormParser],
    )
    def upload_photos(self, request, pk=None):
        """Upload photos for a property (multipart/form-data)"""
        property_obj = self.get_object()
        # Check ownership
        if property_obj.host != request.user:
            return Response(
                {"error": "You don't have permission to upload photos for this property."},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = PropertyPhotoSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(property=property_obj)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PropertyPhotoViewSet(viewsets.ModelViewSet):
    """ViewSet for property photos"""

    queryset = PropertyPhoto.objects.all()
    serializer_class = PropertyPhotoSerializer
    permission_classes = [IsAuthenticated, IsHost]
    parser_classes = [MultiPartParser, FormParser]

    def get_queryset(self):
        property_id = self.kwargs.get("property_pk")
        return PropertyPhoto.objects.filter(property_id=property_id)

    def perform_create(self, serializer):
        property_id = self.kwargs.get("property_pk")
        property_obj = get_object_or_404(Property, id=property_id)
        if property_obj.host != self.request.user:
            raise PermissionError(
                "You don't have permission to add photos to this property."
            )
        serializer.save(property=property_obj)


class AvailabilityViewSet(viewsets.ModelViewSet):
    """ViewSet for availability calendar"""

    queryset = Availability.objects.all()
    serializer_class = AvailabilitySerializer
    permission_classes = [IsAuthenticated, IsHost]

    def get_queryset(self):
        property_id = self.kwargs.get("property_pk")
        return Availability.objects.filter(property_id=property_id)

    def perform_create(self, serializer):
        property_id = self.kwargs.get("property_pk")
        property_obj = get_object_or_404(Property, id=property_id)
        if property_obj.host != self.request.user:
            raise PermissionError(
                "You don't have permission to manage availability for this property."
            )
        serializer.save(property=property_obj)


class BlockedDateViewSet(viewsets.ModelViewSet):
    """ViewSet for blocked dates"""

    queryset = BlockedDate.objects.all()
    serializer_class = BlockedDateSerializer
    permission_classes = [IsAuthenticated, IsHost]

    def get_queryset(self):
        property_id = self.kwargs.get("property_pk")
        return BlockedDate.objects.filter(property_id=property_id)

    def perform_create(self, serializer):
        property_id = self.kwargs.get("property_pk")
        property_obj = get_object_or_404(Property, id=property_id)
        if property_obj.host != self.request.user:
            raise PermissionError(
                "You don't have permission to block dates for this property."
            )
        serializer.save(property=property_obj)
