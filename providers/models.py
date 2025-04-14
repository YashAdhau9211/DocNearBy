# backend/providers/models.py

import uuid
# No longer importing gis_models
from django.db import models
from django.utils.translation import gettext_lazy as _
# from decimal import Decimal # Not needed for model definition, but useful for calculations

class Provider(models.Model):
    """
    Represents a healthcare provider (Doctor, Clinic, Hospital).
    Uses separate latitude/longitude fields instead of PostGIS PointField.
    """
    class ProviderType(models.TextChoices):
        DOCTOR = 'DOCTOR', _('Doctor')
        CLINIC = 'CLINIC', _('Clinic')
        HOSPITAL = 'HOSPITAL', _('Hospital')

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, help_text="Full name of the doctor or facility.")
    provider_type = models.CharField(
        max_length=20,
        choices=ProviderType.choices,
        default=ProviderType.DOCTOR
    )

    # Contact Info
    phone_number = models.CharField(max_length=30, blank=True, help_text="Primary contact phone number.")
    email = models.EmailField(max_length=254, blank=True, null=True, help_text="Contact email address (optional).")
    website = models.URLField(max_length=200, blank=True, null=True, help_text="Provider's website (optional).")

    # Location Info (Address)
    address_line1 = models.CharField(max_length=255, blank=True)
    address_line2 = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True)
    state_province = models.CharField(max_length=100, blank=True, help_text="State or Province")
    postal_code = models.CharField(max_length=20, blank=True)
    country = models.CharField(max_length=100, blank=True, default="USA") # Adjust default as needed

    # --- Geolocation Coordinates (Decimal Fields) ---
    latitude = models.DecimalField(
        max_digits=10,      # Allows for range -90.0000000 to +90.0000000
        decimal_places=7,   # Provides high precision (sub-meter typically)
        blank=True,
        null=True,
        help_text="Latitude coordinate (e.g., 40.7128)"
    )
    longitude = models.DecimalField(
        max_digits=10,      # Allows for range -180.000000 to +180.000000
        decimal_places=7,
        blank=True,
        null=True,
        help_text="Longitude coordinate (e.g., -74.0060)"
    )
    # --- End Geolocation Coordinates ---

    # Specialization, Services, Languages
    specialization = models.CharField(
        max_length=255,
        blank=True,
        help_text="Primary specialty (e.g., Cardiology, General Practice). Comma-separate if multiple for now."
    )
    services_offered = models.TextField(
        blank=True,
        help_text="Description of services offered (e.g., Vaccinations, Check-ups, X-Rays). One per line or comma-separated."
    )
    languages_spoken = models.CharField(
        max_length=255,
        blank=True,
        default="English",
        help_text="Languages spoken by staff (e.g., English, Spanish, French). Comma-separate."
    )

    # Operating Hours
    operating_hours = models.TextField(
        blank=True,
        help_text="General operating hours (e.g., Mon-Fri 9am-5pm, Sat 10am-1pm)."
    )

    # Verification Status
    is_verified = models.BooleanField(
        default=False,
        help_text="Indicates if the provider's information has been verified by the platform."
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.get_provider_type_display()})"

    class Meta:
        # Updated indexes: Removed GistIndex, added index for lat/lon
        indexes = [
            models.Index(fields=['latitude', 'longitude']), # Index for coordinate lookups
            models.Index(fields=['city', 'state_province']), # Index for filtering by area
            models.Index(fields=['is_verified']), # Index for filtering verified providers
        ]