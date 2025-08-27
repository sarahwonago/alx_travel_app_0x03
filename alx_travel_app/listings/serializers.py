from rest_framework import serializers
from .models import Listing, Booking


class ListingSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')  # Show owner's username

    class Meta:
        model = Listing
        fields = ['id', 'title', 'description', 'location', 'price_per_night', 'owner', 'created_at']


class BookingSerializer(serializers.ModelSerializer):
    guest = serializers.ReadOnlyField(source='guest.username')  # Show guest's username
    listing_title = serializers.ReadOnlyField(source='listing.title')  

    class Meta:
        model = Booking
        fields = ['id', 'listing', 'listing_title', 'guest', 'check_in', 'check_out', 'created_at']
        read_only_fields = ['guest', 'created_at']
