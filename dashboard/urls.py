# dashboard/urls.py

from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.home, name='home'),
    path('admin/appointments/', views.admin_appointments, name='admin_appointments'),
    path('landing/', views.landing_page, name='landing'),
]