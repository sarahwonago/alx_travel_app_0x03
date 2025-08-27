from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ListingViewSet,
    BookingViewSet,
    InitiatePaymentView,
    VerifyPaymentView,
)

router = DefaultRouter()
router.register(r"listings", ListingViewSet)
router.register(r"bookings", BookingViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path(
        "initiate-payment/<int:booking_id>/",
        InitiatePaymentView.as_view(),
        name="initiate-payment",
    ),
    path(
        "verify-payment/<uuid:transaction_id>/",
        VerifyPaymentView.as_view(),
        name="verify-payment",
    ),
]
