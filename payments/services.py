import uuid
import requests
from django.conf import settings
from django.utils import timezone
from .models import Payment, Payout


class PaystackService:
    """Service for Paystack payment integration"""

    def __init__(self):
        self.secret_key = settings.PAYSTACK_SECRET_KEY
        self.public_key = settings.PAYSTACK_PUBLIC_KEY
        self.base_url = "https://api.paystack.co"

    def _get_headers(self):
        """Get headers for Paystack API requests"""
        return {
            "Authorization": f"Bearer {self.secret_key}",
            "Content-Type": "application/json",
        }

    def initialize_transaction(self, email, amount, reference, metadata=None):
        """Initialize Paystack transaction"""
        url = f"{self.base_url}/transaction/initialize"
        data = {
            "email": email,
            "amount": int(amount * 100),  # Convert to kobo (smallest currency unit)
            "reference": reference,
            "metadata": metadata or {},
        }

        response = requests.post(url, json=data, headers=self._get_headers())
        if response.status_code == 200:
            return response.json()
        return None

    def verify_transaction(self, reference):
        """Verify Paystack transaction"""
        url = f"{self.base_url}/transaction/verify/{reference}"
        response = requests.get(url, headers=self._get_headers())
        if response.status_code == 200:
            return response.json()
        return None

    def create_transfer_recipient(self, account_number, bank_code, account_name):
        """Create transfer recipient for payouts"""
        url = f"{self.base_url}/transferrecipient"
        data = {
            "type": "nuban",
            "name": account_name,
            "account_number": account_number,
            "bank_code": bank_code,
            "currency": "NGN",
        }

        response = requests.post(url, json=data, headers=self._get_headers())
        if response.status_code == 201:
            return response.json()
        return None

    def initiate_transfer(self, recipient_code, amount, reference, reason=None):
        """Initiate transfer (payout)"""
        url = f"{self.base_url}/transfer"
        data = {
            "source": "balance",
            "amount": int(amount * 100),  # Convert to kobo
            "recipient": recipient_code,
            "reference": reference,
            "reason": reason or "Payout",
        }

        response = requests.post(url, json=data, headers=self._get_headers())
        if response.status_code == 200:
            return response.json()
        return None


def generate_transaction_reference():
    """Generate unique transaction reference"""
    return f"TXN-{uuid.uuid4().hex[:12].upper()}"


def create_payment(booking, user, amount, currency="NGN"):
    """Create payment record"""
    reference = generate_transaction_reference()
    payment = Payment.objects.create(
        booking=booking,
        user=user,
        amount=amount,
        currency=currency,
        transaction_reference=reference,
    )
    return payment


def create_payout(host, amount, currency="NGN"):
    """Create payout record"""
    reference = generate_transaction_reference()
    payout = Payout.objects.create(
        host=host,
        amount=amount,
        currency=currency,
        transaction_reference=reference,
    )
    return payout




