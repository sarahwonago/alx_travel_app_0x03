from rest_framework import viewsets
from .models import Listing, Booking, Payment
from .serializers import ListingSerializer, BookingSerializer
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from .tasks import send_booking_confirmation_email

import os
import requests
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from dotenv import load_dotenv

load_dotenv()

CHAPA_SECRET_KEY = os.getenv("CHAPA_SECRET_KEY")
CHAPA_BASE_URL = "https://api.chapa.co/v1"


class ListingViewSet(viewsets.ModelViewSet):
    queryset = Listing.objects.all()
    serializer_class = ListingSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        booking = serializer.save(guest=self.request.user)
        # Trigger background task
        send_booking_confirmation_email.delay(
            booking.guest.email,
            booking.listing.title,
            booking.check_in.strftime("%Y-%m-%d"),
            booking.check_out.strftime("%Y-%m-%d"),
        )


class InitiatePaymentView(APIView):
    """Initiate payment with Chapa API."""

    def post(self, request, booking_id):
        booking = get_object_or_404(Booking, id=booking_id)
        amount = booking.listing.price_per_night

        payment = Payment.objects.create(booking=booking, amount=amount)

        payload = {
            "amount": str(amount),
            "currency": "ETB",
            "email": booking.guest.email,
            "first_name": booking.guest.first_name,
            "last_name": booking.guest.last_name,
            "tx_ref": str(payment.transaction_id),
            "callback_url": request.build_absolute_uri(
                f"/verify-payment/{payment.transaction_id}/"
            ),
            "return_url": "http://localhost:8000/payment-success/",
        }

        headers = {"Authorization": f"Bearer {CHAPA_SECRET_KEY}"}

        r = requests.post(
            f"{CHAPA_BASE_URL}/transaction/initialize", json=payload, headers=headers
        )
        resp_data = r.json()

        if resp_data.get("status") == "success":
            payment.chapa_tx_ref = payload["tx_ref"]
            payment.save()
            return Response(resp_data, status=status.HTTP_200_OK)
        else:
            payment.status = "Failed"
            payment.save()
            return Response(resp_data, status=status.HTTP_400_BAD_REQUEST)


class VerifyPaymentView(APIView):
    """Verify payment with Chapa API."""

    def get(self, request, transaction_id):
        payment = get_object_or_404(Payment, transaction_id=transaction_id)
        headers = {"Authorization": f"Bearer {CHAPA_SECRET_KEY}"}

        r = requests.get(
            f"{CHAPA_BASE_URL}/transaction/verify/{payment.chapa_tx_ref}",
            headers=headers,
        )
        resp_data = r.json()

        if (
            resp_data.get("status") == "success"
            and resp_data["data"]["status"] == "success"
        ):
            payment.status = "Completed"
        else:
            payment.status = "Failed"

        payment.save()
        return Response({"payment_status": payment.status}, status=status.HTTP_200_OK)
