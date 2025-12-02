# Zelax Properties - Property Rental Platform

A comprehensive property rental platform (Airbnb-like) built with Django REST Framework, featuring user management, property listings, bookings, reviews, messaging, payments (Paystack), and search functionality.

## Features

### Core Features
- **User Management**: Registration, authentication (JWT), profiles with host/guest roles
- **Property Listings**: CRUD operations, multiple photos, amenities, pricing, availability calendar
- **Booking System**: Booking requests, conflict validation, price calculation, cancellation policies
- **Reviews & Ratings**: Two-way reviews (guest-to-property, guest-to-host, host-to-guest)
- **Messaging**: In-app messaging between hosts and guests
- **Wishlists**: Save favorite properties
- **Search & Filtering**: Location-based search, filters (price, type, amenities, dates), geographic search
- **Payment Integration**: Paystack payment processing and host payouts
- **Notifications**: Email notifications via Celery
- **Admin Panel**: Property approval, review moderation, analytics

## Tech Stack

- **Backend**: Django 5.2.8, Django REST Framework
- **Database**: PostgreSQL with PostGIS (for geographic search)
- **Authentication**: JWT (djangorestframework-simplejwt)
- **File Storage**: Cloudinary
- **Payment**: Paystack
- **Task Queue**: Celery with Redis
- **API Documentation**: drf-spectacular (OpenAPI/Swagger)

## Installation

### Prerequisites
- Python 3.8+
- PostgreSQL with PostGIS extension
- Redis (for Celery)

### Setup

1. **Clone the repository**
```bash
git clone <repository-url>
cd property-django
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment variables**
Create a `.env` file in the project root:
```env
# Database
DB_NAME=property_rental
DB_USER=postgres
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432

# Cloudinary
CLOUDINARY_CLOUD_NAME=your_cloud_name
CLOUDINARY_API_KEY=your_api_key
CLOUDINARY_API_SECRET=your_api_secret

# Paystack
PAYSTACK_SECRET_KEY=your_secret_key
PAYSTACK_PUBLIC_KEY=your_public_key

# Celery
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# Email
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your_email@gmail.com
EMAIL_HOST_PASSWORD=your_app_password
DEFAULT_FROM_EMAIL=your_email@gmail.com

# Django Secret Key (generate a new one for production)
SECRET_KEY=your_secret_key
```

5. **Set up PostgreSQL database**
```bash
# Create database
createdb property_rental

# Enable PostGIS extension
psql property_rental -c "CREATE EXTENSION postgis;"
```

6. **Run migrations**
```bash
python manage.py makemigrations
python manage.py migrate
```

7. **Create superuser**
```bash
python manage.py createsuperuser
```

8. **Run development server**
```bash
python manage.py runserver
```

9. **Run Celery worker** (in a separate terminal)
```bash
celery -A config worker -l info
```

## API Documentation

Once the server is running, access the API documentation at:
- Swagger UI: http://localhost:8000/api/docs/
- ReDoc: http://localhost:8000/api/redoc/
- OpenAPI Schema: http://localhost:8000/api/schema/

## API Endpoints

### Authentication
- `POST /api/auth/register/` - User registration
- `POST /api/auth/login/` - Login (get JWT tokens)
- `POST /api/auth/logout/` - Logout (blacklist token)
- `POST /api/auth/refresh-token/` - Refresh access token
- `POST /api/auth/password-reset/` - Request password reset

### Users
- `GET /api/users/profile/` - Get current user profile
- `PUT /api/users/profile/` - Update profile
- `GET /api/users/{id}/` - Get public user profile
- `POST /api/users/verify-email/` - Verify email

### Properties
- `GET /api/properties/` - List properties (with filters)
- `POST /api/properties/` - Create property (host only)
- `GET /api/properties/{id}/` - Property details
- `PUT /api/properties/{id}/` - Update property (owner only)
- `DELETE /api/properties/{id}/` - Delete property (owner only)
- `GET /api/properties/{id}/availability/` - Get availability calendar
- `POST /api/properties/{id}/photos/` - Upload photos
- `GET /api/search/properties/` - Search properties

### Bookings
- `GET /api/bookings/` - List user's bookings
- `POST /api/bookings/` - Create booking request
- `GET /api/bookings/{id}/` - Booking details
- `POST /api/bookings/{id}/confirm/` - Confirm booking (host)
- `POST /api/bookings/{id}/cancel/` - Cancel booking
- `GET /api/bookings/{id}/calculate-price/` - Calculate booking price

### Reviews
- `GET /api/reviews/` - List reviews
- `POST /api/reviews/` - Create review
- `GET /api/reviews/properties/{id}/` - Property reviews
- `GET /api/reviews/users/{id}/` - User reviews

### Messages
- `GET /api/messages/threads/` - List message threads
- `POST /api/messages/threads/` - Create thread
- `GET /api/messages/threads/{id}/messages/` - Get thread messages
- `POST /api/messages/threads/{id}/messages/` - Send message

### Wishlists
- `GET /api/wishlists/` - List wishlists
- `POST /api/wishlists/` - Create wishlist
- `POST /api/wishlists/{id}/properties/{property_id}/` - Add property
- `DELETE /api/wishlists/{id}/properties/{property_id}/` - Remove property

### Payments
- `POST /api/payments/initialize/` - Initialize Paystack payment
- `POST /api/payments/verify/` - Verify payment
- `GET /api/payments/` - Payment history
- `POST /api/payments/payouts/request/` - Request payout (host)

### Notifications
- `GET /api/notifications/` - List notifications
- `POST /api/notifications/{id}/read/` - Mark as read
- `PUT /api/notifications/preferences/` - Update preferences

## Testing

Run tests:
```bash
python manage.py test
```

## Project Structure

```
property-django/
├── accounts/          # User management and authentication
├── properties/        # Property listings and search
├── bookings/          # Booking system
├── reviews/           # Reviews and ratings
├── messaging/         # In-app messaging
├── wishlists/         # Wishlists
├── payments/          # Payment processing (Paystack)
├── notifications/     # Notifications system
├── config/            # Django project settings
└── manage.py
```

## License

This project is licensed under the MIT License.

