from django.contrib import admin
from django.db.models import Count, Sum, Avg
from django.utils.html import format_html
from accounts.models import User
from properties.models import Property
from bookings.models import Booking
from reviews.models import Review
from payments.models import Payment, Payout


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """Enhanced admin for User model with analytics"""

    list_display = [
        "username",
        "email",
        "role",
        "property_count",
        "booking_count",
        "is_active",
        "date_joined",
    ]
    list_filter = ["role", "is_active", "date_joined"]
    search_fields = ["username", "email"]

    def property_count(self, obj):
        """Display property count"""
        return obj.properties.count()
    property_count.short_description = "Properties"

    def booking_count(self, obj):
        """Display booking count"""
        return obj.bookings.count()
    booking_count.short_description = "Bookings"


# Analytics Dashboard
admin.site.site_header = "Property Rental Platform Admin"
admin.site.site_title = "Property Rental Admin"
admin.site.index_title = "Dashboard"


