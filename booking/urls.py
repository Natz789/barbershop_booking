# booking/urls.py

from django.urls import path
from . import views

app_name = 'booking'

urlpatterns = [
    path('create/', views.create_appointment, name='create'),
    path('my-appointments/', views.my_appointments, name='my_appointments'),
    path('appointment/<int:pk>/', views.appointment_detail, name='appointment_detail'),
    path('appointment/<int:pk>/cancel/', views.cancel_appointment, name='cancel_appointment'),
    path('appointment/<int:pk>/approve/', views.approve_appointment, name='approve_appointment'),
    path('appointment/<int:pk>/decline/', views.decline_appointment, name='decline_appointment'),
    path('appointment/<int:pk>/complete/', views.complete_appointment, name='complete_appointment'),
    path('appointment/<int:pk>/reschedule/', views.reschedule_appointment, name='reschedule'),
    path('appointment/<int:pk>/confirmation/', views.booking_confirmation, name='confirmation'),
    path('calendar/admin/', views.admin_calendar, name='admin_calendar'),
    path('calendar/my/', views.customer_calendar, name='customer_calendar'),
    path('api/calendar-events/', views.get_calendar_events, name='calendar_events'),
    path('api/available-slots/', views.get_available_slots, name='available_slots'),
]