/* booking.js - Dynamic booking functionality */

document.addEventListener('DOMContentLoaded', function() {
    const barberSelect = document.getElementById('id_barber');
    const dateInput = document.getElementById('id_appointment_date');
    const timeInput = document.getElementById('id_appointment_time');
    const timeSlotsContainer = document.getElementById('time-slots-container');
    
    if (!barberSelect || !dateInput) return;
    
    // Load time slots when barber or date changes
    barberSelect.addEventListener('change', loadTimeSlots);
    dateInput.addEventListener('change', loadTimeSlots);
    
    function loadTimeSlots() {
        const barberId = barberSelect.value;
        const date = dateInput.value;
        
        if (!barberId || !date) {
            timeSlotsContainer.innerHTML = '<p class="info-message">Please select a barber and date to see available time slots.</p>';
            return;
        }
        
        // Show loading state
        timeSlotsContainer.innerHTML = '<div class="loading-spinner"><div class="spinner"></div><p>Loading available slots...</p></div>';
        
        // Fetch available slots
        fetch(`/booking/api/available-slots/?barber_id=${barberId}&date=${date}`)
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    timeSlotsContainer.innerHTML = `<p class="error-message">${data.error}</p>`;
                    return;
                }
                
                displayTimeSlots(data.slots);
            })
            .catch(error => {
                console.error('Error fetching time slots:', error);
                timeSlotsContainer.innerHTML = '<p class="error-message">Failed to load time slots. Please try again.</p>';
            });
    }
    
    function displayTimeSlots(slots) {
        if (slots.length === 0) {
            timeSlotsContainer.innerHTML = '<p class="info-message">No time slots available for this date.</p>';
            return;
        }
        
        let html = '<div class="time-slots-grid">';
        
        slots.forEach(slot => {
            const isAvailable = slot.available;
            const className = isAvailable ? 'time-slot available' : 'time-slot unavailable';
            const disabled = isAvailable ? '' : 'disabled';
            const title = slot.reason || 'Available';
            
            html += `
                <button type="button" 
                        class="${className}" 
                        data-time="${slot.time}"
                        ${disabled}
                        title="${title}">
                    ${slot.display}
                </button>
            `;
        });
        
        html += '</div>';
        timeSlotsContainer.innerHTML = html;
        
        // Add click handlers to available slots
        document.querySelectorAll('.time-slot.available').forEach(button => {
            button.addEventListener('click', function() {
                // Remove selected class from all slots
                document.querySelectorAll('.time-slot').forEach(btn => {
                    btn.classList.remove('selected');
                });
                
                // Add selected class to clicked slot
                this.classList.add('selected');
                
                // Set the hidden time input value
                timeInput.value = this.dataset.time;
                
                // Hide the original time input (it's now set programmatically)
                if (timeInput.parentElement) {
                    timeInput.parentElement.style.display = 'none';
                }
            });
        });
    }
    
    // Initialize on page load if values are already set
    if (barberSelect.value && dateInput.value) {
        loadTimeSlots();
    }
});
