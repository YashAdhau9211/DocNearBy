# backend/content/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ContentViewSet

router = DefaultRouter()
# Register the ContentViewSet. URL prefix will be 'content'.
# Use 'slug' as the lookup in the generated URL patterns.
router.register(r'content', ContentViewSet, basename='content')

urlpatterns = [
    path('', include(router.urls)),
]