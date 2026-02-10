# dashboard/views.py

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from booking.models import Appointment
from barbers.models import Barber
from services.models import Service
from django.db.models import Count, Q
from django.contrib import messages
from datetime import datetime, timedelta


def landing_page(request):
    """Public landing page - no login required"""
    if request.user.is_authenticated:
        return redirect('dashboard:home')
    
    services = Service.objects.filter(is_active=True)[:6]
    barbers = Barber.objects.filter(is_active=True)[:3]
    
    context = {
        'services': services,
        'barbers': barbers,
    }
    return render(request, 'dashboard/landing.html', context)


@login_required
def home(request):
    user = request.user
    context = {}
    
    if user.is_staff:
        # Admin dashboard
        today = datetime.now().date()
        
        # Statistics
        total_appointments = Appointment.objects.count()
        pending_appointments = Appointment.objects.filter(status='pending').count()
        today_appointments = Appointment.objects.filter(appointment_date=today).count()
        total_barbers = Barber.objects.filter(is_active=True).count()
        
        # Recent appointments
        recent_appointments = Appointment.objects.select_related(
            'customer', 'barber', 'service'
        ).order_by('-created_at')[:10]
        
        context = {
            'total_appointments': total_appointments,
            'pending_appointments': pending_appointments,
            'today_appointments': today_appointments,
            'total_barbers': total_barbers,
            'recent_appointments': recent_appointments,
            'is_admin': True,
        }
    else:
        # Customer dashboard
        user_appointments = Appointment.objects.filter(
            customer=user
        ).select_related('barber', 'service').order_by('-appointment_date', '-appointment_time')[:5]
        
        upcoming_appointments = Appointment.objects.filter(
            customer=user,
            appointment_date__gte=datetime.now().date(),
            status__in=['pending', 'confirmed']
        ).order_by('appointment_date', 'appointment_time')
        
        context = {
            'user_appointments': user_appointments,
            'upcoming_appointments': upcoming_appointments,
            'is_admin': False,
        }
    
    return render(request, 'dashboard/home.html', context)


@login_required
def admin_appointments(request):
    if not request.user.is_staff:
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('dashboard:home')
    
    status_filter = request.GET.get('status', '')
    
    appointments = Appointment.objects.select_related(
        'customer', 'barber', 'service'
    ).order_by('-appointment_date', '-appointment_time')
    
    if status_filter:
        appointments = appointments.filter(status=status_filter)
    
    context = {
        'appointments': appointments,
        'status_filter': status_filter,
    }
    
    return render(request, 'dashboard/admin_appointments.html', context)