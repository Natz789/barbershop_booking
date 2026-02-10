# barbers/admin.py

from django.contrib import admin
from .models import Barber, BarberAvailability

@admin.register(Barber)
class BarberAdmin(admin.ModelAdmin):
    list_display = ['name', 'specialization', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'specialization']

@admin.register(BarberAvailability)
class BarberAvailabilityAdmin(admin.ModelAdmin):
    list_display = ['barber', 'day_of_week', 'start_time', 'end_time', 'is_available']
    list_filter = ['day_of_week', 'is_available']
    search_fields = ['barber__name']