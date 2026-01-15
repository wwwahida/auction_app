"""project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.contrib import admin
from django.urls import include, path, re_path
from django.http import HttpResponse
from django.contrib.auth import views as auth_views
from django.views.static import serve

from .views import addItem, session_status, signup , getItems, profile, logout_api, change_password,getitemDetails, search_items, place_bid, item_forum, post_question, post_reply


urlpatterns = [
    path("session/", session_status, name="session-status"),
    path('signup/', signup, name='signup'),
    path('add-item/', addItem, name='add-item'),
    path('get-items/', getItems, name='get-items'),
    path('profile/', profile, name='profile'),
    path("logout/", logout_api, name="logout-api"),
    path("change-password/", change_password, name="change-password"),
    path("search-items/", search_items, name="search-items"),
    path("place-bid/", place_bid, name="place-bid"),
    path("item/<int:item_id>/",getitemDetails, name='get_item_details'),
    path("item/<int:item_id>/forum/", item_forum, name="item-forum"),
    path("item/<int:item_id>/questions/", post_question, name="post-question"),
    path("questions/<int:question_id>/replies/", post_reply, name="post-reply"),
    re_path(r"^media/(?P<path>.*)$", serve, {"document_root": settings.MEDIA_ROOT})
]

