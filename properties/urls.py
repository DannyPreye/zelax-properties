from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    PropertyViewSet,
    PropertyPhotoViewSet,
    AvailabilityViewSet,
    BlockedDateViewSet,
)

router = DefaultRouter()
router.register(r"", PropertyViewSet, basename="property")

app_name = "properties"

urlpatterns = [
    path("", include(router.urls)),
    # Nested routes for property photos, availability, and blocked dates
    path(
        "<int:property_pk>/photos/",
        PropertyPhotoViewSet.as_view({"get": "list", "post": "create"}),
        name="property-photos",
    ),
    path(
        "<int:property_pk>/photos/<int:pk>/",
        PropertyPhotoViewSet.as_view(
            {"get": "retrieve", "put": "update", "patch": "partial_update", "delete": "destroy"}
        ),
        name="property-photo-detail",
    ),
    path(
        "<int:property_pk>/availability/",
        AvailabilityViewSet.as_view({"get": "list", "post": "create"}),
        name="property-availability",
    ),
    path(
        "<int:property_pk>/availability/<int:pk>/",
        AvailabilityViewSet.as_view(
            {"get": "retrieve", "put": "update", "patch": "partial_update", "delete": "destroy"}
        ),
        name="property-availability-detail",
    ),
    path(
        "<int:property_pk>/blocked-dates/",
        BlockedDateViewSet.as_view({"get": "list", "post": "create"}),
        name="property-blocked-dates",
    ),
    path(
        "<int:property_pk>/blocked-dates/<int:pk>/",
        BlockedDateViewSet.as_view(
            {"get": "retrieve", "put": "update", "patch": "partial_update", "delete": "destroy"}
        ),
        name="property-blocked-date-detail",
    ),
    # Search endpoint
    path("search/", PropertyViewSet.as_view({"get": "list"}), name="property-search"),
]

