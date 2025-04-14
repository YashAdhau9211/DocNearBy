"""
URL configuration for docnearby_core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include # Make sure include is imported

urlpatterns = [
    path('admin/', admin.site.urls),
    # Include DRF authentication URLs (login/logout for browsable API)
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    # Include dj-rest-auth URLs (for registration, login, etc.)
    path('api/auth/', include('dj_rest_auth.urls')),
    path('api/auth/registration/', include('dj_rest_auth.registration.urls')), # If using registration

    # --- Include your app's API URLs ---
    path('api/', include('providers.urls')), # Add this line for providers
    path('api/', include('symptoms.urls')),
    # path('api/', include('interactions.urls')),
    path('api/', include('content.urls')),
    # path('api/', include('users.urls')), # Add later for user-specific endpoints
    # path('api/', include('interactions.urls')), # Add later for favorites/reviews
    # path('api/', include('content.urls')), # Add later for content
]
