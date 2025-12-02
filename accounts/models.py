from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Custom User model with host/guest roles and profile information"""

    class Role(models.TextChoices):
        HOST = "host", "Host"
        GUEST = "guest", "Guest"

    role = models.CharField(
        max_length=10, choices=Role.choices, default=Role.GUEST
    )
    phone = models.CharField(max_length=20, blank=True)
    email_verified = models.BooleanField(default=False)
    identity_verified = models.BooleanField(default=False)
    profile_photo = models.ImageField(upload_to="profiles/", blank=True, null=True)
    bio = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.username

    @property
    def is_host(self):
        return self.role == self.Role.HOST

    @property
    def is_guest(self):
        return self.role == self.Role.GUEST


class UserProfile(models.Model):
    """Additional profile information for users"""

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    date_of_birth = models.DateField(blank=True, null=True)
    nationality = models.CharField(max_length=100, blank=True)
    languages = models.JSONField(default=list, blank=True)
    emergency_contact_name = models.CharField(max_length=100, blank=True)
    emergency_contact_phone = models.CharField(max_length=20, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"
