# booking/forms.py

from django import forms
from .models import Appointment
from barbers.models import Barber
from services.models import Service
from datetime import datetime, time, timedelta

class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['service', 'barber', 'appointment_date', 'appointment_time', 'notes']
        widgets = {
            'appointment_date': forms.DateInput(attrs={'type': 'date', 'min': datetime.now().date()}),
            'appointment_time': forms.TimeInput(attrs={'type': 'time'}),
            'notes': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Any special requests or notes...'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['service'].queryset = Service.objects.filter(is_active=True)
        self.fields['barber'].queryset = Barber.objects.filter(is_active=True)
        
        # Add CSS classes
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'
    
    def clean(self):
        cleaned_data = super().clean()
        appointment_date = cleaned_data.get('appointment_date')
        appointment_time = cleaned_data.get('appointment_time')
        barber = cleaned_data.get('barber')
        
        if appointment_date and appointment_time and barber:
            # Check if date is not in the past
            if appointment_date < datetime.now().date():
                raise forms.ValidationError('Cannot book appointments in the past.')
            
            # Check if barber is already booked
            existing = Appointment.objects.filter(
                barber=barber,
                appointment_date=appointment_date,
                appointment_time=appointment_time,
                status__in=['pending', 'confirmed']
            )
            
            if self.instance.pk:
                existing = existing.exclude(pk=self.instance.pk)
            
            if existing.exists():
                raise forms.ValidationError('This barber is already booked at this time. Please choose another time.')
        
        return cleaned_data