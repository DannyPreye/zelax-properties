from django.db import models
from accounts.models import User
from properties.models import Property


class Wishlist(models.Model):
    """Wishlist model for saving favorite properties"""

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="wishlists")
    name = models.CharField(max_length=100)
    is_public = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["user", "is_public"])]

    def __str__(self):
        return f"{self.user.username}'s {self.name}"


class WishlistItem(models.Model):
    """Wishlist item model for properties in wishlists"""

    wishlist = models.ForeignKey(
        Wishlist, on_delete=models.CASCADE, related_name="items"
    )
    property = models.ForeignKey(
        Property, on_delete=models.CASCADE, related_name="wishlist_items"
    )
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [["wishlist", "property"]]
        ordering = ["-added_at"]
        indexes = [models.Index(fields=["wishlist", "added_at"])]

    def __str__(self):
        return f"{self.property.title} in {self.wishlist.name}"
