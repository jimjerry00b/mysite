"""API tests for the House Management endpoints.

Run these against an isolated, throwaway test database (never your real data):

    # SQLite in-memory test DB (fast, safe — no MySQL/tunnel needed):
    DJANGO_DB_ENGINE= python manage.py test api

The APITestCase creates its own test database and rolls back after each test,
so it does NOT read or write your production rows.
"""
from decimal import Decimal

from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import ContactMessage, Property, RentPayment, Tenant


class ApiAuthTests(APITestCase):
    def test_endpoints_require_authentication(self):
        """Anonymous requests are rejected (session auth + IsAuthenticated)."""
        for name in ['property-list', 'tenant-list', 'rentpayment-list', 'contactmessage-list']:
            resp = self.client.get(reverse(name))
            self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN, name)

    def test_summary_requires_authentication(self):
        resp = self.client.get(reverse('dashboard-summary'))
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)


class PropertyApiTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user('tester', password='x')
        self.client.force_authenticate(self.user)

    def test_list_properties(self):
        Property.objects.create(name='Oak', rent_amount=Decimal('1200'), status='occupied')
        resp = self.client.get(reverse('property-list'))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['count'], 1)
        self.assertEqual(resp.data['results'][0]['name'], 'Oak')

    def test_create_property(self):
        payload = {'name': 'Maple', 'address': '4B', 'rent_amount': '950.00',
                   'bedrooms': 1, 'status': 'available'}
        resp = self.client.post(reverse('property-list'), payload)
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Property.objects.count(), 1)
        self.assertEqual(Property.objects.get().name, 'Maple')

    def test_update_and_delete_property(self):
        prop = Property.objects.create(name='Hill', rent_amount=Decimal('2100'))
        url = reverse('property-detail', args=[prop.pk])

        resp = self.client.patch(url, {'status': 'occupied'})
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        prop.refresh_from_db()
        self.assertEqual(prop.status, 'occupied')

        resp = self.client.delete(url)
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Property.objects.count(), 0)


class PaymentSerializerTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user('tester', password='x')
        self.client.force_authenticate(self.user)

    def test_payment_includes_tenant_and_property_names(self):
        prop = Property.objects.create(name='Riverside', rent_amount=Decimal('1650'), status='occupied')
        tenant = Tenant.objects.create(full_name='Ashleigh Langosh', property=prop)
        RentPayment.objects.create(tenant=tenant, amount=Decimal('1650'),
                                   payment_date='2026-07-20', status='paid')

        resp = self.client.get(reverse('rentpayment-list'))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        row = resp.data['results'][0]
        self.assertEqual(row['tenant_name'], 'Ashleigh Langosh')
        self.assertEqual(row['property_name'], 'Riverside')
        self.assertEqual(row['status'], 'paid')


class DashboardSummaryTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user('tester', password='x')
        self.client.force_authenticate(self.user)

    def test_summary_aggregates(self):
        occupied = Property.objects.create(name='A', rent_amount=Decimal('1200'), status='occupied')
        Property.objects.create(name='B', rent_amount=Decimal('900'), status='available')
        tenant = Tenant.objects.create(full_name='Brandon Jacob', property=occupied)
        RentPayment.objects.create(tenant=tenant, amount=Decimal('1200'),
                                   payment_date='2026-07-20', status='paid')
        ContactMessage.objects.create(name='Maria Hudson', email='m@x.com', subject='Hi', message='Hi')

        resp = self.client.get(reverse('dashboard-summary'))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['properties_total'], 2)
        self.assertEqual(Decimal(str(resp.data['monthly_revenue'])), Decimal('1200'))  # occupied only
        self.assertEqual(resp.data['tenants_active'], 1)
        self.assertEqual(len(resp.data['recent_payments']), 1)
        self.assertEqual(resp.data['recent_activity'][0]['name'], 'Maria Hudson')
