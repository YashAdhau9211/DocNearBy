# backend/symptoms/views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
import ollama
import re
import requests # Import requests explicitly for ConnectionError handling

from .serializers import (
    SymptomInputSerializer,
    SymptomAnalysisResponseSerializer,
)

# --- Configuration ---
# Use the exact model name provided by the user
OLLAMA_MODEL_NAME = 'deepseek-r1:1.5b' # <<< Confirmed Model Name
OLLAMA_API_BASE_URL = 'http://localhost:11434'

ANALYSIS_DISCLAIMER = "This suggestion is based on an AI model and is for informational purposes only to help you find a relevant doctor specialty. It is NOT a medical diagnosis. Please consult a qualified healthcare professional for any health concerns. If you are experiencing a medical emergency, call your local emergency number immediately."
# --- ---

class SymptomAnalysisView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = SymptomInputSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        symptoms_list = serializer.validated_data['symptoms']
        symptoms_string = ", ".join(symptoms_list).lower()

        # --- Refined Prompt ---
        prompt = (
            f"User symptoms: {symptoms_string}. "
            f"Task: Suggest relevant medical specialties. "
            f"Output format requirements: Respond ONLY with a single line containing a comma-separated list of 1 to 5 relevant medical specialty names. "
            f"Strictly NO explanations, NO apologies, NO markdown formatting (like bullets or numbers), NO introductory phrases, NO concluding sentences, NO XML-like tags (like <think>). " # Added No XML tags instruction
            f"Example of desired output ONLY: Cardiologist, Pulmonologist, General Practice"
        )
        # --- ---

        processed_specialties_list = []
        error_message = None
        status_code = status.HTTP_200_OK

        try:
            client = ollama.Client(host=OLLAMA_API_BASE_URL)
            response = client.chat(
                model=OLLAMA_MODEL_NAME, # Uses the updated model name
                messages=[{'role': 'user', 'content': prompt}],
                # options={'temperature': 0.1} # Lower temp might help consistency
            )
            raw_suggestions = response['message']['content'].strip()
            print(f"\nDEBUG: Raw Ollama Response ({OLLAMA_MODEL_NAME}):\n---\n{raw_suggestions}\n---\n")

            # --- UPDATED Robust Parsing Logic ---
            if raw_suggestions:
                # 1. REMOVE <think> block FIRST
                cleaned_text = re.sub(r'<think>.*?</think>', '', raw_suggestions, flags=re.DOTALL | re.IGNORECASE).strip()
                print(f"DEBUG: Text after removing <think> block:\n---\n{cleaned_text}\n---") # Debug print

                # 2. Attempt to isolate the core list by removing common prefixes/suffixes (apply to cleaned_text)
                cleaned_text = re.sub(r'^(Okay|Sure|Here|Based on).*?:\s*', '', cleaned_text, flags=re.IGNORECASE | re.DOTALL).strip()
                cleaned_text = re.sub(r'\s*Remember, I am an AI.*$', '', cleaned_text, flags=re.IGNORECASE | re.DOTALL).strip()
                cleaned_text = re.sub(r'\s*Please consult.*$', '', cleaned_text, flags=re.IGNORECASE | re.DOTALL).strip()
                # Try removing other potential XML/instruction tags if they appear
                cleaned_text = re.sub(r'<[^>]+>', '', cleaned_text).strip() # Remove any remaining simple tags
                # Try to keep only the first line if multiple lines still exist
                cleaned_text = cleaned_text.splitlines()[0] if cleaned_text.strip() else ""
                cleaned_text = cleaned_text.rstrip('.').strip()

                print(f"DEBUG: Text after general cleaning:\n---\n{cleaned_text}\n---") # Debug print

                # 3. Split potential items by comma
                potential_items = re.split(r'\s*,\s*', cleaned_text) # Split by comma
                unique_specialties = set()

                # 4. Clean and validate each item
                for item in potential_items:
                    # Remove list markers (numbers, bullets) and leading whitespace
                    cleaned_item = re.sub(r'^\s*[\d\.\*\-]+\s*', '', item.strip())
                    # Remove parenthetical explanations (e.g., "Cardiologist (for heart)")
                    cleaned_item = re.sub(r'\s*\([^)]*\)\s*$', '', cleaned_item)
                    # Remove trailing punctuation (like periods if they survived)
                    cleaned_item = cleaned_item.rstrip('.').strip()

                    # Validate the cleaned item
                    if cleaned_item and len(cleaned_item) <= 100:
                        unique_specialties.add(cleaned_item.title()) # Title case
                    elif cleaned_item:
                        print(f"DEBUG: Skipping specialty '{cleaned_item}' (length > 100 or invalid)")

                # 5. Convert set to the desired list format, applying limit
                processed_specialties_list = [{'specialty_name': spec} for spec in list(unique_specialties)[:5]]

                print(f"DEBUG: Final Processed Specialties: {processed_specialties_list}") # Final check
            # --- End UPDATED Robust Parsing Logic ---

        except ollama.ResponseError as e:
            print(f"Ollama API Error: {e.error}")
            error_message = f"Error communicating with the analysis model: {e.status_code}"
            if "model" in e.error.lower() and "not found" in e.error.lower():
                 error_message = f"Model '{OLLAMA_MODEL_NAME}' not found locally. Please ensure it's pulled via Ollama."
                 status_code = status.HTTP_404_NOT_FOUND
            else:
                status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        except requests.exceptions.ConnectionError as e:
             print(f"Ollama Connection Error: {e}")
             error_message = "Could not connect to the symptom analysis service."
             status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        except Exception as e:
            # Add traceback for debugging unexpected errors
            import traceback
            print(f"Unexpected error during symptom analysis: {e}")
            traceback.print_exc() # Print detailed traceback
            error_message = "An unexpected error occurred during analysis."
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

        # --- Prepare Response ---
        response_data_dict = {
                'suggested_specialties': processed_specialties_list,
                'disclaimer': ANALYSIS_DISCLAIMER
            }

        if error_message:
            response_data_dict['error'] = error_message
            return Response(response_data_dict, status=status_code)
        else:
            # Validate final structure before sending
            response_serializer = SymptomAnalysisResponseSerializer(data=response_data_dict)
            if not response_serializer.is_valid():
                 print(f"ERROR: Final response serialization failed: {response_serializer.errors}")
                 return Response(
                     {"error": "Failed to format the analysis response.", "details": response_serializer.errors},
                     status=status.HTTP_500_INTERNAL_SERVER_ERROR
                 )
            # Return validated data on success
            return Response(response_serializer.validated_data, status=status.HTTP_200_OK)