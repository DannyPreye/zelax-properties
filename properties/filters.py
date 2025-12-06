import django_filters
from django.db import models
from .models import Property


class PropertyFilter(django_filters.FilterSet):
    """Filter for property listings"""

    # Location filters
    city = django_filters.CharFilter(field_name="city", lookup_expr="icontains")
    country = django_filters.CharFilter(field_name="country", lookup_expr="icontains")

    # Price filters
    min_price = django_filters.NumberFilter(field_name="base_price", lookup_expr="gte")
    max_price = django_filters.NumberFilter(field_name="base_price", lookup_expr="lte")

    # Property type filter
    property_type = django_filters.ChoiceFilter(
        choices=Property.PropertyType.choices
    )

    # Capacity filters
    min_guests = django_filters.NumberFilter(
        field_name="max_guests", lookup_expr="gte"
    )
    bedrooms = django_filters.NumberFilter(field_name="bedrooms")
    beds = django_filters.NumberFilter(field_name="beds")
    bathrooms = django_filters.NumberFilter(field_name="bathrooms")

    # Status filter
    status = django_filters.ChoiceFilter(choices=Property.PropertyStatus.choices)

    # Amenities filter (check if amenity exists in JSON field)
    has_wifi = django_filters.BooleanFilter(
        field_name="amenities", method="filter_amenity"
    )
    has_parking = django_filters.BooleanFilter(
        field_name="amenities", method="filter_amenity"
    )
    has_pool = django_filters.BooleanFilter(
        field_name="amenities", method="filter_amenity"
    )
    has_kitchen = django_filters.BooleanFilter(
        field_name="amenities", method="filter_amenity"
    )
    has_ac = django_filters.BooleanFilter(
        field_name="amenities", method="filter_amenity"
    )

    # Date availability filter
    check_in = django_filters.DateFilter(method="filter_available_dates")
    check_out = django_filters.DateFilter(method="filter_available_dates")

    # Geographic search
    latitude = django_filters.NumberFilter(method="filter_nearby")
    longitude = django_filters.NumberFilter(method="filter_nearby")
    radius_km = django_filters.NumberFilter(method="filter_nearby", required=False)

    # Search
    search = django_filters.CharFilter(method="filter_search")

    class Meta:
        model = Property
        fields = [
            "city",
            "country",
            "property_type",
            "min_price",
            "max_price",
            "min_guests",
            "bedrooms",
            "beds",
            "bathrooms",
            "status",
        ]

    def filter_amenity(self, queryset, name, value):
        """Filter by amenity in JSON field"""
        if value:
            amenity_name = name.replace("has_", "")
            return queryset.filter(**{f"amenities__{amenity_name}": True})
        return queryset

    def filter_available_dates(self, queryset, name, value):
        """Filter properties available for given dates"""
        from datetime import timedelta
        from .models import Availability, BlockedDate

        if not value:
            return queryset

        # Check availability calendar
        if name == "check_in":
            # Properties available on check-in date
            available_properties = Availability.objects.filter(
                date=value, is_available=True
            ).values_list("property_id", flat=True)
            queryset = queryset.filter(id__in=available_properties)

        elif name == "check_out":
            # Properties available on check-out date
            available_properties = Availability.objects.filter(
                date=value, is_available=True
            ).values_list("property_id", flat=True)
            queryset = queryset.filter(id__in=available_properties)

        # Check blocked dates
        blocked_properties = BlockedDate.objects.filter(
            start_date__lte=value, end_date__gte=value
        ).values_list("property_id", flat=True)
        queryset = queryset.exclude(id__in=blocked_properties)

        return queryset

    def filter_nearby(self, queryset, name, value):
        """Filter properties within radius of given coordinates"""
        latitude = self.data.get("latitude")
        longitude = self.data.get("longitude")
        radius_km = float(self.data.get("radius_km", 10))

        if latitude and longitude:
            # Use approximate distance calculation using bounding box
            # For more accurate results, consider using PostGIS or a geopy library
            from math import radians, cos

            lat = float(latitude)
            lon = float(longitude)

            # Convert radius from km to degrees (approximate)
            # 1 degree latitude ≈ 111 km
            lat_range = radius_km / 111.0
            # Longitude range depends on latitude
            lon_range = radius_km / (111.0 * cos(radians(lat)))

            queryset = queryset.filter(
                latitude__gte=lat - lat_range,
                latitude__lte=lat + lat_range,
                longitude__gte=lon - lon_range,
                longitude__lte=lon + lon_range,
            )
        return queryset

    def filter_search(self, queryset, name, value):
        """Search in title, description, city, country"""
        return queryset.filter(
            models.Q(title__icontains=value)
            | models.Q(description__icontains=value)
            | models.Q(city__icontains=value)
            | models.Q(country__icontains=value)
        )

