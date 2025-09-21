from django import forms
from .models import Address,Review
from django.contrib.auth.models import User

class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = ['full_name', 'address_line1', 'address_line2', 'city', 'state', 'postal_code', 'phone']

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}),
        }