from rest_framework import serializers
from .models import Provider

class ProviderSerializer(serializers.ModelSerializer):
    """
    Serializer for the Provider model.
    """
    # Optionally add read_only fields or customize representation here
    # For now, we'll serialize most fields defined in the model.

    class Meta:
        model = Provider
        # List the fields you want to include in the API output
        fields = [
            'id',
            'name',
            'provider_type',
            'phone_number',
            'email',
            'website',
            'address_line1',
            'address_line2',
            'city',
            'state_province',
            'postal_code',
            'country',
            'latitude',        # Include the lat/lon fields
            'longitude',
            # 'distance',
            'specialization',
            'services_offered',
            'languages_spoken',
            'operating_hours',
            'is_verified',
            # 'created_at',    # Usually excluded unless needed
            # 'updated_at',    # Usually excluded unless needed
        ]
        # Example: Make certain fields read-only if providers shouldn't update them via this serializer
        # read_only_fields = ['is_verified']
