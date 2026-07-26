from django.contrib import admin

from .models import ContactMessage, Property, RentPayment, Tenant


@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = ('name', 'address', 'bedrooms', 'rent_amount', 'status', 'created_at')
    list_filter = ('status', 'bedrooms')
    search_fields = ('name', 'address')


@admin.register(Tenant)
class TenantAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'email', 'phone', 'property', 'lease_start', 'lease_end')
    list_filter = ('property',)
    search_fields = ('full_name', 'email', 'phone')


@admin.register(RentPayment)
class RentPaymentAdmin(admin.ModelAdmin):
    list_display = ('tenant', 'amount', 'payment_date', 'status', 'created_at')
    list_filter = ('status', 'payment_date')
    search_fields = ('tenant__full_name',)


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'subject', 'is_read', 'created_at')
    list_filter = ('is_read', 'created_at')
    search_fields = ('name', 'email', 'subject', 'message')
