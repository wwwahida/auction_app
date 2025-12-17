from django import forms
from datetime import datetime

class Signupform(forms.Form):
    displayPic = forms.ImageField(
        label='Display picture',
        required=False,
        widget=forms.ClearableFileInput(attrs={'class': 'form-control-file'})
    )

    firstName = forms.CharField(
        label='First name',
        max_length=30,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter first name'})
    )   

    lastName = forms.CharField(
        label='Last name',
        max_length=30,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter last name'})
    )   

    date_of_birth = forms.DateField(
        label='Date of birth',
        widget=forms.DateInput(attrs={
            'type': 'date',
            'max': datetime.now().date(),
            'class': 'form-control'
        })
    )

    username = forms.CharField(
        label='Username',
        max_length=150,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter username'})
    )

    email = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter email'})
    )

    password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Enter password'})
    )

    confirmPassword = forms.CharField(
        label='Confirm password',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm password'})
    )
