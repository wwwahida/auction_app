from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings

# Create your models here.
class User(AbstractUser):
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)
    username = models.CharField(max_length=50, unique=True)
    firstName = models.CharField(max_length=30)
    lastName = models.CharField(max_length=30)
    dob = models.DateField()
    displayPic = models.ImageField(upload_to='display_pics/', null=True, blank=True)
    
    REQUIRED_FIELDS = ['email', 'dob', 'firstName', 'lastName']

 
class AuctionListing(models.Model):
    title = models.CharField(max_length=100)   
    description = models.TextField()
    startingPrice = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="The minimum starting price for the auction."
    )
    picture = models.ImageField(
        upload_to='listing_images/',
        null=True,
        blank=True
    )
    finishTime = models.DateTimeField(
        help_text="The date and time the auction will end."
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="listings"
    )
    

class Bid(models.Model):
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="The amount you are bidding."
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="bids"
    )
    auctionItem = models.ForeignKey(
        AuctionListing,
        on_delete=models.CASCADE,
        related_name="bids"
    )


class PageView(models.Model):
    count = models.IntegerField(default=0)

    def __str__(self):
        return f"Page view count: {self.count}"