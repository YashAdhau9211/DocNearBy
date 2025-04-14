# backend/symptoms/serializers.py

from rest_framework import serializers

class SymptomInputSerializer(serializers.Serializer):
    """
    Validates the incoming list of symptom descriptions.
    """
    symptoms = serializers.ListField(
        child=serializers.CharField(max_length=200, trim_whitespace=True),
        min_length=1,
        help_text="A list of symptom descriptions provided by the user (e.g., ['headache', 'fever', 'sore throat'])"
    )
    # Could add other fields later, like age, gender for more context (Phase 2+)

class SpecialtySuggestionSerializer(serializers.Serializer):
    """
    Represents a suggested specialty.
    """
    # Using name for simplicity, could use an ID if you create a Specialty model later
    specialty_name = serializers.CharField(max_length=100)
    # Could add relevance score later
    # relevance_score = serializers.FloatField(min_value=0, max_value=1)

class SymptomAnalysisResponseSerializer(serializers.Serializer):
    """
    Formats the overall response for the symptom analysis endpoint.
    """
    suggested_specialties = SpecialtySuggestionSerializer(many=True)
    disclaimer = serializers.CharField(read_only=True) # Ensure disclaimer is always included