from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import WishlistViewSet

router = DefaultRouter()
router.register(r"", WishlistViewSet, basename="wishlist")

app_name = "wishlists"

urlpatterns = [
    path("", include(router.urls)),
]




