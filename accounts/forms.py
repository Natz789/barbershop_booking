# accounts/forms.py

from django import forms
from django.contrib.auth.forms import UserCreationForm

class RegistrationForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add CSS classes to all fields
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'
