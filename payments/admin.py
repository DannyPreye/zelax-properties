from django.contrib import admin
from .models import Payment, Payout


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    """Admin interface for Payment model"""

    list_display = [
        "id",
        "booking",
        "user",
        "amount",
        "currency",
        "status",
        "payment_method",
        "transaction_reference",
        "created_at",
    ]
    list_filter = ["status", "payment_method", "currency", "created_at"]
    search_fields = [
        "user__username",
        "booking__id",
        "transaction_reference",
        "paystack_reference",
    ]
    readonly_fields = ["created_at", "updated_at"]


@admin.register(Payout)
class PayoutAdmin(admin.ModelAdmin):
    """Admin interface for Payout model"""

    list_display = [
        "id",
        "host",
        "amount",
        "currency",
        "status",
        "transaction_reference",
        "processed_at",
        "created_at",
    ]
    list_filter = ["status", "currency", "created_at", "processed_at"]
    search_fields = [
        "host__username",
        "transaction_reference",
        "paystack_reference",
    ]
    readonly_fields = ["created_at", "updated_at"]
