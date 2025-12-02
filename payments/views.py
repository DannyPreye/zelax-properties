from rest_framework import viewsets, generics, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from accounts.permissions import IsHost
from bookings.models import Booking
from .models import Payment, Payout
from .serializers import (
    PaymentSerializer,
    PaymentInitializeSerializer,
    PaymentVerifySerializer,
    PayoutSerializer,
    PayoutRequestSerializer,
)
from .services import PaystackService, create_payment, create_payout


class PaymentViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for payment operations"""

    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Get user's payments"""
        return Payment.objects.filter(user=self.request.user).select_related(
            "booking", "user"
        )

    @action(
        detail=False,
        methods=["post"],
        permission_classes=[IsAuthenticated],
        url_path="initialize",
    )
    def initialize(self, request):
        """Initialize Paystack payment"""
        serializer = PaymentInitializeSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)

        booking = get_object_or_404(Booking, id=serializer.validated_data["booking_id"])
        email = serializer.validated_data["email"]

        # Create payment record
        payment = create_payment(booking, request.user, booking.total_price)

        # Initialize Paystack transaction
        paystack_service = PaystackService()
        metadata = {
            "booking_id": booking.id,
            "payment_id": payment.id,
            "user_id": request.user.id,
        }
        result = paystack_service.initialize_transaction(
            email=email,
            amount=booking.total_price,
            reference=payment.transaction_reference,
            metadata=metadata,
        )

        if result and result.get("status"):
            payment.paystack_reference = result["data"]["reference"]
            payment.metadata = result["data"]
            payment.save()

            return Response(
                {
                    "authorization_url": result["data"]["authorization_url"],
                    "access_code": result["data"]["access_code"],
                    "reference": payment.transaction_reference,
                },
                status=status.HTTP_200_OK,
            )

        return Response(
            {"error": "Failed to initialize payment."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    @action(
        detail=False,
        methods=["post"],
        permission_classes=[IsAuthenticated],
        url_path="verify",
    )
    def verify(self, request):
        """Verify Paystack payment"""
        serializer = PaymentVerifySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        reference = serializer.validated_data["reference"]
        payment = get_object_or_404(Payment, transaction_reference=reference)

        # Verify payment belongs to user
        if payment.user != request.user:
            return Response(
                {"error": "You don't have permission to verify this payment."},
                status=status.HTTP_403_FORBIDDEN,
            )

        # Verify with Paystack
        paystack_service = PaystackService()
        result = paystack_service.verify_transaction(reference)

        if result and result.get("status"):
            data = result["data"]
            if data["status"] == "success":
                payment.status = Payment.PaymentStatus.SUCCESS
                payment.paystack_reference = data.get("reference", "")
                payment.metadata = data
                payment.save()

                # Update booking status
                booking = payment.booking
                if booking.status == Booking.BookingStatus.PENDING:
                    booking.status = Booking.BookingStatus.CONFIRMED
                    booking.save()

                return Response(
                    {
                        "status": "success",
                        "message": "Payment verified successfully.",
                        "payment": PaymentSerializer(payment).data,
                    },
                    status=status.HTTP_200_OK,
                )
            else:
                payment.status = Payment.PaymentStatus.FAILED
                payment.metadata = data
                payment.save()

                return Response(
                    {"status": "failed", "message": "Payment verification failed."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        return Response(
            {"error": "Failed to verify payment."},
            status=status.HTTP_400_BAD_REQUEST,
        )


class PayoutViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for payout operations"""

    serializer_class = PayoutSerializer
    permission_classes = [IsAuthenticated, IsHost]

    def get_queryset(self):
        """Get host's payouts"""
        return Payout.objects.filter(host=self.request.user)

    @action(
        detail=False,
        methods=["post"],
        permission_classes=[IsAuthenticated, IsHost],
        url_path="request",
    )
    def request_payout(self, request):
        """Request payout"""
        serializer = PayoutRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        amount = serializer.validated_data["amount"]
        # In a real implementation, you would check available balance
        # and validate payout amount

        payout = create_payout(request.user, amount)

        # In a real implementation, you would initiate Paystack transfer here
        # For now, just create the payout record

        return Response(
            PayoutSerializer(payout).data, status=status.HTTP_201_CREATED
        )
