from rest_framework import viewsets, status, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from accounts.permissions import IsHost, IsOwner
from properties.models import Property
from .models import Booking
from .serializers import (
    BookingSerializer,
    BookingCreateSerializer,
    PriceCalculationSerializer,
)


class BookingViewSet(viewsets.ModelViewSet):
    """ViewSet for booking operations"""

    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Filter bookings based on user role"""
        user = self.request.user
        if user.is_host:
            # Hosts see bookings for their properties
            return Booking.objects.filter(property__host=user).select_related(
                "property", "guest"
            )
        else:
            # Guests see their own bookings
            return Booking.objects.filter(guest=user).select_related(
                "property", "guest"
            )

    def get_serializer_class(self):
        if self.action == "create":
            return BookingCreateSerializer
        return BookingSerializer

    def perform_create(self, serializer):
        """Create booking with guest set to current user"""
        serializer.save(guest=self.request.user)

    @action(
        detail=True,
        methods=["post"],
        permission_classes=[IsAuthenticated, IsHost],
        url_path="confirm",
    )
    def confirm(self, request, pk=None):
        """Host confirms a booking"""
        booking = self.get_object()
        if booking.property_obj.host != request.user:
            return Response(
                {"error": "You don't have permission to confirm this booking."},
                status=status.HTTP_403_FORBIDDEN,
            )

        if booking.status != Booking.BookingStatus.PENDING:
            return Response(
                {"error": "Only pending bookings can be confirmed."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        booking.status = Booking.BookingStatus.CONFIRMED
        booking.save()

        serializer = self.get_serializer(booking)
        return Response(serializer.data)

    @action(
        detail=True,
        methods=["post"],
        permission_classes=[IsAuthenticated],
        url_path="cancel",
    )
    def cancel(self, request, pk=None):
        """Cancel a booking"""
        booking = self.get_object()
        # Only guest or host can cancel
        if booking.guest != request.user and booking.property_obj.host != request.user:
            return Response(
                {"error": "You don't have permission to cancel this booking."},
                status=status.HTTP_403_FORBIDDEN,
            )

        if booking.status == Booking.BookingStatus.CANCELLED:
            return Response(
                {"error": "Booking is already cancelled."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if booking.status == Booking.BookingStatus.COMPLETED:
            return Response(
                {"error": "Cannot cancel a completed booking."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        booking.cancel()
        serializer = self.get_serializer(booking)
        return Response(serializer.data)

    @action(
        detail=True,
        methods=["get"],
        permission_classes=[IsAuthenticated],
        url_path="calculate-price",
    )
    def calculate_price(self, request, pk=None):
        """Calculate booking price"""
        booking = self.get_object()
        # Recalculate price
        booking.calculate_price()
        serializer = self.get_serializer(booking)
        return Response(serializer.data)


class PriceCalculationView(generics.GenericAPIView):
    """View for calculating booking price before creating booking"""

    permission_classes = [IsAuthenticated]
    serializer_class = PriceCalculationSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        property_obj = Property.objects.get(
            id=serializer.validated_data["property_id"]
        )
        check_in = serializer.validated_data["check_in"]
        check_out = serializer.validated_data["check_out"]
        guest_count = serializer.validated_data["guest_count"]

        # Create temporary booking to calculate price
        temp_booking = Booking(
            property=property_obj,
            guest=request.user,
            check_in=check_in,
            check_out=check_out,
            guest_count=guest_count,
        )
        temp_booking.calculate_price()

        return Response(
            {
                "base_price": str(temp_booking.base_price),
                "cleaning_fee": str(temp_booking.cleaning_fee),
                "service_fee": str(temp_booking.service_fee),
                "security_deposit": str(temp_booking.security_deposit),
                "total_price": str(temp_booking.total_price),
                "nights": temp_booking.nights,
            }
        )
