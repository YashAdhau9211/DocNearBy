# backend/interactions/serializers.py

from rest_framework import serializers
from .models import Favorite
from providers.models import Provider

# A simple serializer to represent basic Provider info within the Favorite list
class NestedProviderSerializer(serializers.ModelSerializer):
    """
    Read-only serializer for basic Provider details nested within Favorite.
    """
    class Meta:
        model = Provider
        fields = [
            'id',
            'name',
            'provider_type',
            'specialization', # Include specialization
            'city',
            'state_province'
        ]
        read_only_fields = fields # Ensure all fields are read-only here


class FavoriteSerializer(serializers.ModelSerializer):
    """
    Serializer for the Favorite model. Handles:
    - Displaying user's favorites with nested provider details (read).
    - Creating a new favorite by accepting a 'provider_id' (write).
    """
    # On read operations (GET), display nested provider details using the dedicated serializer
    provider = NestedProviderSerializer(read_only=True)

    # On write operations (POST), accept the provider's ID.
    # Use 'source' to link this input field back to the 'provider' model field.
    # Use 'write_only=True' so this field is only used for input, not shown in output.
    provider_id = serializers.PrimaryKeyRelatedField(
        queryset=Provider.objects.all(), # Needed for validation by DRF
        source='provider',
        write_only=True,
        help_text="The ID of the provider to favorite."
    )

    # Optionally display user ID (usually not needed as it's implicit)
    # user = serializers.ReadOnlyField(source='user.id')

    class Meta:
        model = Favorite
        # Fields included in the API response (GET)
        fields = [
            'id',           # The favorite record's ID
            'provider',     # Nested provider details (read-only structure)
            'provider_id',  # The ID field used for input (write-only)
            'created_at'    # When the favorite was added
            # 'user'        # Uncomment if you want to explicitly show user ID
        ]
        # Fields that are not directly set by the client when creating/updating
        # Note: 'provider' itself (the nested structure) is implicitly read-only
        # because NestedProviderSerializer has read_only_fields = fields.
        read_only_fields = ['id', 'created_at']

    def create(self, validated_data):
        """
        Override create to automatically set the user based on the request context.
        Also handles potential unique constraint errors gracefully.
        """
        # Extract provider from validated_data (set via provider_id source)
        provider = validated_data.get('provider')
        # Get user from the request context (injected by DRF views)
        user = self.context['request'].user

        # Check if the favorite already exists
        favorite, created = Favorite.objects.get_or_create(
            user=user,
            provider=provider,
            # Defaults aren't needed here as get_or_create handles it
        )

        # If it wasn't created (meaning it already existed), we might want
        # to treat it differently depending on desired API behavior.
        # For now, we just return the existing or newly created favorite.
        return favorite

    # Note: We don't need an update method as users typically only add/remove favorites.