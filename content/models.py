# backend/content/models.py
import uuid
from django.db import models

class ContentCategory(models.TextChoices):
    FIRST_AID = 'FIRST_AID', 'First Aid'
    SPECIALTY_INFO = 'SPECIALTY_INFO', 'Specialty Information'
    # Add more later if needed

class ContentEntry(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, help_text="URL-friendly identifier")
    category = models.CharField(max_length=50, choices=ContentCategory.choices)
    body = models.TextField(help_text="The main content (HTML or Markdown potentially)")
    last_updated = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['category', 'title']
        verbose_name_plural = "Content Entries" # Fix admin display

    def __str__(self):
        return f"[{self.get_category_display()}] {self.title}"