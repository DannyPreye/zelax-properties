from django.db import models
from django.core.validators import MinValueValidator
from accounts.models import User


class Property(models.Model):
    """Property listing model"""

    class PropertyType(models.TextChoices):
        APARTMENT = "apartment", "Apartment"
        HOUSE = "house", "House"
        VILLA = "villa", "Villa"
        CONDO = "condo", "Condo"
        TOWNHOUSE = "townhouse", "Townhouse"
        STUDIO = "studio", "Studio"
        CABIN = "cabin", "Cabin"
        COTTAGE = "cottage", "Cottage"
        OTHER = "other", "Other"

    class PropertyStatus(models.TextChoices):
        ACTIVE = "active", "Active"
        INACTIVE = "inactive", "Inactive"
        UNDER_REVIEW = "under_review", "Under Review"

    class CancellationPolicy(models.TextChoices):
        FLEXIBLE = "flexible", "Flexible"
        MODERATE = "moderate", "Moderate"
        STRICT = "strict", "Strict"

    # Basic Information
    title = models.CharField(max_length=200)
    description = models.TextField()
    property_type = models.CharField(
        max_length=20, choices=PropertyType.choices, default=PropertyType.APARTMENT
    )
    host = models.ForeignKey(User, on_delete=models.CASCADE, related_name="properties")

    # Location
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    # Note: Location PointField would require GeoDjango/GDAL
    # For now, we use latitude/longitude for geographic calculations

    # Amenities (stored as JSON)
    amenities = models.JSONField(
        default=dict,
        help_text="Available amenities: WiFi, parking, pool, kitchen, AC, etc.",
    )

    # Rules and Policies
    house_rules = models.TextField(blank=True)
    cancellation_policy = models.CharField(
        max_length=20,
        choices=CancellationPolicy.choices,
        default=CancellationPolicy.MODERATE,
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

    # Capacity
    max_guests = models.PositiveIntegerField()
    bedrooms = models.PositiveIntegerField()
    beds = models.PositiveIntegerField()
    bathrooms = models.DecimalField(max_digits=3, decimal_places=1)

    # Booking Settings
    instant_booking = models.BooleanField(default=False)
    min_stay = models.PositiveIntegerField(default=1)
    max_stay = models.PositiveIntegerField(default=30)

    # Status
    status = models.CharField(
        max_length=20,
        choices=PropertyStatus.choices,
        default=PropertyStatus.UNDER_REVIEW,
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Properties"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status", "property_type"]),
            models.Index(fields=["city", "country"]),
        ]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        """Override save method"""
        super().save(*args, **kwargs)


class PropertyPhoto(models.Model):
    """Property photos model"""

    property = models.ForeignKey(
        Property, on_delete=models.CASCADE, related_name="photos"
    )
    image = models.ImageField(upload_to="properties/")
    is_primary = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["order", "created_at"]
        unique_together = [["property", "is_primary"]]

    def __str__(self):
        return f"{self.property.title} - Photo {self.order}"

    def save(self, *args, **kwargs):
        """Ensure only one primary photo per property"""
        if self.is_primary:
            PropertyPhoto.objects.filter(
                property=self.property, is_primary=True
            ).exclude(pk=self.pk).update(is_primary=False)
        super().save(*args, **kwargs)


class Availability(models.Model):
    """Property availability calendar"""

    property = models.ForeignKey(
        Property, on_delete=models.CASCADE, related_name="availability"
    )
    date = models.DateField()
    is_available = models.BooleanField(default=True)
    price_override = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True
    )

    class Meta:
        unique_together = [["property", "date"]]
        ordering = ["date"]
        indexes = [models.Index(fields=["property", "date", "is_available"])]

    def __str__(self):
        return f"{self.property.title} - {self.date}"


class BlockedDate(models.Model):
    """Blocked dates for properties (unavailable periods)"""

    property = models.ForeignKey(
        Property, on_delete=models.CASCADE, related_name="blocked_dates"
    )
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["start_date"]
        indexes = [models.Index(fields=["property", "start_date", "end_date"])]

    def __str__(self):
        return f"{self.property.title} - {self.start_date} to {self.end_date}"

    def clean(self):
        from django.core.exceptions import ValidationError

        if self.end_date < self.start_date:
            raise ValidationError("End date must be after start date.")
