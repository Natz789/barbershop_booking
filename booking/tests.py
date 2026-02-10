from django.test import TestCase, Client
from django.contrib.auth.models import User
from barbers.models import Barber
from services.models import Service
from booking.models import Appointment
from payments.models import Payment
from datetime import date, time

from django.urls import reverse

class AppointmentWorkflowTest(TestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser(username='admin', password='password', email='admin@test.com')
        self.customer = User.objects.create_user(username='customer', password='password', email='customer@test.com')
        barber_user = User.objects.create_user(username='barber_user', password='password')
        self.barber = Barber.objects.create(user=barber_user, name='Test Barber', is_active=True)
        self.service = Service.objects.create(name='Test Service', price=500, duration_minutes=30, is_active=True)
        self.client = Client()
        
    def test_appointment_lifecycle(self):
        # 1. Create appointment
        self.client.login(username='customer', password='password')
        appointment = Appointment.objects.create(
            customer=self.customer,
            barber=self.barber,
            service=self.service,
            appointment_date=date.today(),
            appointment_time=time(10, 0),
            status='pending'
        )
        Payment.objects.create(appointment=appointment, payment_method='pay_after', amount=500)
        
        # 2. Admin Approves
        self.client.login(username='admin', password='password')
        response = self.client.get(reverse('booking:approve_appointment', kwargs={'pk': appointment.pk}))
        appointment.refresh_from_db()
        self.assertEqual(appointment.status, 'confirmed')
        
        # 3. Try to complete without payment
        response = self.client.get(reverse('booking:complete_appointment', kwargs={'pk': appointment.pk}))
        appointment.refresh_from_db()
        self.assertEqual(appointment.status, 'confirmed') # Should stay confirmed
        
        # 4. Mark as paid
        payment = appointment.payment
        self.client.post(reverse('payments:mark_as_paid', kwargs={'payment_id': payment.pk}))
        payment.refresh_from_db()
        self.assertEqual(payment.payment_status, 'paid')
        
        # 5. Complete appointment
        response = self.client.get(reverse('booking:complete_appointment', kwargs={'pk': appointment.pk}))
        appointment.refresh_from_db()
        self.assertEqual(appointment.status, 'completed')
        
    def test_calendar_api_filtering(self):
        # Create appointments for two customers
        customer2 = User.objects.create_user(username='customer2', password='password')
        Appointment.objects.create(customer=self.customer, barber=self.barber, service=self.service, appointment_date=date.today(), appointment_time=time(10, 0))
        Appointment.objects.create(customer=customer2, barber=self.barber, service=self.service, appointment_date=date.today(), appointment_time=time(11, 0))
        
        # Customer sees 1 appointment
        self.client.login(username='customer', password='password')
        response = self.client.get(reverse('booking:calendar_events'), {'start': date.today().isoformat(), 'end': date.today().isoformat()})
        self.assertEqual(len(response.json()), 1)
        
        # Admin sees 2 appointments
        self.client.login(username='admin', password='password')
        response = self.client.get(reverse('booking:calendar_events'), {'start': date.today().isoformat(), 'end': date.today().isoformat()})
        self.assertEqual(len(response.json()), 2)
