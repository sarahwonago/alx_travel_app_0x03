from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings


@shared_task
def send_booking_confirmation_email(to_email, listing_title, check_in, check_out):
    subject = "Booking Confirmation"
    message = (
        f"Your booking for {listing_title} has been confirmed!\n\n"
        f"Check-in: {check_in}\n"
        f"Check-out: {check_out}\n\n"
        "Thank you for booking with us."
    )
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [to_email])
