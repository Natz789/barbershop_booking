# booking/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Appointment
from .forms import AppointmentForm
from payments.models import Payment
from services.models import Service

@login_required
def create_appointment(request):
    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.customer = request.user
            
            # Set queue number for the day
            from django.db.models import Max
            today_max = Appointment.objects.filter(
                appointment_date=appointment.appointment_date
            ).aggregate(Max('queue_number'))['queue_number__max'] or 0
            appointment.queue_number = today_max + 1
            
            appointment.save()
            
            # Store appointment ID in session for payment
            request.session['appointment_id'] = appointment.id
            
            messages.success(request, 'Appointment created successfully!')
            # Redirect to confirmation page where they can see ticket and select payment
            return redirect('booking:confirmation', pk=appointment.id)
    else:
        form = AppointmentForm()
    
    return render(request, 'booking/create_appointment.html', {'form': form})


@login_required
def my_appointments(request):
    appointments = Appointment.objects.filter(
        customer=request.user
    ).select_related('barber', 'service', 'payment').order_by('-appointment_date', '-appointment_time')
    
    return render(request, 'booking/my_appointments.html', {'appointments': appointments})


@login_required
def appointment_detail(request, pk):
    appointment = get_object_or_404(
        Appointment.objects.select_related('barber', 'service', 'customer'),
        pk=pk
    )
    
    # Check permission
    if not request.user.is_staff and appointment.customer != request.user:
        messages.error(request, 'You do not have permission to view this appointment.')
        return redirect('booking:my_appointments')
    
    return render(request, 'booking/appointment_detail.html', {'appointment': appointment})


@login_required
def cancel_appointment(request, pk):
    appointment = get_object_or_404(Appointment, pk=pk)
    
    # Check permission
    if not request.user.is_staff and appointment.customer != request.user:
        messages.error(request, 'You do not have permission to cancel this appointment.')
        return redirect('booking:my_appointments')
    
    if request.method == 'POST':
        appointment.status = 'cancelled'
        appointment.save()
        messages.success(request, 'Appointment cancelled successfully.')
        if request.user.is_staff:
            return redirect('dashboard:admin_appointments')
        return redirect('booking:my_appointments')
    
    return render(request, 'booking/cancel_appointment.html', {'appointment': appointment})


@login_required
def approve_appointment(request, pk):
    if not request.user.is_staff:
        messages.error(request, 'You do not have permission to perform this action.')
        return redirect('dashboard:home')
    
    appointment = get_object_or_404(Appointment, pk=pk)
    appointment.status = 'confirmed'
    appointment.save()
    
    messages.success(request, f'Appointment for {appointment.customer.username} has been approved.')
    return redirect('dashboard:admin_appointments')


@login_required
def decline_appointment(request, pk):
    if not request.user.is_staff:
        messages.error(request, 'You do not have permission to perform this action.')
        return redirect('dashboard:home')
    
    appointment = get_object_or_404(Appointment, pk=pk)
    appointment.status = 'declined'
    appointment.save()
    
    messages.success(request, f'Appointment for {appointment.customer.username} has been declined.')
    return redirect('dashboard:admin_appointments')


@login_required
def complete_appointment(request, pk):
    if not request.user.is_staff:
        messages.error(request, 'You do not have permission to perform this action.')
        return redirect('dashboard:home')
    
    appointment = get_object_or_404(Appointment, pk=pk)
    
    # Check if payment is made
    if not hasattr(appointment, 'payment') or appointment.payment.payment_status != 'paid':
        messages.error(request, 'Cannot complete appointment until payment is recorded.')
        return redirect('booking:appointment_detail', pk=pk)
    
    appointment.status = 'completed'
    appointment.save()
    
    messages.success(request, f'Appointment for {appointment.customer.username} is now completed.')
    return redirect('dashboard:admin_appointments')


@login_required
def update_appointment_status(request, pk):
    if not request.user.is_staff:
        messages.error(request, 'You do not have permission to perform this action.')
        return redirect('dashboard:home')
    
    appointment = get_object_or_404(Appointment, pk=pk)
    
    if request.method == 'POST':
        status = request.POST.get('status')
        if status in dict(Appointment.STATUS_CHOICES):
            appointment.status = status
            appointment.save()
            messages.success(request, f'Appointment status updated to {appointment.get_status_display()}.')
        else:
            messages.error(request, 'Invalid status.')
    if request.user.is_staff and request.method == 'POST':
        return redirect('dashboard:admin_appointments')
        
    return redirect('booking:appointment_detail', pk=pk)


@login_required
def admin_calendar(request):
    if not request.user.is_staff:
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('dashboard:home')
    return render(request, 'booking/admin_calendar.html')


@login_required
def customer_calendar(request):
    return render(request, 'booking/customer_calendar.html')


