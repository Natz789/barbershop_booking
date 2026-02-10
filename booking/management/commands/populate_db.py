# booking/management/commands/populate_db.py

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from accounts.models import UserProfile
from barbers.models import Barber, BarberAvailability
from services.models import Service
from datetime import time


class Command(BaseCommand):
    help = 'Populate database with test data'

    def handle(self, *args, **kwargs):
        self.stdout.write("=" * 60)
        self.stdout.write("POPULATING DATABASE WITH TEST DATA")
        self.stdout.write("=" * 60)
        
        # Create admin
        self.create_admin()
        
        # Create barbers
        barbers = self.create_barbers()
        
        # Create availability
        self.create_availability(barbers)
        
        # Create services
        self.create_services()
        
        # Print summary
        self.print_summary()
    
    def create_admin(self):
        self.stdout.write("\nCreating admin user...")
        admin = User.objects.create_superuser(
            username='admin',
            email='admin@barbershop.com',
            password='admin123',
            first_name='Admin',
            last_name='User'
        )
        UserProfile.objects.create(user=admin, role='admin', phone='09171234567')
        self.stdout.write(self.style.SUCCESS("✓ Created admin: username='admin', password='admin123'"))
    
    def create_barbers(self):
        self.stdout.write("\nCreating barber users...")
        
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
        for barber_data in barbers_data:
            user = User.objects.create_user(
                username=barber_data['username'],
                password=barber_data['password'],
                first_name=barber_data['first_name'],
                last_name=barber_data['last_name'],
                email=barber_data['email']
            )
            
            UserProfile.objects.create(
                user=user,
                role='barber',
                phone=barber_data['phone']
            )
            
            barber = Barber.objects.create(
                user=user,
                name=barber_data['name'],
                specialization=barber_data['specialization'],
                bio=barber_data['bio'],
                is_active=True
            )
            
            created_barbers.append({
                'barber': barber,
                'schedule': barber_data['schedule'],
                'username': barber_data['username']
            })
            
            self.stdout.write(self.style.SUCCESS(f"✓ Created barber: username='{barber_data['username']}', password='barber123'"))
        
        return created_barbers
    
    def create_availability(self, barbers):
        self.stdout.write("\nCreating barber availability schedules...")
        
        start_time = time(9, 0)
        end_time = time(18, 0)
        
        for barber_info in barbers:
            barber = barber_info['barber']
            schedule = barber_info['schedule']
            
            if schedule == 'mon-fri':
                days = [0, 1, 2, 3, 4]  # Monday to Friday
                schedule_text = "Monday to Friday"
            else:  # sun-wed
                days = [6, 0, 1, 2]  # Sunday, Monday, Tuesday, Wednesday
                schedule_text = "Sunday to Wednesday"
            
            for day in days:
                BarberAvailability.objects.create(
                    barber=barber,
                    day_of_week=day,
                    start_time=start_time,
                    end_time=end_time,
                    is_available=True
                )
            
            self.stdout.write(self.style.SUCCESS(f"✓ Set {barber.name} availability: {schedule_text}, 9 AM - 6 PM"))
    
    def create_services(self):
        self.stdout.write("\nCreating services...")
        
        services_data = [
            {
                'name': 'Classic Haircut',
                'description': 'Traditional haircut with scissors and clippers. Includes wash and basic styling.',
                'duration_minutes': 30,
                'price': 250.00
            },
            {
                'name': 'Premium Haircut & Styling',
                'description': 'Premium haircut with consultation, wash, cut, and professional styling.',
                'duration_minutes': 45,
                'price': 400.00
            },
            {
                'name': 'Beard Trim & Grooming',
                'description': 'Professional beard trimming and shaping with hot towel treatment.',
                'duration_minutes': 20,
                'price': 150.00
            },
            {
                'name': 'Haircut + Beard Combo',
                'description': 'Complete grooming package with haircut and beard trim.',
                'duration_minutes': 50,
                'price': 350.00
            },
            {
                'name': 'Kids Haircut',
                'description': 'Haircut for children 12 years and under.',
                'duration_minutes': 25,
                'price': 200.00
            },
            {
                'name': 'Hot Shave',
                'description': 'Traditional straight razor shave with hot towel and aftershave.',
                'duration_minutes': 30,
                'price': 300.00
            }
        ]
        
        for service_data in services_data:
            Service.objects.create(**service_data)
            self.stdout.write(self.style.SUCCESS(f"✓ Created service: {service_data['name']} - ₱{service_data['price']}"))
    
    def print_summary(self):
        self.stdout.write("\n" + "=" * 60)
        self.stdout.write(self.style.SUCCESS("DATABASE POPULATED SUCCESSFULLY!"))
        self.stdout.write("=" * 60)
        
        self.stdout.write("\n📋 ACCOUNT SUMMARY:")
        self.stdout.write("-" * 60)
        self.stdout.write("\n🔑 ADMIN ACCOUNT:")
        self.stdout.write("   Username: admin")
        self.stdout.write("   Password: admin123")
        self.stdout.write("   Email: admin@barbershop.com")
        
        self.stdout.write("\n💈 BARBER ACCOUNTS:")
        self.stdout.write("\n   Mon-Fri Barbers (Available Monday to Friday, 9 AM - 6 PM):")
        self.stdout.write("   1. Username: barber1 | Password: barber123")
        self.stdout.write("      Name: John Smith")
        self.stdout.write("      Specialization: Classic Cuts & Fades")
        self.stdout.write("   2. Username: barber2 | Password: barber123")
        self.stdout.write("      Name: Mike Johnson")
        self.stdout.write("      Specialization: Modern Styles & Beard Grooming")
        
        self.stdout.write("\n   Sun-Wed Barbers (Available Sunday to Wednesday, 9 AM - 6 PM):")
        self.stdout.write("   3. Username: barber3 | Password: barber123")
        self.stdout.write("      Name: Carlos Rodriguez")
        self.stdout.write("      Specialization: Trendy Cuts & Hair Coloring")
        self.stdout.write("   4. Username: barber4 | Password: barber123")
        self.stdout.write("      Name: David Lee")
        self.stdout.write("      Specialization: Precision Cuts & Styling")
        
        self.stdout.write("\n" + "=" * 60)
