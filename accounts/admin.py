from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, UserProfile


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Admin interface for User model"""

    list_display = [
        "username",
        "email",
        "role",
        "email_verified",
        "identity_verified",
        "is_active",
        "date_joined",
    ]
    list_filter = ["role", "email_verified", "identity_verified", "is_active"]
    fieldsets = BaseUserAdmin.fieldsets + (
        (
            "Additional Info",
            {
                "fields": (
                    "role",
                    "phone",
                    "email_verified",
                    "identity_verified",
                    "profile_photo",
                    "bio",
                )
            },
        ),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        (
            "Additional Info",
            {
                "fields": (
                    "role",
                    "phone",
                    "email_verified",
                    "identity_verified",
                    "profile_photo",
                    "bio",
                )
            },
        ),
    )


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """Admin interface for UserProfile model"""

    list_display = ["user", "nationality", "date_of_birth"]
    search_fields = ["user__username", "user__email", "nationality"]