@login_required
def get_calendar_events(request):
    """API endpoint for FullCalendar events."""
    from django.http import JsonResponse
    from datetime import datetime
    
    start_str = request.GET.get('start')
    end_str = request.GET.get('end')
    
    if not start_str or not end_str:
        return JsonResponse({'error': 'Missing start or end parameters'}, status=400)
    
    # FullCalendar uses ISO8601 strings
    try:
        # FullCalendar might send strings with time, or just date
        start_date = datetime.fromisoformat(start_str.replace('Z', '+00:00')).date()
        end_date = datetime.fromisoformat(end_str.replace('Z', '+00:00')).date()
    except ValueError:
        # Fallback if fromisoformat fails
        start_date = datetime.strptime(start_str[:10], '%Y-%m-%d').date()
        end_date = datetime.strptime(end_str[:10], '%Y-%m-%d').date()

    if request.user.is_staff:
        appointments = Appointment.objects.filter(
            appointment_date__range=[start_date, end_date]
        ).select_related('customer', 'service', 'barber')
    else:
        appointments = Appointment.objects.filter(
            customer=request.user,
            appointment_date__range=[start_date, end_date]
        ).select_related('service', 'barber')
    
    events = []
    for appt in appointments:
        # Calculate end time based on service duration
        from datetime import timedelta
        start_dt = datetime.combine(appt.appointment_date, appt.appointment_time)
        end_dt = start_dt + timedelta(minutes=appt.service.duration_minutes)
        
        status_colors = {
            'pending': '#f39c12',  # Orange
            'confirmed': '#27ae60', # Green
            'completed': '#2980b9', # Blue
            'cancelled': '#c0392b', # Red
            'declined': '#7f8c8d',  # Grey
        }
        
        title = f"{appt.service.name}"
        if request.user.is_staff:
            title = f"{appt.customer.username}: {title}"
            
        events.append({
            'id': appt.id,
            'title': title,
            'start': start_dt.isoformat(),
            'end': end_dt.isoformat(),
            'color': status_colors.get(appt.status, '#34495e'),
            'url': f'/booking/appointment/{appt.id}/',
            'extendedProps': {
                'status': appt.get_status_display(),
                'barber': appt.barber.name,
                'customer': appt.customer.username if request.user.is_staff else None
            }
        })
        
    return JsonResponse(events, safe=False)


@login_required
def get_available_slots(request):
    """AJAX endpoint to get available time slots for a barber on a specific date."""
    from django.http import JsonResponse
    from datetime import datetime
    from barbers.models import Barber
    from .utils import get_available_slots as get_slots, format_time_slot
    
    barber_id = request.GET.get('barber_id')
    date_str = request.GET.get('date')
    
    if not barber_id or not date_str:
        return JsonResponse({'error': 'Missing parameters'}, status=400)
    
    try:
        barber = Barber.objects.get(pk=barber_id, is_active=True)
        date = datetime.strptime(date_str, '%Y-%m-%d').date()
    except (Barber.DoesNotExist, ValueError):
        return JsonResponse({'error': 'Invalid barber or date'}, status=400)
    
    # Get available slots
    slots = get_slots(barber, date)
    
    # Format response
    slots_data = [
        {
            'time': slot['time'].strftime('%H:%M'),
            'display': format_time_slot(slot['time']),
            'available': slot['available'],
            'reason': slot['reason']
        }
        for slot in slots
    ]
    
    return JsonResponse({'slots': slots_data})


@login_required
def reschedule_appointment(request, pk):
    """Allow customers to reschedule their appointments."""
    appointment = get_object_or_404(Appointment, pk=pk)
    
    # Check permission
    if not request.user.is_staff and appointment.customer != request.user:
        messages.error(request, 'You do not have permission to reschedule this appointment.')
        return redirect('booking:my_appointments')
    
    # Check if can reschedule
    if not appointment.can_reschedule():
        messages.error(request, 'This appointment cannot be rescheduled. It may be too close to the appointment time or already completed/cancelled.')
        return redirect('booking:appointment_detail', pk=pk)
    
    if request.method == 'POST':
        form = AppointmentForm(request.POST, instance=appointment)
        if form.is_valid():
            form.save()
            messages.success(request, 'Appointment rescheduled successfully!')
            return redirect('booking:appointment_detail', pk=pk)
    else:
        form = AppointmentForm(instance=appointment)
    
    context = {
        'form': form,
        'appointment': appointment,
        'is_reschedule': True
    }
    return render(request, 'booking/reschedule_appointment.html', context)


@login_required
def booking_confirmation(request, pk):
    """Display booking confirmation page with queue ticket and payment options."""
    appointment = get_object_or_404(
        Appointment.objects.select_related('barber', 'service', 'customer'),
        pk=pk
    )
    
    # Check permission
    if not request.user.is_staff and appointment.customer != request.user:
        messages.error(request, 'You do not have permission to view this appointment.')
        return redirect('booking:my_appointments')

    # If payment already exists, redirect to detail
    if hasattr(appointment, 'payment') and request.method == 'GET':
        return redirect('booking:appointment_detail', pk=appointment.pk)

    if request.method == 'POST':
        payment_method = request.POST.get('payment_method')
        gcash_reference = request.POST.get('reference_number', '')
        
        if payment_method in ['gcash', 'pay_after']:
            # Create or update payment
            from payments.models import Payment
            payment, created = Payment.objects.get_or_create(
                appointment=appointment,
                defaults={'amount': appointment.service.price}
            )
            payment.payment_method = payment_method
            payment.amount = appointment.service.price # Ensure amount is correct
            
            if payment_method == 'gcash':
                if not gcash_reference:
                    messages.error(request, 'Please provide a GCash reference number.')
                else:
                    payment.gcash_reference = gcash_reference
                    payment.save()
                    messages.success(request, 'Payment details submitted! Waiting for verification.')
                    return redirect('booking:appointment_detail', pk=appointment.pk)
            else:
                payment.save()
                messages.success(request, 'Booking confirmed! You may pay after your service.')
                return redirect('booking:appointment_detail', pk=appointment.pk)
        else:
            messages.error(request, 'Invalid payment method selected.')

    # Get GCash QR
    from payments.models import GCashQRCode
    gcash_qr = GCashQRCode.objects.filter(is_active=True).first()
    
    context = {
        'appointment': appointment,
        'gcash_qr': gcash_qr,
    }
    return render(request, 'booking/booking_confirmation.html', context)
