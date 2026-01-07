from django.http import HttpResponse, HttpRequest, JsonResponse
from django.shortcuts import render
from django.shortcuts import get_object_or_404, render, redirect
from django.http import Http404
from django.contrib import auth

from .models import User
from .forms import Signupform

def signup(request):
    
    if request.method == 'POST':
        form = Signupform(request.POST , request.FILES )
        if form.is_valid():
            username = form.cleaned_data['username']
            firstName = form.cleaned_data['firstName']
            lastName = form.cleaned_data['lastName']
            email = form.cleaned_data['email']
            dob = form.cleaned_data['date_of_birth']
            password = form.cleaned_data['password']
            displayPic = form.cleaned_data['displayPic']
            
            user = User.objects.create_user(
                
                username=username,
                email=email,
                password=password,
                firstName=firstName,
                lastName=lastName,
                dob=dob,
                displayPic = displayPic
            )
            
               
              
            
            return redirect('login')
    else:
        form = Signupform()

    return render(request, 'registration/signup.html', {'form': form})


    




def main_spa(request: HttpRequest) -> HttpResponse:
    return render(request, 'api/spa/index.html', {})
