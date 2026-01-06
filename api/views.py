from django.http import HttpResponse, HttpRequest, JsonResponse
from django.shortcuts import render
from django.shortcuts import get_object_or_404, render, redirect
from django.http import Http404
from django.contrib import auth


from .models import User
from .forms import Signupform

def signup(request):
    """
    Minimal signup view.
    Stores username, email, date of birth, and password.
    Redirects to login page after successful signup.
    """
    form = Signupform()
    
    if request.method == 'POST':
        form = Signupform(request.POST, request.FILES)
        if form.is_valid():
            display_pic = request('displayPic')
            if not display_pic:
                # If no file was uploaded, set a default picture
                display_pic = 'profile_pics/default.png'
            first_name = form.cleaned_data['firstName']
            last_name = form.cleaned_data['lastName']
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            dob = form.cleaned_data['date_of_birth']
            password = form.cleaned_data['password']
            confirm_password = form.cleaned_data['confirmPassword']

            # Check if passwords match
            if password == confirm_password:
                try:
                    # Create the user
                    user = User.objects.create_user(
                        displayPic=display_pic,
                        firstName=first_name,
                        lastName=last_name,
                        username=username,
                        email=email,
                        dob=dob,
                        password=password
                    )
                    user.save()
                    # Redirect to login page
                    return redirect('mainapp:login')
                except Exception as e:
                    print(f"CRITICAL ERROR: {e}")
    else:
        form = Signupform()

    return render(request, 'registration/signup.html', {'form': form})
    
    




def main_spa(request: HttpRequest) -> HttpResponse:
    return render(request, 'api/spa/index.html', {})
