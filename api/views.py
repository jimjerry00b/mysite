from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.shortcuts import render
from django.utils.timesince import timesince
from drf_spectacular.utils import extend_schema
from rest_framework import viewsets
from rest_framework.authtoken.serializers import AuthTokenSerializer
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .models import ContactMessage, Property, RentPayment, Tenant
from .serializers import (
    ContactMessageSerializer,
    DashboardSummarySerializer,
    PropertySerializer,
    RentPaymentSerializer,
    TenantSerializer,
    TokenResponseSerializer,
)


@login_required
def dashboard(request):
    """Render the NiceAdmin-style admin dashboard. Requires an authenticated
    (staff) user; unauthenticated visitors are redirected to the admin login.
    The widgets are populated client-side from /api/dashboard/summary/."""
    return render(request, 'dashboard.html', {'active_page': 'dashboard'})


# --- Login: exchange username + password for an API token --------------------

class LoginView(ObtainAuthToken):
    """Exchange a username and password for an API token.

    POST your credentials and use the returned token in the `Authorization`
    header (`Token <key>` or `Bearer <key>`) for every other endpoint. This
    endpoint itself needs no token."""

    authentication_classes = []          # no session/CSRF needed to log in
    permission_classes = [AllowAny]

    @extend_schema(request=AuthTokenSerializer, responses=TokenResponseSerializer)
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


# --- REST API viewsets (full CRUD, session-authenticated) --------------------

class PropertyViewSet(viewsets.ModelViewSet):
    """Rentable houses/units. Supports list, retrieve, create, update and delete."""
    queryset = Property.objects.all()
    serializer_class = PropertySerializer


class TenantViewSet(viewsets.ModelViewSet):
    """Tenants renting a property. Includes the linked `property_name` (read-only)."""
    queryset = Tenant.objects.select_related('property').all()
    serializer_class = TenantSerializer


class RentPaymentViewSet(viewsets.ModelViewSet):
    """Rent payments. Each row includes `tenant_name` and `property_name` (read-only)."""
    queryset = RentPayment.objects.select_related('tenant', 'tenant__property').all()
    serializer_class = RentPaymentSerializer


class ContactMessageViewSet(viewsets.ModelViewSet):
    """Messages submitted through the site's contact form."""
    queryset = ContactMessage.objects.all()
    serializer_class = ContactMessageSerializer


# --- Dashboard summary (aggregates the widgets need) -------------------------

@extend_schema(responses=DashboardSummarySerializer)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_summary(request):
    """Aggregated metrics + recent rows used by the dashboard widgets:
    total properties, monthly rent from occupied units, active tenant count,
    the five most recent payments and the five most recent contact messages."""
    monthly_revenue = (
        Property.objects.filter(status='occupied')
        .aggregate(total=Sum('rent_amount'))['total']
        or 0
    )

    recent_payments = [
        {
            'id': p.id,
            'tenant_name': p.tenant.full_name,
            'property_name': p.tenant.property.name if p.tenant.property else '-',
            'amount': p.amount,
            'status': p.status,
        }
        for p in RentPayment.objects.select_related('tenant', 'tenant__property')[:5]
    ]

    recent_activity = [
        {
            'name': m.name,
            'subject': m.subject or '(no subject)',
            'ago': timesince(m.created_at).split(',')[0] + ' ago',
        }
        for m in ContactMessage.objects.all()[:5]
    ]

    return Response({
        'properties_total': Property.objects.count(),
        'monthly_revenue': monthly_revenue,
        'tenants_active': Tenant.objects.count(),
        'recent_payments': recent_payments,
        'recent_activity': recent_activity,
    })
