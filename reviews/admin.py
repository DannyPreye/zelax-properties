from django.contrib import admin
from .models import Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    """Admin interface for Review model"""

    list_display = [
        "id",
        "reviewer",
        "reviewee",
        "property",
        "review_type",
        "rating",
        "is_visible",
        "is_moderated",
        "created_at",
    ]
    list_filter = [
        "review_type",
        "rating",
        "is_visible",
        "is_moderated",
        "created_at",
    ]
    search_fields = [
        "reviewer__username",
        "reviewee__username",
        "property__title",
        "comment",
    ]
    readonly_fields = ["created_at", "updated_at"]
    actions = ["approve_reviews", "hide_reviews", "mark_as_moderated"]
    fieldsets = (
        ("Review Information", {"fields": ("booking", "reviewer", "reviewee", "property", "review_type")}),
        ("Ratings", {"fields": ("rating", "cleanliness", "accuracy", "communication", "location", "value")}),
        ("Content", {"fields": ("comment",)}),
        ("Moderation", {"fields": ("is_visible", "is_moderated")}),
        ("Timestamps", {"fields": ("created_at", "updated_at")}),
    )

    def approve_reviews(self, request, queryset):
        """Approve selected reviews"""
        updated = queryset.update(is_visible=True, is_moderated=True)
        self.message_user(
            request,
            f"{updated} review(s) approved and made visible.",
        )
    approve_reviews.short_description = "Approve selected reviews"

    def hide_reviews(self, request, queryset):
        """Hide selected reviews"""
        updated = queryset.update(is_visible=False)
        self.message_user(
            request,
            f"{updated} review(s) hidden.",
        )
    hide_reviews.short_description = "Hide selected reviews"

    def mark_as_moderated(self, request, queryset):
        """Mark selected reviews as moderated"""
        updated = queryset.update(is_moderated=True)
        self.message_user(
            request,
            f"{updated} review(s) marked as moderated.",
        )
    mark_as_moderated.short_description = "Mark as moderated"
