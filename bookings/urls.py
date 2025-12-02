from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BookingViewSet, PriceCalculationView

router = DefaultRouter()
router.register(r"", BookingViewSet, basename="booking")

app_name = "bookings"

urlpatterns = [
    path("", include(router.urls)),
    path("calculate-price/", PriceCalculationView.as_view(), name="calculate-price"),
]


