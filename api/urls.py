"""API routes: a DRF router for the CRUD resources, the dashboard summary,
and the OpenAPI schema + Swagger/ReDoc documentation."""
from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)
from rest_framework.permissions import AllowAny
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register('properties', views.PropertyViewSet)
router.register('tenants', views.TenantViewSet)
router.register('payments', views.RentPaymentViewSet)
router.register('messages', views.ContactMessageViewSet)

urlpatterns = [
    # --- Documentation (viewable without login; the API itself still needs a token) ---
    path('schema/', SpectacularAPIView.as_view(permission_classes=[AllowAny]), name='schema'),
    path('docs/', SpectacularSwaggerView.as_view(url_name='schema', permission_classes=[AllowAny]), name='swagger-ui'),
    path('redoc/', SpectacularRedocView.as_view(url_name='schema', permission_classes=[AllowAny]), name='redoc'),

    # --- Endpoints ---
    path('auth/login/', views.LoginView.as_view(), name='api-login'),
    path('dashboard/summary/', views.dashboard_summary, name='dashboard-summary'),
    path('', include(router.urls)),
]
