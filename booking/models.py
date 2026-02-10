# booking/models.py

from django.db import models
from django.contrib.auth.models import User
from barbers.models import Barber
from services.models import Service

class Appointment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed/Scheduled'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('declined', 'Declined'),
    ]
    
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='appointments')
    barber = models.ForeignKey(Barber, on_delete=models.CASCADE, related_name='appointments')
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='appointments')
    appointment_date = models.DateField()
    appointment_time = models.TimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    notes = models.TextField(blank=True)
    queue_number = models.PositiveIntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def can_reschedule(self):
        """Check if appointment can be rescheduled."""
        from datetime import datetime, timedelta
        
        # Can't reschedule completed or cancelled appointments
        if self.status in ['completed', 'cancelled']:
            return False
        
        # Can't reschedule if appointment is in the past
        appointment_datetime = datetime.combine(self.appointment_date, self.appointment_time)
        if appointment_datetime < datetime.now():
            return False
        
        # Can reschedule if at least 2 hours before appointment
        time_until_appointment = appointment_datetime - datetime.now()
        return time_until_appointment > timedelta(hours=2)
    
    def get_end_time(self):
        """Calculate appointment end time based on service duration."""
        from datetime import datetime, timedelta
        start_datetime = datetime.combine(datetime.today(), self.appointment_time)
        end_datetime = start_datetime + timedelta(minutes=self.service.duration_minutes)
        return end_datetime.time()
    
    def __str__(self):
        return f"{self.customer.username} - {self.barber.name} - {self.appointment_date}"
    
    class Meta:
        verbose_name = 'Appointment'
        verbose_name_plural = 'Appointments'
        ordering = ['-appointment_date', '-appointment_time']
        unique_together = ['barber', 'appointment_date', 'appointment_time']