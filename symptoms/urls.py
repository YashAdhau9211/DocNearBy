# backend/symptoms/urls.py

from django.urls import path
from .views import SymptomAnalysisView

urlpatterns = [
    # Route POST requests to /api/symptom-analysis/ to the view
    path('symptom-analysis/', SymptomAnalysisView.as_view(), name='symptom-analysis'),
]