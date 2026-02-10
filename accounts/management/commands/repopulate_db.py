import os
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from accounts.models import UserProfile
from barbers.models import Barber, BarberAvailability
from services.models import Service
from datetime import time

class Command(BaseCommand):
    help = 'Repopulate the database with test data and create an admin account'

    def handle(self, *args, **options):
        self.stdout.write("=" * 60)
        self.stdout.write("REPOPULATING DATABASE WITH TEST DATA")
        self.stdout.write("=" * 60)

        # Clear existing data
        self.stdout.write("Clearing existing data...")
        User.objects.all().delete()
        Service.objects.all().delete()
        Barber.objects.all().delete()
        # BarberAvailability and UserProfile will be deleted via cascade or manual if needed
        # UserProfile.objects.all().delete() # Already deleted via User cascade
        
        # Create admin user
        self.stdout.write("\nCreating admin user...")
        admin = User.objects.create_superuser(
            username='admin',
            email='admin@barbershop.com',
            password='admin123',
            first_name='Admin',
            last_name='User'
        )
        UserProfile.objects.get_or_create(user=admin, defaults={'role': 'admin', 'phone': '09171234567'})
        self.stdout.write(self.style.SUCCESS(f"✓ Created admin: username='admin', password='admin123'"))

        # Create barber users
        barbers_data = [
            {
                'username': 'barber1',
                'password': 'barber123',
                'first_name': 'John',
                'last_name': 'Smith',
                'email': 'john@barbershop.com',
                'phone': '09171234568',
                'name': 'John Smith',
                'specialization': 'Classic Cuts & Fades',
                'bio': 'Expert in traditional barbering with 10 years of experience.',
                'schedule': 'mon-fri'
            },
            {
                'username': 'barber2',
                'password': 'barber123',
                'first_name': 'Mike',
                'last_name': 'Johnson',
                'email': 'mike@barbershop.com',
                'phone': '09171234569',
                'name': 'Mike Johnson',
                'specialization': 'Modern Styles & Beard Grooming',
                'bio': 'Specializes in contemporary hairstyles and beard sculpting.',
                'schedule': 'mon-fri'
            },
            {
                'username': 'barber3',
                'password': 'barber123',
                'first_name': 'Carlos',
                'last_name': 'Rodriguez',
                'email': 'carlos@barbershop.com',
                'phone': '09171234570',
                'name': 'Carlos Rodriguez',
                'specialization': 'Trendy Cuts & Hair Coloring',
                'bio': 'Creative stylist with expertise in modern trends and color.',
                'schedule': 'sun-wed'
            },
            {
                'username': 'barber4',
                'password': 'barber123',
                'first_name': 'David',
                'last_name': 'Lee',
                'email': 'david@barbershop.com',
                'phone': '09171234571',
                'name': 'David Lee',
                'specialization': 'Precision Cuts & Styling',
                'bio': 'Detail-oriented barber focused on precision and style.',
                'schedule': 'sun-wed'
            }
        ]

        created_barbers = []
        for b_data in barbers_data:
            user = User.objects.create_user(
                username=b_data['username'],
                password=b_data['password'],
                first_name=b_data['first_name'],
                last_name=b_data['last_name'],
                email=b_data['email']
            )
            UserProfile.objects.create(user=user, role='barber', phone=b_data['phone'])
            barber = Barber.objects.create(
                user=user,
                name=b_data['name'],
                specialization=b_data['specialization'],
                bio=b_data['bio'],
                is_active=True
            )
            created_barbers.append({'barber': barber, 'schedule': b_data['schedule']})
            self.stdout.write(self.style.SUCCESS(f"✓ Created barber: {b_data['username']}"))

        # Create availability
        self.stdout.write("\nCreating availability...")
        start_time = time(9, 0)
        end_time = time(18, 0)
        for b_info in created_barbers:
            barber = b_info['barber']
            days = [0, 1, 2, 3, 4] if b_info['schedule'] == 'mon-fri' else [6, 0, 1, 2]
            for day in days:
                BarberAvailability.objects.create(
                    barber=barber,
                    day_of_week=day,
                    start_time=start_time,
                    end_time=end_time,
                    is_available=True
                )

        # Create services
        self.stdout.write("\nCreating services...")
        services_data = [
            {'name': 'Classic Haircut', 'duration_minutes': 30, 'price': 250.00, 'description': 'Basic style'},
            {'name': 'Premium Haircut', 'duration_minutes': 45, 'price': 400.00, 'description': 'Expert style'},
            {'name': 'Beard Trim', 'duration_minutes': 20, 'price': 150.00, 'description': 'Shape and trim'},
        ]
        for s_data in services_data:
            Service.objects.create(**s_data)
            self.stdout.write(self.style.SUCCESS(f"✓ Created service: {s_data['name']}"))

        self.stdout.write("\n" + "=" * 60)
        self.stdout.write(self.style.SUCCESS("DATABASE POPULATED SUCCESSFULLY!"))
        self.stdout.write("=" * 60)
