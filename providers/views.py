# backend/providers/views.py

from rest_framework import viewsets, permissions, filters, mixins
from rest_framework.authentication import TokenAuthentication, SessionAuthentication
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.response import Response # Import Response
from .models import Provider
from .serializers import ProviderSerializer
from utils.geolocation import haversine
from decimal import Decimal, InvalidOperation

class ProviderViewSet(viewsets.ModelViewSet):
    serializer_class = ProviderSerializer
    authentication_classes = [TokenAuthentication, SessionAuthentication]

    # Ordering: Define fields Django's ORM can handle directly
    ordering_fields = ['name', 'updated_at']
    ordering = ['name'] # Default ordering

    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter # Handles 'name', 'updated_at' ordering
    ]
    filterset_fields = [
        'city', 'state_province', 'provider_type', 'languages_spoken', 'is_verified',
    ]
    search_fields = [
        'name', 'specialization', 'services_offered', 'city', 'address_line1',
    ]

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [permissions.AllowAny]
        else:
            permission_classes = [permissions.IsAdminUser]
        return [permission() for permission in permission_classes]

    # --- SIMPLIFIED get_queryset ---
    def get_queryset(self):
        """
        Returns the base QuerySet. Standard filters will be applied later.
        Distance calculation is handled in the list method.
        """
        # Start with base QuerySet, filtering out providers without coordinates
        # as they cannot be used for distance calculation anyway.
        queryset = Provider.objects.filter(latitude__isnull=False, longitude__isnull=False)

        # Optional: Apply a default filter like is_verified=True if desired for all list views
        # queryset = queryset.filter(is_verified=True)

        return queryset

    # --- OVERRIDDEN list Method ---
    def list(self, request, *args, **kwargs):
        """
        Overrides the default list action to handle distance calculation
        and sorting *after* standard filtering.
        """
        # 1. Apply standard filters (SearchFilter, DjangoFilterBackend, OrderingFilter)
        #    This uses the simplified get_queryset defined above.
        queryset = self.filter_queryset(self.get_queryset())

        # 2. Check for location parameters
        user_lat = request.query_params.get('lat')
        user_lon = request.query_params.get('lon')
        max_distance_km = request.query_params.get('distance_km')
        requested_ordering = request.query_params.get('ordering')

        results_list = [] # This will hold either QuerySet or List after processing

        # 3. Perform distance processing if lat/lon are provided
        if user_lat and user_lon:
            try:
                user_lat_dec = Decimal(user_lat)
                user_lon_dec = Decimal(user_lon)

                # Fetch providers *after* standard filtering
                providers = list(queryset) # Evaluate QuerySet here
                providers_with_distance = []

                for provider in providers:
                    dist = haversine(user_lat_dec, user_lon_dec, provider.latitude, provider.longitude, unit='km')
                    provider.distance = dist # Annotate instance
                    providers_with_distance.append(provider)

                # Filter list by distance
                if max_distance_km:
                    try:
                        max_dist_val = float(max_distance_km)
                        providers_with_distance = [p for p in providers_with_distance if p.distance <= max_dist_val]
                    except (ValueError, TypeError):
                        pass # Ignore invalid distance

                # Sort list by distance if requested
                if requested_ordering == 'distance':
                    providers_with_distance.sort(key=lambda p: p.distance)
                elif requested_ordering == '-distance':
                    providers_with_distance.sort(key=lambda p: p.distance, reverse=True)
                # Else: list retains order from filtered queryset

                results_list = providers_with_distance # Use the processed list

            except (ValueError, TypeError, InvalidOperation):
                # On bad geo input, maybe return empty list or handle differently
                 results_list = [] # Assign empty list instead of queryset.none()
        else:
            # If no lat/lon, use the standard filtered queryset directly
            results_list = queryset

        # 4. Paginate the results (works on both QuerySets and Lists)
        page = self.paginate_queryset(results_list)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        # 5. Serialize and return (if pagination is not enabled)
        serializer = self.get_serializer(results_list, many=True)
        return Response(serializer.data)