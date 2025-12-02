from rest_framework import viewsets, generics
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Avg, Count
from accounts.models import User
from properties.models import Property
from .models import Review
from .serializers import ReviewSerializer, ReviewCreateSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    """ViewSet for review operations"""

    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Filter reviews based on visibility"""
        queryset = Review.objects.filter(is_visible=True).select_related(
            "reviewer", "reviewee", "property", "booking"
        )
        return queryset

    def get_serializer_class(self):
        if self.action == "create":
            return ReviewCreateSerializer
        return ReviewSerializer

    def get_permissions(self):
        """Set permissions based on action"""
        if self.action == "create":
            return [IsAuthenticated()]
        return [AllowAny()]

    def perform_create(self, serializer):
        """Create review with reviewer set to current user"""
        serializer.save(reviewer=self.request.user)


class PropertyReviewsView(generics.ListAPIView):
    """View for getting reviews for a specific property"""

    serializer_class = ReviewSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        property_id = self.kwargs["property_id"]
        return Review.objects.filter(
            property_id=property_id,
            review_type=Review.ReviewType.GUEST_TO_PROPERTY,
            is_visible=True,
        ).select_related("reviewer", "property")

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)

        # Calculate average ratings
        ratings = queryset.aggregate(
            avg_rating=Avg("rating"),
            avg_cleanliness=Avg("cleanliness"),
            avg_accuracy=Avg("accuracy"),
            avg_communication=Avg("communication"),
            avg_location=Avg("location"),
            avg_value=Avg("value"),
            total_reviews=Count("id"),
        )

        return Response(
            {
                "reviews": serializer.data,
                "statistics": {
                    "average_rating": round(ratings["avg_rating"] or 0, 2),
                    "average_cleanliness": round(ratings["avg_cleanliness"] or 0, 2),
                    "average_accuracy": round(ratings["avg_accuracy"] or 0, 2),
                    "average_communication": round(
                        ratings["avg_communication"] or 0, 2
                    ),
                    "average_location": round(ratings["avg_location"] or 0, 2),
                    "average_value": round(ratings["avg_value"] or 0, 2),
                    "total_reviews": ratings["total_reviews"],
                },
            }
        )


class UserReviewsView(generics.ListAPIView):
    """View for getting reviews for a specific user"""

    serializer_class = ReviewSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        user_id = self.kwargs["user_id"]
        return Review.objects.filter(
            reviewee_id=user_id, is_visible=True
        ).select_related("reviewer", "reviewee", "property")
