# backend/providers/admin.py

from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.http import urlencode
from .models import Provider

@admin.register(Provider)
class ProviderAdmin(admin.ModelAdmin):
    # --- List View Configuration ---

    list_display = (
        'name',
        'provider_type',
        'city',
        'state_province',
        'is_verified',
        'specialization_display', # Display specialization cleanly
        'updated_at',
        'id', # Useful for reference
    )
    list_filter = (
        'is_verified',          # Primary filter
        'provider_type',
        'state_province',       # Filter by location hierarchy
        'city',
        'languages_spoken',     # Can filter by language if needed (simple text match)
        'country',              # Useful if expanding internationally
    )
    search_fields = (
        'id',                   # Allow searching by UUID
        'name',
        'specialization',
        'services_offered',
        'city',
        'state_province',
        'postal_code',
        'phone_number',
        'email',
    )
    ordering = ('-updated_at', 'name') # Show recently updated first, then by name
    list_per_page = 25 # Adjust as needed
    date_hierarchy = 'updated_at' # Adds date drill-down navigation

    # --- Detail/Change View Configuration ---

    readonly_fields = (
        'id',                   # Cannot change primary key
        'created_at',
        'updated_at',
        'map_link_display',     # Display link to map based on coordinates
    )

    fieldsets = (
        (None, { # Basic Info Section
            'fields': ('name', 'provider_type', 'is_verified')
        }),
        ('Contact Information', {
            'fields': ('phone_number', 'email', 'website')
        }),
        ('Location Details', {
            'fields': (
                'address_line1', 'address_line2', 'city', 'state_province',
                'postal_code', 'country',
                ('latitude', 'longitude'), # Display lat/lon side-by-side
                'map_link_display'         # Show the map link here too
            ),
            # 'classes': ('collapse',), # Optionally make section collapsible
        }),
        ('Clinical & Service Details', {
            'fields': ('specialization', 'services_offered', 'languages_spoken')
        }),
        ('Operational Information', {
            'fields': ('operating_hours',)
        }),
        ('Metadata', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',), # Collapse metadata by default
        }),
    )

    # --- Custom Actions ---

    actions = ['mark_verified', 'mark_unverified']

    @admin.action(description='Mark selected providers as VERIFIED')
    def mark_verified(self, request, queryset):
        updated_count = queryset.update(is_verified=True)
        self.message_user(
            request,
            f'{updated_count} provider(s) were successfully marked as verified.'
        )

    @admin.action(description='Mark selected providers as UNVERIFIED')
    def mark_unverified(self, request, queryset):
        updated_count = queryset.update(is_verified=False)
        self.message_user(
            request,
            f'{updated_count} provider(s) were successfully marked as unverified.'
        )

    # --- Custom Display Methods ---

    @admin.display(description='Specialization(s)')
    def specialization_display(self, obj):
        # Simple display helper, could be enhanced later
        return obj.specialization or '-'

    @admin.display(description='Map Link')
    def map_link_display(self, obj):
        # Creates a link to Google Maps using stored coordinates
        if obj.latitude and obj.longitude:
            lat, lon = obj.latitude, obj.longitude
            google_maps_url = f"https://www.google.com/maps/search/?api=1&query={lat},{lon}"
            # You could also use: f"https://www.google.com/maps/@?api=1&map_action=map¢er={lat},{lon}&zoom=15"
            return format_html('<a href="{}" target="_blank">View on Google Maps</a>', google_maps_url)
        return "N/A (Missing Coordinates)"

# --- You might also want to register other models ---
# from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
# from users.models import User # Assuming your custom user is in 'users' app

# If you have a custom user model, register it:
# class UserAdmin(BaseUserAdmin):
#     # Add customization if needed
#     pass
# admin.site.register(User, UserAdmin)

# Register Favorite and Content models for admin management
# from interactions.models import Favorite
# from content.models import ContentEntry

# @admin.register(Favorite)
# class FavoriteAdmin(admin.ModelAdmin):
#     list_display = ('user', 'provider', 'created_at')
#     list_filter = ('created_at',)
#     search_fields = ('user__username', 'provider__name')
#     raw_id_fields = ('user', 'provider') # Better UI for selecting user/provider

# @admin.register(ContentEntry)
# class ContentEntryAdmin(admin.ModelAdmin):
#     list_display = ('title', 'category', 'slug', 'last_updated')
#     list_filter = ('category',)
#     search_fields = ('title', 'body')
#     prepopulated_fields = {'slug': ('title',)} # Auto-generate slug from title