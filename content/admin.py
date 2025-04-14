# backend/content/admin.py
from django.contrib import admin
from .models import ContentEntry

@admin.register(ContentEntry)
class ContentEntryAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'slug', 'last_updated')
    list_filter = ('category',)
    search_fields = ('title', 'body')
    # Automatically create slug from title (ensure title is unique enough)
    prepopulated_fields = {'slug': ('title',)}