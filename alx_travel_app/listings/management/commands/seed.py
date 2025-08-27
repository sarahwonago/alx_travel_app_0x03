import random
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from listings.models import Listing

User = get_user_model()

SAMPLE_TITLES = [
    "Cozy Cabin in the Woods",
    "Luxury Downtown Apartment",
    "Beachside Bungalow",
    "Modern Loft",
    "Charming Country House",
    "Quiet Suburban Retreat",
    "Stylish City Studio",
    "Eco-Friendly Treehouse"
]

LOCATIONS = [
    "Nairobi", "Mombasa", "Kisumu", "Nakuru", "Eldoret", "Naivasha"
]

DESCRIPTIONS = [
    "A peaceful escape surrounded by nature.",
    "Perfect location for business or leisure.",
    "Wake up to ocean views every morning.",
    "Open-plan living with artistic flair.",
    "A rustic home with all modern comforts.",
    "Ideal for long stays or weekend getaways."
]

class Command(BaseCommand):
    help = 'Seed the database with sample listings.'

    def handle(self, *args, **kwargs):
        users = User.objects.all()
        if not users.exists():
            self.stdout.write(self.style.ERROR('No users found. Please create users before seeding listings.'))
            return

        for _ in range(20):
            title = random.choice(SAMPLE_TITLES)
            location = random.choice(LOCATIONS)
            description = random.choice(DESCRIPTIONS)
            price = round(random.uniform(30.00, 300.00), 2)
            owner = random.choice(users)

            listing = Listing.objects.create(
                title=title,
                location=location,
                description=description,
                price_per_night=price,
                owner=owner
            )
            self.stdout.write(self.style.SUCCESS(f'Created listing: {listing.title} (${listing.price_per_night})'))

        self.stdout.write(self.style.SUCCESS('Seeding complete.'))
