# backend/providers/views.py

from rest_framework import viewsets, permissions
from rest_framework.authentication import TokenAuthentication, SessionAuthentication
from .models import Provider
from .serializers import ProviderSerializer
from django.utils.decorators import method_decorator # Import decorator utility
from django.views.decorators.csrf import csrf_exempt # Import csrf_exempt

class ProviderViewSet(viewsets.ModelViewSet):
    queryset = Provider.objects.all().order_by('name')
    serializer_class = ProviderSerializer
    authentication_classes = [TokenAuthentication, SessionAuthentication]

    def get_permissions(self):
        # ... (permissions logic remains) ...
        if self.action in ['list', 'retrieve']:
            permission_classes = [permissions.AllowAny]
        else:
            permission_classes = [permissions.IsAdminUser]
        return [permission() for permission in permission_classes]

    # --- TEMPORARY DIAGNOSTIC ---
    # Apply csrf_exempt to the dispatch method
    # @method_decorator(csrf_exempt, name='dispatch')
    # def dispatch(self, *args, **kwargs):
    #     return super().dispatch(*args, **kwargs)
    # --------------------------