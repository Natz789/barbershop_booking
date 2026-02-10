# payments/models.py

from django.db import models
from booking.models import Appointment

class Payment(models.Model):
    PAYMENT_METHOD_CHOICES = [
        ('pay_after', 'Pay After Service'),
        ('gcash', 'GCash'),
    ]
    
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('refunded', 'Refunded'),
    ]
    
    appointment = models.OneToOneField(Appointment, on_delete=models.CASCADE, related_name='payment')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    gcash_reference = models.CharField(max_length=100, blank=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Payment for {self.appointment} - {self.payment_status}"
    
    class Meta:
        verbose_name = 'Payment'
        verbose_name_plural = 'Payments'


class GCashQRCode(models.Model):
    name = models.CharField(max_length=100)
    qr_image = models.ImageField(upload_to='gcash_qr/')
    account_name = models.CharField(max_length=100)
    account_number = models.CharField(max_length=50)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = 'GCash QR Code'
        verbose_name_plural = 'GCash QR Codes'