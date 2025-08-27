# alx_travel_app_0x03

## Milestone 5: Setting Up Background Jobs for Email Notifications

## Background Tasks with Celery + RabbitMQ

- Celery is configured in `alx_travel_app/celery.py`
- Booking confirmation emails are sent asynchronously via Celery task in `listings/tasks.py`
- Triggered automatically when a booking is created (`BookingViewSet.perform_create`)
