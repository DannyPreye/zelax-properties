from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status

User = get_user_model()


class UserModelTest(TestCase):
    """Test User model"""

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
            role=User.Role.GUEST,
        )

    def test_user_creation(self):
        """Test user creation"""
        self.assertEqual(self.user.username, "testuser")
        self.assertEqual(self.user.email, "test@example.com")
        self.assertTrue(self.user.is_guest)

    def test_user_is_host(self):
        """Test host role"""
        self.user.role = User.Role.HOST
        self.user.save()
        self.assertTrue(self.user.is_host)


class UserRegistrationTest(TestCase):
    """Test user registration API"""

    def setUp(self):
        self.client = APIClient()

    def test_user_registration(self):
        """Test user registration endpoint"""
        data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "testpass123",
            "password2": "testpass123",
            "role": "guest",
        }
        response = self.client.post("/api/auth/register/", data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("tokens", response.data)
