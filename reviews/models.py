from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from accounts.models import User
from properties.models import Property
from bookings.models import Booking


class Review(models.Model):
    """Review model for two-way reviews"""

    class ReviewType(models.TextChoices):
        GUEST_TO_PROPERTY = "guest_to_property", "Guest to Property"
        GUEST_TO_HOST = "guest_to_host", "Guest to Host"
        HOST_TO_GUEST = "host_to_guest", "Host to Guest"

    booking = models.ForeignKey(
        Booking, on_delete=models.CASCADE, related_name="reviews"
    )
    reviewer = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="reviews_given"
    )
    reviewee = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="reviews_received"
    )
    property = models.ForeignKey(
        Property, on_delete=models.CASCADE, related_name="reviews"
    )
    review_type = models.CharField(
        max_length=20, choices=ReviewType.choices
    )

    # Overall rating
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )

    # Category ratings
    cleanliness = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)], blank=True, null=True
    )
    accuracy = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)], blank=True, null=True
    )
    communication = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)], blank=True, null=True
    )
    location = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)], blank=True, null=True
    )
    value = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)], blank=True, null=True
    )

    # Review content
    comment = models.TextField(blank=True)

    # Moderation
    is_visible = models.BooleanField(default=True)
    is_moderated = models.BooleanField(default=False)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["property", "is_visible"]),
            models.Index(fields=["reviewee", "is_visible"]),
            models.Index(fields=["booking", "review_type"]),
        ]
        unique_together = [["booking", "reviewer", "review_type"]]

    def __str__(self):
        return f"{self.reviewer.username} -> {self.reviewee.username} ({self.rating} stars)"

    def clean(self):
        """Validate review based on type"""
        from django.core.exceptions import ValidationError

        # Ensure reviewer and reviewee are different
        if self.reviewer == self.reviewee:
            raise ValidationError("Reviewer and reviewee must be different.")

        # Validate review type matches booking participants
        if self.review_type == self.ReviewType.GUEST_TO_PROPERTY:
            if self.reviewer != self.booking.guest:
                raise ValidationError(
                    "Only the guest can review the property."
                )
        elif self.review_type == self.ReviewType.GUEST_TO_HOST:
            if self.reviewer != self.booking.guest:
                raise ValidationError("Only the guest can review the host.")
            if self.reviewee != self.booking.property_obj.host:
                raise ValidationError("Reviewee must be the property host.")
        elif self.review_type == self.ReviewType.HOST_TO_GUEST:
            if self.reviewer != self.booking.property_obj.host:
                raise ValidationError("Only the host can review the guest.")
            if self.reviewee != self.booking.guest:
                raise ValidationError("Reviewee must be the booking guest.")

    def save(self, *args, **kwargs):
        """Override save to validate and set reviewee"""
        # Set reviewee based on review type
        if self.review_type == self.ReviewType.GUEST_TO_HOST:
            self.reviewee = self.booking.property_obj.host
        elif self.review_type == self.ReviewType.HOST_TO_GUEST:
            self.reviewee = self.booking.guest

        self.full_clean()
        super().save(*args, **kwargs)


def calculate_average_rating(property_obj):
    """Calculate average rating for a property"""
    reviews = Review.objects.filter(
        property=property_obj,
        review_type=Review.ReviewType.GUEST_TO_PROPERTY,
        is_visible=True,
    )
    if not reviews.exists():
        return None

    total_rating = sum(review.rating for review in reviews)
    return round(total_rating / reviews.count(), 2)
