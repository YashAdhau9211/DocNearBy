# backend/content/serializers.py

from rest_framework import serializers
from .models import ContentEntry

class ContentEntrySerializer(serializers.ModelSerializer):
    """
    Serializer for informational content entries (First-Aid, Specialties).
    """
    # Optionally get the display name for the category choice
    category_display = serializers.CharField(source='get_category_display', read_only=True)

    class Meta:
        model = ContentEntry
        fields = [
            'id',
            'title',
            'slug',         # Useful for fetching specific entries or creating URLs
            'category',     # The raw category value (e.g., 'FIRST_AID')
            'category_display', # The human-readable category name
            'body',         # The main content
            'last_updated',
            # 'created_at' # Usually not needed in response
        ]
        # Make slug read-only if it's auto-generated or set via admin
        read_only_fields = ['id', 'category_display', 'last_updated', 'slug']