# payments/urls.py

from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('select/<int:appointment_id>/', views.select_payment, name='select_payment'),
    path('gcash/<int:payment_id>/', views.gcash_payment, name='gcash_payment'),
    path('mark-paid/<int:payment_id>/', views.mark_as_paid, name='mark_as_paid'),
]