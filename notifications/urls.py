from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import NotificationViewSet, NotificationPreferenceView

router = DefaultRouter()
router.register(r"", NotificationViewSet, basename="notification")

app_name = "notifications"

urlpatterns = [
    path("", include(router.urls)),
    path("preferences/", NotificationPreferenceView.as_view(), name="preferences"),
]




