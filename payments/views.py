# payments/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Payment, GCashQRCode
from booking.models import Appointment
from datetime import datetime

@login_required
def select_payment(request, appointment_id):
    """Redirect to the consolidated booking confirmation page."""
    return redirect('booking:confirmation', pk=appointment_id)


@login_required
def gcash_payment(request, payment_id):
    payment = get_object_or_404(Payment, pk=payment_id, appointment__customer=request.user)
    
    if payment.payment_method != 'gcash':
        messages.error(request, 'This is not a GCash payment.')
        return redirect('booking:appointment_detail', pk=payment.appointment.pk)
    
    # Get active GCash QR code
    gcash_qr = GCashQRCode.objects.filter(is_active=True).first()
    
    if request.method == 'POST':
        reference_number = request.POST.get('reference_number')
        
        if reference_number:
            payment.gcash_reference = reference_number
            payment.save()
            
            messages.success(request, 'GCash reference submitted! Waiting for admin verification.')
            return redirect('booking:appointment_detail', pk=payment.appointment.pk)
        else:
            messages.error(request, 'Please provide a reference number.')
    
    context = {
        'payment': payment,
        'gcash_qr': gcash_qr,
    }
    
    return render(request, 'payments/gcash_payment.html', context)


@login_required
def mark_as_paid(request, payment_id):
    if not request.user.is_staff:
        messages.error(request, 'You do not have permission to perform this action.')
        return redirect('dashboard:home')
    
    payment = get_object_or_404(Payment, pk=payment_id)
    
    if request.method == 'POST':
        payment.payment_status = 'paid'
        payment.paid_at = datetime.now()
        payment.save()
        
        messages.success(request, 'Payment marked as paid.')
        return redirect('dashboard:admin_appointments')
    
    return render(request, 'payments/mark_as_paid.html', {'payment': payment})