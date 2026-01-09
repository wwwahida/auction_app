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
from django.contrib.auth import logout
from django.views.decorators.http import require_POST
import json
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
import json
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError



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
    


class ProfilePayload(TypedDict):
    username: str
    firstName: str
    lastName: str
    email: str
    dob: str
    displayPic: Optional[str]


def _profile_to_payload(user: User, request: HttpRequest) -> ProfilePayload:
    display_url: Optional[str] = None
    if user.displayPic:
        display_url = request.build_absolute_uri(user.displayPic.url)

    return {
        "username": user.username,
        "firstName": user.firstName,
        "lastName": user.lastName,
        "email": user.email,
        "dob": user.dob.isoformat(),
        "displayPic": display_url,
    }


@login_required
def profile(request: HttpRequest) -> JsonResponse:
    user: User = request.user 

    if request.method == "GET":
        return JsonResponse(_profile_to_payload(user, request))

    if request.method != "POST":
        return JsonResponse({"error": "GET or POST required"}, status=405)

    # Read fields 
    username = request.POST.get("username", user.username).strip()
    first_name = request.POST.get("firstName", user.firstName).strip()
    last_name = request.POST.get("lastName", user.lastName).strip()
    email = request.POST.get("email", user.email).strip()
    dob_str = request.POST.get("dob", user.dob.isoformat()).strip()

    # Basic validation
    if not username:
        return JsonResponse({"error": "Username cannot be empty."}, status=400)
    if not email:
        return JsonResponse({"error": "Email cannot be empty."}, status=400)

    # Uniqueness checks
    if User.objects.filter(username=username).exclude(pk=user.pk).exists():
        return JsonResponse({"error": "Username is already in use."}, status=400)

    if User.objects.filter(email=email).exclude(pk=user.pk).exists():
        return JsonResponse({"error": "Email is already in use."}, status=400)

    # Date of birth parsing and validation
    try:
        dob_val = date.fromisoformat(dob_str)
    except ValueError:
        return JsonResponse({"error": "Invalid date of birth."}, status=400)

    if dob_val > date.today():
        return JsonResponse({"error": "Date of birth cannot be in the future."}, status=400)

    # Update user fields
    user.username = username
    user.firstName = first_name
    user.lastName = last_name
    user.email = email
    user.dob = dob_val

    # Handle display picture upload
    if "displayPic" in request.FILES:
        user.displayPic = request.FILES["displayPic"]

    user.save()

    return JsonResponse(_profile_to_payload(user, request))

        
@login_required
@require_POST
def logout_api(request: HttpRequest) -> JsonResponse:
    logout(request)
    return JsonResponse({"message": "Logged out"})
    
@login_required
@require_POST
def change_password(request: HttpRequest) -> JsonResponse:
    try:
        data = json.loads(request.body.decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError):
        return JsonResponse({"error": "Invalid JSON body."}, status=400)

    new_password = str(data.get("newPassword", "")).strip()
    confirm_password = str(data.get("confirmPassword", "")).strip()

    if not new_password or not confirm_password:
        return JsonResponse({"error": "Both password fields are required."}, status=400)

    if new_password != confirm_password:
        return JsonResponse({"error": "Passwords do not match."}, status=400)

    user: User = request.user  # type: ignore[assignment]

    try:
        validate_password(new_password, user=user)
    except ValidationError as e:
        return JsonResponse({"error": " ".join(e.messages)}, status=400)

    user.set_password(new_password)
    user.save()

    # keep them logged in after password change
    update_session_auth_hash(request, user)

    return JsonResponse({"message": "Password updated"})
