from rest_framework import serializers

from .models import ContactMessage, Property, RentPayment, Tenant


class PropertySerializer(serializers.ModelSerializer):
    class Meta:
        model = Property
        fields = [
            'id', 'name', 'address', 'rent_amount', 'bedrooms',
            'status', 'created_at',
        ]


class TenantSerializer(serializers.ModelSerializer):
    property_name = serializers.CharField(source='property.name', read_only=True)

    class Meta:
        model = Tenant
        fields = [
            'id', 'full_name', 'email', 'phone', 'property', 'property_name',
            'lease_start', 'lease_end', 'created_at',
        ]


class RentPaymentSerializer(serializers.ModelSerializer):
    tenant_name = serializers.CharField(source='tenant.full_name', read_only=True)
    property_name = serializers.CharField(source='tenant.property.name', read_only=True)

    class Meta:
        model = RentPayment
        fields = [
            'id', 'tenant', 'tenant_name', 'property_name',
            'amount', 'payment_date', 'status', 'created_at',
        ]


class ContactMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactMessage
        fields = [
            'id', 'name', 'email', 'subject', 'message', 'is_read', 'created_at',
        ]


# --- Read-only serializers that document the /dashboard/summary/ response -----

class _RecentPaymentSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    tenant_name = serializers.CharField()
    property_name = serializers.CharField()
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    status = serializers.CharField()


class _RecentActivitySerializer(serializers.Serializer):
    name = serializers.CharField()
    subject = serializers.CharField()
    ago = serializers.CharField()


class DashboardSummarySerializer(serializers.Serializer):
    properties_total = serializers.IntegerField()
    monthly_revenue = serializers.DecimalField(max_digits=12, decimal_places=2)
    tenants_active = serializers.IntegerField()
    recent_payments = _RecentPaymentSerializer(many=True)
    recent_activity = _RecentActivitySerializer(many=True)


class TokenResponseSerializer(serializers.Serializer):
    """Response returned by the login endpoint."""
    token = serializers.CharField(
        help_text='API token — send it as "Authorization: Token <key>" or "Bearer <key>".'
    )
