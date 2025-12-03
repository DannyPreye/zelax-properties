from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ReviewViewSet, PropertyReviewsView, UserReviewsView

router = DefaultRouter()
router.register(r"", ReviewViewSet, basename="review")

app_name = "reviews"

urlpatterns = [
    path("", include(router.urls)),
    path("properties/<int:property_id>/", PropertyReviewsView.as_view(), name="property-reviews"),
    path("users/<int:user_id>/", UserReviewsView.as_view(), name="user-reviews"),
]




