from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
import uuid

User = get_user_model()


class Listing(models.Model):
    """A property listed for rent or booking."""

    title = models.CharField(max_length=255)
    description = models.TextField()
    location = models.CharField(max_length=255)
    price_per_night = models.DecimalField(max_digits=10, decimal_places=2)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="listings")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Booking(models.Model):
    """A booking made by a user for a listing."""

    listing = models.ForeignKey(
        Listing, on_delete=models.CASCADE, related_name="bookings"
    )
    guest = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bookings")
    check_in = models.DateField()
    check_out = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=models.Q(check_out__gt=models.F("check_in")),
                name="check_out_after_check_in",
            )
        ]

    def __str__(self):
        return f"{self.guest} booking {self.listing} from {self.check_in} to {self.check_out}"


class Review(models.Model):
    """A review left by a guest after a booking."""

    listing = models.ForeignKey(
        Listing, on_delete=models.CASCADE, related_name="reviews"
    )
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reviews")
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("listing", "reviewer")  # One review per user per listing

    def __str__(self):
        return f"{self.reviewer} rated {self.listing} ({self.rating})"


class Payment(models.Model):
    """Payment information for a booking."""

    STATUS_CHOICES = [
        ("Pending", "Pending"),
        ("Completed", "Completed"),
        ("Failed", "Failed"),
    ]

    booking = models.OneToOneField(
        Booking, on_delete=models.CASCADE, related_name="payment"
    )
    transaction_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    chapa_tx_ref = models.CharField(max_length=255, blank=True, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="Pending")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Payment {self.transaction_id} - {self.status}"
