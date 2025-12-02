from django.test import TestCase
from django.contrib.auth import get_user_model
from datetime import date, timedelta
from properties.models import Property
from .models import Booking

User = get_user_model()


class BookingModelTest(TestCase):
    """Test Booking model"""

    def setUp(self):
        self.host = User.objects.create_user(
            username="host",
            email="host@example.com",
            password="testpass123",
            role=User.Role.HOST,
        )
        self.guest = User.objects.create_user(
            username="guest",
            email="guest@example.com",
            password="testpass123",
            role=User.Role.GUEST,
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
        self.check_in = date.today() + timedelta(days=7)
        self.check_out = date.today() + timedelta(days=10)

    def test_booking_creation(self):
        """Test booking creation"""
        booking = Booking.objects.create(
            property_obj=self.property,
            guest=self.guest,
            check_in=self.check_in,
            check_out=self.check_out,
            guest_count=2,
        )
        self.assertEqual(booking.property_obj, self.property)
        self.assertEqual(booking.guest, self.guest)
        self.assertEqual(booking.nights, 3)

    def test_booking_price_calculation(self):
        """Test booking price calculation"""
        booking = Booking.objects.create(
            property_obj=self.property,
            guest=self.guest,
            check_in=self.check_in,
            check_out=self.check_out,
            guest_count=2,
        )
        # Base price should be 100 * 3 nights = 300
        self.assertEqual(booking.base_price, 300.00)
