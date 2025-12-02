from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone
from datetime import timedelta
from accounts.models import User
from properties.models import Property


class Booking(models.Model):
    """Booking model"""

    class BookingStatus(models.TextChoices):
        PENDING = "pending", "Pending"
        CONFIRMED = "confirmed", "Confirmed"
        CANCELLED = "cancelled", "Cancelled"
        COMPLETED = "completed", "Completed"

    property_obj = models.ForeignKey(
        Property, on_delete=models.CASCADE, related_name="bookings"
    )
    guest = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bookings")
    check_in = models.DateField()
    check_out = models.DateField()
    guest_count = models.PositiveIntegerField()
    status = models.CharField(
        max_length=20, choices=BookingStatus.choices, default=BookingStatus.PENDING
    )

    # Pricing
    base_price = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[MinValueValidator(0)]
    )
    cleaning_fee = models.DecimalField(
        max_digits=10, decimal_places=2, default=0, validators=[MinValueValidator(0)]
    )
    service_fee = models.DecimalField(
        max_digits=10, decimal_places=2, default=0, validators=[MinValueValidator(0)]
    )
    security_deposit = models.DecimalField(
        max_digits=10, decimal_places=2, default=0, validators=[MinValueValidator(0)]
    )
    total_price = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[MinValueValidator(0)]
    )

    # Cancellation
    cancellation_policy = models.CharField(
        max_length=20,
        choices=Property.CancellationPolicy.choices,
        default=Property.CancellationPolicy.MODERATE,
    )
    cancelled_at = models.DateTimeField(blank=True, null=True)
    cancellation_refund = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["property_obj", "check_in", "check_out"]),
            models.Index(fields=["guest", "status"]),
            models.Index(fields=["status", "check_in"]),
        ]

    def __str__(self):
        return f"{self.property_obj.title} - {self.guest.username} ({self.check_in} to {self.check_out})"

    def clean(self):
        """Validate booking dates and conflicts"""
        from django.core.exceptions import ValidationError

        if self.check_out <= self.check_in:
            raise ValidationError("Check-out date must be after check-in date.")

        # Check minimum stay
        nights = (self.check_out - self.check_in).days
        if nights < self.property_obj.min_stay:
            raise ValidationError(
                f"Minimum stay is {self.property_obj.min_stay} nights."
            )

        # Check maximum stay
        if nights > self.property_obj.max_stay:
            raise ValidationError(
                f"Maximum stay is {self.property_obj.max_stay} nights."
            )

        # Check guest capacity
        if self.guest_count > self.property_obj.max_guests:
            raise ValidationError(
                f"Maximum {self.property_obj.max_guests} guests allowed."
            )

        # Check for conflicts (only if not cancelled)
        if self.status != self.BookingStatus.CANCELLED:
            conflicting_bookings = Booking.objects.filter(
                property_obj=self.property_obj,
                status__in=[
                    self.BookingStatus.PENDING,
                    self.BookingStatus.CONFIRMED,
                ],
            ).exclude(pk=self.pk)

            for booking in conflicting_bookings:
                if not (
                    self.check_out <= booking.check_in
                    or self.check_in >= booking.check_out
                ):
                    raise ValidationError(
                        "This property is already booked for the selected dates."
                    )

    def save(self, *args, **kwargs):
        """Override save to validate and calculate price"""
        self.full_clean()
        if not self.pk or self._state.adding:
            # Calculate price on creation
            self.calculate_price()
            # Set cancellation policy from property
            if not self.cancellation_policy:
                self.cancellation_policy = self.property_obj.cancellation_policy
        super().save(*args, **kwargs)

    def calculate_price(self):
        """Calculate total booking price"""
        from datetime import timedelta

        nights = (self.check_out - self.check_in).days
        self.base_price = self.property_obj.base_price * nights
        self.cleaning_fee = self.property_obj.cleaning_fee
        self.service_fee = self.property_obj.service_fee
        # Security deposit is typically a percentage of base price
        if not self.security_deposit:
            self.security_deposit = self.base_price * 0.1  # 10% default
        self.total_price = (
            self.base_price + self.cleaning_fee + self.service_fee
        )

    def calculate_refund(self):
        """Calculate refund based on cancellation policy"""
        if self.status != self.BookingStatus.CANCELLED:
            return 0

        days_until_checkin = (self.check_in - timezone.now().date()).days

        if self.cancellation_policy == Property.CancellationPolicy.FLEXIBLE:
            # Full refund if cancelled more than 1 day before check-in
            if days_until_checkin > 1:
                return self.total_price
            # 50% refund if cancelled 1 day or less before check-in
            return self.total_price * 0.5

        elif self.cancellation_policy == Property.CancellationPolicy.MODERATE:
            # Full refund if cancelled more than 5 days before check-in
            if days_until_checkin > 5:
                return self.total_price
            # 50% refund if cancelled 1-5 days before check-in
            elif days_until_checkin > 1:
                return self.total_price * 0.5
            # No refund if cancelled less than 1 day before check-in
            return 0

        elif self.cancellation_policy == Property.CancellationPolicy.STRICT:
            # 50% refund if cancelled more than 7 days before check-in
            if days_until_checkin > 7:
                return self.total_price * 0.5
            # No refund otherwise
            return 0

        return 0

    def cancel(self):
        """Cancel the booking and calculate refund"""
        if self.status == self.BookingStatus.CANCELLED:
            return

        self.status = self.BookingStatus.CANCELLED
        self.cancelled_at = timezone.now()
        self.cancellation_refund = self.calculate_refund()
        self.save()

    @property
    def nights(self):
        """Calculate number of nights"""
        return (self.check_out - self.check_in).days

    @property
    def is_past(self):
        """Check if booking is in the past"""
        return self.check_out < timezone.now().date()

    @property
    def is_upcoming(self):
        """Check if booking is upcoming"""
        return self.check_in > timezone.now().date()

    @property
    def is_current(self):
        """Check if booking is currently active"""
        today = timezone.now().date()
        return self.check_in <= today <= self.check_out
