from django.contrib import admin
from .models import Wishlist, WishlistItem


@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    """Admin interface for Wishlist model"""

    list_display = ["id", "user", "name", "is_public", "created_at"]
    list_filter = ["is_public", "created_at"]
    search_fields = ["user__username", "name"]


@admin.register(WishlistItem)
class WishlistItemAdmin(admin.ModelAdmin):
    """Admin interface for WishlistItem model"""

    list_display = ["id", "wishlist", "property", "added_at"]
    list_filter = ["added_at"]
    search_fields = ["wishlist__name", "property__title"]
