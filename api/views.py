from django.conf import settings
from django.http import HttpResponse, HttpRequest, JsonResponse
from django.shortcuts import render
from django.shortcuts import get_object_or_404, render, redirect
from django.http import Http404
from django.contrib import auth
from django.utils.timezone import now
from datetime import date
from typing import Any, Optional, TypedDict
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import ensure_csrf_cookie



from .models import User , AuctionListing
from .forms import Signupform

def signup(request : HttpRequest) -> HttpResponse:
    
    if request.method == 'POST':
        form = Signupform(request.POST , request.FILES )
        if form.is_valid():
            username: str = form.cleaned_data['username']
            firstName: str = form.cleaned_data['firstName']
            lastName: str = form.cleaned_data['lastName']
            email: str = form.cleaned_data['email']
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


    
@login_required
@ensure_csrf_cookie
def main_spa(request: HttpRequest) -> HttpResponse:
    return render(request, 'api/spa/index.html', {})


def addItem(request:HttpRequest) -> JsonResponse:
    if request.method == "POST"  :
        title : str = request.POST["title"]
        description : str = request.POST["description"]
        startingPrice : float = float(request.POST["startingPrice"])
        picture = request.FILES["image"]
        finishTime = request.POST["endTime"]
        
        newItem = AuctionListing(title=title, description=description, startingPrice=startingPrice, picture=picture, finishTime=finishTime , user=request.user)
        newItem.save()
        
        return JsonResponse({"message": "Item added"})
    
    return JsonResponse({"error": "POST required"})

def getItems(request: HttpRequest) -> JsonResponse:
    if request.method == "GET":
        items = list(AuctionListing.objects.filter(finishTime__gt=now()).values("id", "title", "description" , "startingPrice", "picture", "finishTime"))
        
        for image in items:
            image["picture"] = request.build_absolute_uri(settings.MEDIA_URL + image["picture"])

        return JsonResponse({"items": items})
    



        
      