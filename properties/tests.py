from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import Property, PropertyPhoto, Availability

User = get_user_model()


class PropertyModelTest(TestCase):
    """Test Property model"""

    def setUp(self):
        self.host = User.objects.create_user(
            username="host",
            email="host@example.com",
            password="testpass123",
            role=User.Role.HOST,
        )
        self.property = Property.objects.create(
            title="Test Property",
            description="Test Description",
            property_type=Property.PropertyType.APARTMENT,
            host=self.host,
            address="123 Test St",
            city="Test City",
            country="Test Country",
            latitude=6.5244,
            longitude=3.3792,
            base_price=100.00,
            max_guests=4,
            bedrooms=2,
            beds=2,
            bathrooms=1.0,
        )

    def test_property_creation(self):
        """Test property creation"""
        self.assertEqual(self.property.title, "Test Property")
        self.assertEqual(self.property.host, self.host)
        self.assertIsNotNone(self.property.latitude)
        self.assertIsNotNone(self.property.longitude)

    def test_property_price_calculation(self):
        """Test property price fields"""
        self.assertEqual(self.property.base_price, 100.00)
