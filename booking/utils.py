# booking/utils.py

from datetime import datetime, time, timedelta
from .models import Appointment
from barbers.models import BarberAvailability


def generate_time_slots(start_time=time(9, 0), end_time=time(18, 0), interval_minutes=30, lunch_break=True):
    """
    Generate time slots for booking.
    
    Args:
        start_time: Start of business hours (default 9:00 AM)
        end_time: End of business hours (default 6:00 PM)
        interval_minutes: Slot duration in minutes (default 30)
        lunch_break: Whether to skip lunch hour 12-1 PM (default True)
    
    Returns:
        List of time objects representing available slots
    """
    slots = []
    current = datetime.combine(datetime.today(), start_time)
    end = datetime.combine(datetime.today(), end_time)
    
    while current < end:
        slot_time = current.time()
        
        # Skip lunch break (12:00 PM - 1:00 PM)
        if lunch_break and time(12, 0) <= slot_time < time(13, 0):
            current += timedelta(minutes=interval_minutes)
            continue
        
        slots.append(slot_time)
        current += timedelta(minutes=interval_minutes)
    
    return slots


def get_available_slots(barber, date, service=None):
    """
    Get available time slots for a specific barber on a specific date.
    
    Args:
        barber: Barber instance
        date: Date object for the appointment
        service: Service instance (optional, for duration calculation)
    
    Returns:
        List of dictionaries with time and availability status
    """
    # Generate all possible time slots
    all_slots = generate_time_slots()
    
    # Get day of week (0=Monday, 6=Sunday)
    day_of_week = date.weekday()
    
    # Check if barber is available on this day
    try:
        barber_availability = BarberAvailability.objects.get(
            barber=barber,
            day_of_week=day_of_week,
            is_available=True
        )
    except BarberAvailability.DoesNotExist:
        # Barber not available on this day
        return [{'time': slot, 'available': False, 'reason': 'Barber not working'} for slot in all_slots]
    
    # Get existing appointments for this barber on this date
    existing_appointments = Appointment.objects.filter(
        barber=barber,
        appointment_date=date,
        status__in=['pending', 'confirmed']
    ).values_list('appointment_time', flat=True)
    
    booked_times = set(existing_appointments)
    
    # Build available slots list
    available_slots = []
    for slot in all_slots:
        # Check if within barber's working hours
        if slot < barber_availability.start_time or slot >= barber_availability.end_time:
            available_slots.append({
                'time': slot,
                'available': False,
                'reason': 'Outside working hours'
            })
        # Check if already booked
        elif slot in booked_times:
            available_slots.append({
                'time': slot,
                'available': False,
                'reason': 'Already booked'
            })
        else:
            available_slots.append({
                'time': slot,
                'available': True,
                'reason': None
            })
    
    return available_slots


def check_slot_availability(barber, date, time_slot):
    """
    Check if a specific time slot is available for booking.
    
    Args:
        barber: Barber instance
        date: Date object
        time_slot: Time object
    
    Returns:
        Tuple (is_available: bool, reason: str)
    """
    # Check if date is in the past
    if date < datetime.now().date():
        return False, "Cannot book appointments in the past"
    
    # Check if same day and time is in the past
    if date == datetime.now().date() and time_slot <= datetime.now().time():
        return False, "Time slot has passed"
    
    # Get day of week
    day_of_week = date.weekday()
    
    # Check barber availability for this day
    try:
        barber_availability = BarberAvailability.objects.get(
            barber=barber,
            day_of_week=day_of_week,
            is_available=True
        )
        
        if time_slot < barber_availability.start_time or time_slot >= barber_availability.end_time:
            return False, "Outside barber's working hours"
    except BarberAvailability.DoesNotExist:
        return False, "Barber not available on this day"
    
    # Check if slot is already booked
    existing = Appointment.objects.filter(
        barber=barber,
        appointment_date=date,
        appointment_time=time_slot,
        status__in=['pending', 'confirmed']
    ).exists()
    
    if existing:
        return False, "Time slot already booked"
    
    return True, "Available"


def format_time_slot(time_obj):
    """Format time object to 12-hour format string."""
    return time_obj.strftime('%I:%M %p')


def get_appointment_end_time(start_time, duration_minutes):
    """
    Calculate appointment end time.
    
    Args:
        start_time: Time object for appointment start
        duration_minutes: Duration in minutes
    
    Returns:
        Time object for appointment end
    """
    start_datetime = datetime.combine(datetime.today(), start_time)
    end_datetime = start_datetime + timedelta(minutes=duration_minutes)
    return end_datetime.time()
