from django import forms
from datetime import datetime
from .models import User

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
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Email is already in use.")
        return email
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Username is already in use.")
        return username
    
    def clean(self):
        cleaned_data = super().clean()
        password = self.cleaned_data.get('password')
        confirm_password = self.cleaned_data.get('confirmPassword')

        if password != confirm_password:
            self.add_error("confirmPassword", "Passwords do not match.")
        
        return cleaned_data