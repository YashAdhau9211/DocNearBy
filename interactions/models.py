# backend/interactions/models.py
import uuid
from django.conf import settings # Use settings.AUTH_USER_MODEL
from django.db import models
# Import Provider model correctly based on app structure
from providers.models import Provider

class Favorite(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # Reference the User model defined in settings.AUTH_USER_MODEL
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='favorites'
    )
    # Reference the Provider model from the 'providers' app
    provider = models.ForeignKey(
        Provider,
        on_delete=models.CASCADE,
        related_name='favorited_by'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'provider')
        ordering = ['-created_at']

    def __str__(self):
        # Use user.username (or another field if you change User model)
        return f"{self.user.username} favorites {self.provider.name}"

# Add Review model here later (Phase 2)
# class Review(models.Model): ...