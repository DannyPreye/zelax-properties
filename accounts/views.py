from rest_framework import generics, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from .models import UserProfile
from .serializers import (
    UserRegistrationSerializer,
    UserSerializer,
    UserPublicSerializer,
    UserUpdateSerializer,
    PasswordResetSerializer,
    PasswordResetConfirmSerializer,
)
from .permissions import IsOwner

User = get_user_model()


class UserRegistrationView(generics.CreateAPIView):
    """View for user registration"""

    queryset = User.objects.all()
    permission_classes = [AllowAny]
    serializer_class = UserRegistrationSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        access_token = refresh.access_token

        return Response(
            {
                "user": UserSerializer(user).data,
                "tokens": {
                    "refresh": str(refresh),
                    "access": str(access_token),
                },
            },
            status=status.HTTP_201_CREATED,
        )


class UserProfileView(generics.RetrieveUpdateAPIView):
    """View for getting and updating current user profile"""

    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


class UserPublicProfileView(generics.RetrieveAPIView):
    """View for getting public user profile"""

    queryset = User.objects.all()
    serializer_class = UserPublicSerializer
    permission_classes = [AllowAny]
    lookup_field = "id"


class EmailVerificationView(generics.GenericAPIView):
    """View for email verification"""

    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        """Override to return None since this view doesn't use a serializer"""
        return None

    def post(self, request):
        # In a real implementation, you would verify the token sent via email
        # For now, we'll just mark it as verified
        user = request.user
        user.email_verified = True
        user.save()
        return Response(
            {"message": "Email verified successfully"},
            status=status.HTTP_200_OK,
        )


class PasswordResetView(generics.GenericAPIView):
    """View for password reset request"""

    permission_classes = [AllowAny]
    serializer_class = PasswordResetSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"]

        try:
            user = User.objects.get(email=email)
            # In a real implementation, send password reset email
            # For now, just return success
            return Response(
                {"message": "Password reset email sent"},
                status=status.HTTP_200_OK,
            )
        except User.DoesNotExist:
            # Don't reveal if email exists or not
            return Response(
                {"message": "Password reset email sent"},
                status=status.HTTP_200_OK,
            )


class PasswordResetConfirmView(generics.GenericAPIView):
    """View for password reset confirmation"""

    permission_classes = [AllowAny]
    serializer_class = PasswordResetConfirmSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # In a real implementation, verify token and reset password
        # For now, just return success
        return Response(
            {"message": "Password reset successfully"},
            status=status.HTTP_200_OK,
        )
