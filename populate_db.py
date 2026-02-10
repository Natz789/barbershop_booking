# populate_db.py - Script to populate database with test data

from django.contrib.auth.models import User
from accounts.models import UserProfile
from barbers.models import Barber, BarberAvailability
from services.models import Service

def create_users_and_profiles():
    """Create admin and barber users"""
    print("Creating users...")
    
    # Create admin user
    admin = User.objects.create_superuser(
        username='admin',
        email='admin@barbershop.com',
        password='admin123',
        first_name='Admin',
        last_name='User'
    )
    UserProfile.objects.create(user=admin, role='admin', phone='09171234567')
    print(f"✓ Created admin: username='admin', password='admin123'")
    
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
            'schedule': 'mon-fri'  # Monday to Friday
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
            'schedule': 'mon-fri'  # Monday to Friday
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
            'schedule': 'sun-wed'  # Sunday to Wednesday
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
            'schedule': 'sun-wed'  # Sunday to Wednesday
        }
    ]
    
    created_barbers = []
    for barber_data in barbers_data:
        # Create user
        user = User.objects.create_user(
            username=barber_data['username'],
            password=barber_data['password'],
            first_name=barber_data['first_name'],
            last_name=barber_data['last_name'],
            email=barber_data['email']
        )
        
        # Create user profile
        UserProfile.objects.create(
            user=user,
            role='barber',
            phone=barber_data['phone']
        )
        
        # Create barber profile
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
        
        print(f"✓ Created barber: username='{barber_data['username']}', password='barber123'")
    
    return created_barbers


def create_barber_availability(barbers):
    """Create availability schedules for barbers"""
    print("\nCreating barber availability schedules...")
    
    # Working hours: 9 AM to 6 PM
    from datetime import time
    start_time = time(9, 0)
    end_time = time(18, 0)
    
    for barber_info in barbers:
        barber = barber_info['barber']
        schedule = barber_info['schedule']
        
        if schedule == 'mon-fri':
            # Monday (0) to Friday (4)
            days = [0, 1, 2, 3, 4]
            schedule_text = "Monday to Friday"
        else:  # sun-wed
            # Sunday (6), Monday (0), Tuesday (1), Wednesday (2)
            days = [6, 0, 1, 2]
            schedule_text = "Sunday to Wednesday"
        
        for day in days:
            BarberAvailability.objects.create(
                barber=barber,
                day_of_week=day,
                start_time=start_time,
                end_time=end_time,
                is_available=True
            )
        
        print(f"✓ Set {barber.name} availability: {schedule_text}, 9 AM - 6 PM")


def create_services():
    """Create barbershop services"""
    print("\nCreating services...")
    
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
        print(f"✓ Created service: {service_data['name']} - ₱{service_data['price']}")


def run():
    """Main function to populate database"""
    print("=" * 60)
    print("POPULATING DATABASE WITH TEST DATA")
    print("=" * 60)
    
    # Create users and barbers
    barbers = create_users_and_profiles()
    
    # Create barber availability
    create_barber_availability(barbers)
    
    # Create services
    create_services()
    
    print("\n" + "=" * 60)
    print("DATABASE POPULATED SUCCESSFULLY!")
    print("=" * 60)
    
    print("\n📋 ACCOUNT SUMMARY:")
    print("-" * 60)
    print("\n🔑 ADMIN ACCOUNT:")
    print("   Username: admin")
    print("   Password: admin123")
    print("   Email: admin@barbershop.com")
    
    print("\n💈 BARBER ACCOUNTS:")
    print("\n   Mon-Fri Barbers:")
    print("   1. Username: barber1 | Password: barber123 | Name: John Smith")
    print("      Specialization: Classic Cuts & Fades")
    print("   2. Username: barber2 | Password: barber123 | Name: Mike Johnson")
    print("      Specialization: Modern Styles & Beard Grooming")
    
    print("\n   Sun-Wed Barbers:")
    print("   3. Username: barber3 | Password: barber123 | Name: Carlos Rodriguez")
    print("      Specialization: Trendy Cuts & Hair Coloring")
    print("   4. Username: barber4 | Password: barber123 | Name: David Lee")
    print("      Specialization: Precision Cuts & Styling")
    
    print("\n✅ All barbers work 9 AM - 6 PM on their scheduled days")
    print("=" * 60)


if __name__ == '__main__':
    run()
