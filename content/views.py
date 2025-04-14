# backend/content/views.py

from rest_framework import viewsets, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import ContentEntry
from .serializers import ContentEntrySerializer

class ContentViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint to view informational content like First-Aid guides
    and Medical Specialty explanations.

    Provides `list` and `retrieve` actions.
    Allows filtering by `category` (e.g., ?category=FIRST_AID).
    Allows searching title and body content (?search=...).
    Allows retrieving by slug using lookup_field.
    """
    serializer_class = ContentEntrySerializer
    permission_classes = [permissions.AllowAny] # Content is publicly viewable
    queryset = ContentEntry.objects.all().order_by('category', 'title')

    # --- Filtering and Searching ---
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ['category'] # Allow filtering by ?category=FIRST_AID or ?category=SPECIALTY_INFO
    search_fields = ['title', 'body'] # Allow searching using ?search=...
    ordering_fields = ['title', 'last_updated', 'category']
    ordering = ['category', 'title'] # Default ordering

    # --- Use 'slug' for Detail View Lookups ---
    # Allows URLs like /api/content/first-aid-slug/ instead of /api/content/uuid/
    lookup_field = 'slug'