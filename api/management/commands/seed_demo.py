"""Seed a small sample House Management dataset for the dashboard + API.

Usage:
    python manage.py seed_demo          # seed only if empty
    python manage.py seed_demo --clear  # wipe seeded tables, then seed
"""
import datetime
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.utils import timezone

from api.models import ContactMessage, Property, RentPayment, Tenant


class Command(BaseCommand):
    help = 'Seed a small sample House Management dataset.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear', action='store_true',
            help='Delete existing rows in these tables before seeding.',
        )

    def handle(self, *args, **options):
        if options['clear']:
            RentPayment.objects.all().delete()
            Tenant.objects.all().delete()
            Property.objects.all().delete()
            ContactMessage.objects.all().delete()
            self.stdout.write(self.style.WARNING('Cleared existing House Management data.'))

        if Property.objects.exists():
            self.stdout.write('Data already present; nothing seeded. Use --clear to reset.')
            return

        today = timezone.now().date()
        now = timezone.now()

        # --- Properties ------------------------------------------------------
        props = {
            'oak': Property.objects.create(name='Oak Street 2-Bed', address='12 Oak Street', rent_amount=Decimal('1200'), bedrooms=2, status='occupied'),
            'maple': Property.objects.create(name='Maple Apartments 4B', address='4B Maple Court', rent_amount=Decimal('950'), bedrooms=1, status='occupied'),
            'river': Property.objects.create(name='Riverside Cottage', address='8 River Lane', rent_amount=Decimal('1650'), bedrooms=3, status='occupied'),
            'studio': Property.objects.create(name='Downtown Studio', address='220 Main St', rent_amount=Decimal('800'), bedrooms=0, status='available'),
            'hill': Property.objects.create(name='Hilltop House', address='5 Hill Road', rent_amount=Decimal('2100'), bedrooms=4, status='available'),
            'garden': Property.objects.create(name='Garden Flat', address='9 Garden Way', rent_amount=Decimal('1050'), bedrooms=2, status='maintenance'),
        }

        # --- Tenants ---------------------------------------------------------
        tenants = {
            'brandon': Tenant.objects.create(full_name='Brandon Jacob', email='brandon@example.com', phone='555-0101', property=props['oak'], lease_start=today - datetime.timedelta(days=120)),
            'bridie': Tenant.objects.create(full_name='Bridie Kessler', email='bridie@example.com', phone='555-0102', property=props['maple'], lease_start=today - datetime.timedelta(days=60)),
            'ashleigh': Tenant.objects.create(full_name='Ashleigh Langosh', email='ashleigh@example.com', phone='555-0103', property=props['river'], lease_start=today - datetime.timedelta(days=200)),
            'angus': Tenant.objects.create(full_name='Angus Grady', email='angus@example.com', phone='555-0104'),
            'raheem': Tenant.objects.create(full_name='Raheem Lehner', email='raheem@example.com', phone='555-0105'),
        }

        # --- Rent payments ---------------------------------------------------
        RentPayment.objects.create(tenant=tenants['raheem'], amount=Decimal('1050'), payment_date=today, status='paid')
        RentPayment.objects.create(tenant=tenants['bridie'], amount=Decimal('950'), payment_date=today - datetime.timedelta(days=1), status='pending')
        RentPayment.objects.create(tenant=tenants['brandon'], amount=Decimal('1200'), payment_date=today - datetime.timedelta(days=2), status='paid')
        RentPayment.objects.create(tenant=tenants['angus'], amount=Decimal('800'), payment_date=today - datetime.timedelta(days=3), status='overdue')
        RentPayment.objects.create(tenant=tenants['ashleigh'], amount=Decimal('1650'), payment_date=today - datetime.timedelta(days=5), status='paid')
        RentPayment.objects.create(tenant=tenants['brandon'], amount=Decimal('1200'), payment_date=today - datetime.timedelta(days=32), status='paid')

        # --- Contact messages (varied timestamps for the activity feed) ------
        messages = [
            ('Maria Hudson', 'maria@example.com', 'Is the Oak Street 2-bed still available?', 32, 'minutes'),
            ('Anna Nelson', 'anna@example.com', 'Signed lease returned', 56, 'minutes'),
            ('David Muldon', 'david@example.com', 'Can we schedule the inspection for Friday?', 2, 'hours'),
            ('Kevin Price', 'kevin@example.com', 'Maintenance: leaking tap in 4B', 1, 'days'),
            ('Sara Lynn', 'sara@example.com', 'Question about the security deposit', 2, 'days'),
        ]
        deltas = {'minutes': lambda n: datetime.timedelta(minutes=n),
                  'hours': lambda n: datetime.timedelta(hours=n),
                  'days': lambda n: datetime.timedelta(days=n)}
        for name, email, subject, n, unit in messages:
            m = ContactMessage.objects.create(name=name, email=email, subject=subject, message=subject)
            # auto_now_add ignores an assigned value on create, so update afterwards.
            ContactMessage.objects.filter(pk=m.pk).update(created_at=now - deltas[unit](n))

        self.stdout.write(self.style.SUCCESS(
            f'Seeded {Property.objects.count()} properties, {Tenant.objects.count()} tenants, '
            f'{RentPayment.objects.count()} payments, {ContactMessage.objects.count()} messages.'
        ))
