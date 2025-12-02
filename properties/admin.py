from django.contrib import admin
from .models import Property, PropertyPhoto, Availability, BlockedDate


@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    """Admin interface for Property model"""

    list_display = [
        "title",
        "host",
        "property_type",
        "city",
        "country",
        "status",
        "base_price",
        "booking_count",
        "created_at",
    ]
    list_filter = ["status", "property_type", "city", "country", "created_at"]
    search_fields = ["title", "description", "address", "city", "host__username"]
    readonly_fields = ["created_at", "updated_at"]
    actions = ["approve_properties", "reject_properties", "activate_properties", "deactivate_properties"]
    fieldsets = (
        ("Basic Information", {"fields": ("title", "description", "property_type", "host")}),
        ("Location", {"fields": ("address", "city", "country", "latitude", "longitude")}),
        ("Amenities & Rules", {"fields": ("amenities", "house_rules", "cancellation_policy")}),
        ("Pricing", {"fields": ("base_price", "cleaning_fee", "service_fee")}),
        ("Capacity", {"fields": ("max_guests", "bedrooms", "beds", "bathrooms")}),
        ("Booking Settings", {"fields": ("instant_booking", "min_stay", "max_stay")}),
        ("Status", {"fields": ("status",)}),
        ("Timestamps", {"fields": ("created_at", "updated_at")}),
    )

    def booking_count(self, obj):
        """Display booking count"""
        return obj.bookings.count()
    booking_count.short_description = "Bookings"

    def approve_properties(self, request, queryset):
        """Approve selected properties"""
        updated = queryset.update(status=Property.PropertyStatus.ACTIVE)
        self.message_user(
            request,
            f"{updated} property(ies) approved successfully.",
        )
    approve_properties.short_description = "Approve selected properties"

    def reject_properties(self, request, queryset):
        """Reject selected properties"""
        updated = queryset.update(status=Property.PropertyStatus.INACTIVE)
        self.message_user(
            request,
            f"{updated} property(ies) rejected.",
        )
    reject_properties.short_description = "Reject selected properties"

    def activate_properties(self, request, queryset):
        """Activate selected properties"""
        updated = queryset.update(status=Property.PropertyStatus.ACTIVE)
        self.message_user(
            request,
            f"{updated} property(ies) activated.",
        )
    activate_properties.short_description = "Activate selected properties"

    def deactivate_properties(self, request, queryset):
        """Deactivate selected properties"""
        updated = queryset.update(status=Property.PropertyStatus.INACTIVE)
        self.message_user(
            request,
            f"{updated} property(ies) deactivated.",
        )
    deactivate_properties.short_description = "Deactivate selected properties"


@admin.register(PropertyPhoto)
class PropertyPhotoAdmin(admin.ModelAdmin):
    """Admin interface for PropertyPhoto model"""

    list_display = ["property", "is_primary", "order", "created_at"]
    list_filter = ["is_primary", "created_at"]
    search_fields = ["property__title"]


@admin.register(Availability)
class AvailabilityAdmin(admin.ModelAdmin):
    """Admin interface for Availability model"""

    list_display = ["property", "date", "is_available", "price_override"]
    list_filter = ["is_available", "date"]
    search_fields = ["property__title"]


@admin.register(BlockedDate)
class BlockedDateAdmin(admin.ModelAdmin):
    """Admin interface for BlockedDate model"""

    list_display = ["property", "start_date", "end_date", "reason", "created_at"]
    list_filter = ["start_date", "end_date", "created_at"]
    search_fields = ["property__title", "reason"]
