# payments/admin.py

from django.contrib import admin
from .models import Payment, GCashQRCode

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['appointment', 'payment_method', 'amount', 'payment_status', 'created_at']
    list_filter = ['payment_method', 'payment_status', 'created_at']
    search_fields = ['appointment__customer__username', 'gcash_reference']

@admin.register(GCashQRCode)
class GCashQRCodeAdmin(admin.ModelAdmin):
    list_display = ['name', 'account_name', 'account_number', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']