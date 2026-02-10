# barbers/models.py

from django.db import models
from django.contrib.auth.models import User

class Barber(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='barber_profile')
    name = models.CharField(max_length=100)
    bio = models.TextField(blank=True)
    photo = models.ImageField(upload_to='barbers/', blank=True, null=True)
    specialization = models.CharField(max_length=200, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = 'Barber'
        verbose_name_plural = 'Barbers'


class BarberAvailability(models.Model):
    DAYS_OF_WEEK = [
        (0, 'Monday'),
        (1, 'Tuesday'),
        (2, 'Wednesday'),
        (3, 'Thursday'),
        (4, 'Friday'),
        (5, 'Saturday'),
        (6, 'Sunday'),
    ]
    
    barber = models.ForeignKey(Barber, on_delete=models.CASCADE, related_name='availability')
    day_of_week = models.IntegerField(choices=DAYS_OF_WEEK)
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_available = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.barber.name} - {self.get_day_of_week_display()}"
    
    class Meta:
        verbose_name = 'Barber Availability'
        verbose_name_plural = 'Barber Availabilities'
        unique_together = ['barber', 'day_of_week']