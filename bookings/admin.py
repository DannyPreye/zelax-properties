from django.contrib import admin
from .models import Booking


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    """Admin interface for Booking model"""

    list_display = [
        "id",
        "property_obj",
        "guest",
        "check_in",
        "check_out",
        "guest_count",
        "status",
        "total_price",
        "nights",
        "created_at",
    ]
    list_filter = ["status", "check_in", "check_out", "created_at"]
    search_fields = [
        "property_obj__title",
        "guest__username",
        "guest__email",
    ]
    readonly_fields = ["created_at", "updated_at", "cancelled_at", "nights"]
    actions = ["confirm_bookings", "cancel_bookings"]
    fieldsets = (
        ("Booking Information", {"fields": ("property_obj", "guest", "check_in", "check_out", "guest_count", "status")}),
        ("Pricing", {"fields": ("base_price", "cleaning_fee", "service_fee", "security_deposit", "total_price")}),
        ("Cancellation", {"fields": ("cancellation_policy", "cancelled_at", "cancellation_refund")}),
        ("Timestamps", {"fields": ("created_at", "updated_at")}),
    )

    def nights(self, obj):
        """Display number of nights"""
        return obj.nights
    nights.short_description = "Nights"

    def confirm_bookings(self, request, queryset):
        """Confirm selected bookings"""
        updated = queryset.filter(status=Booking.BookingStatus.PENDING).update(
            status=Booking.BookingStatus.CONFIRMED
        )
        self.message_user(
            request,
            f"{updated} booking(s) confirmed.",
        )
    confirm_bookings.short_description = "Confirm selected bookings"

    def cancel_bookings(self, request, queryset):
        """Cancel selected bookings"""
        for booking in queryset.exclude(status=Booking.BookingStatus.CANCELLED):
            booking.cancel()
        self.message_user(
            request,
            f"{queryset.count()} booking(s) cancelled.",
        )
    cancel_bookings.short_description = "Cancel selected bookings"
