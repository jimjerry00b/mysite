"""
URL configuration for config project.

Routing overview:
  /               -> redirects to the dashboard at /admin/
  /admin/         -> the NiceAdmin dashboard (login required)
  /admin/api-docs/-> interactive API reference (Swagger UI) in the dashboard
  /django-admin/  -> Django's built-in model admin (users, models, etc.)
"""
from django.contrib import admin
from django.urls import include, path
from django.views.generic.base import RedirectView

from api.views import api_docs, dashboard

urlpatterns = [
    # Root redirects to the dashboard. Using pattern_name (not a hardcoded URL)
    # keeps the redirect correct when the app is served under a sub-path
    # (e.g. /mysite/ in production).
    path('', RedirectView.as_view(pattern_name='dashboard', permanent=False)),
    path('admin/', dashboard, name='dashboard'),
    path('admin/api-docs/', api_docs, name='api-docs'),
    path('api/', include('api.urls')),
    path('api-auth/', include('rest_framework.urls')),  # login for the browsable API
    path('django-admin/', admin.site.urls),
]
