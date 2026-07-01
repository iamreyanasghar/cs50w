from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

    def __str__(self):
        return self.username


class Listing(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="listings")
    title = models.CharField(max_length=64)
    price = models.IntegerField()
    created = models.DateTimeField(auto_now_add=True)
    description = models.CharField(max_length=500)
    image = models.ImageField(upload_to="listing_images/", blank=True, null=True)
    active = models.BooleanField(default=True)
    category = models.CharField(max_length=64, blank=True, null=True)
    winner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="won_listings")
    
    def __str__(self):
        return f"{self.title} - ${self.price}"


class Bid(models.Model):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="bids")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bids")
    bid_price = models.IntegerField()
    time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} bid ${self.bid_price} on {self.listing.title}"


class Comment(models.Model):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="comments")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
    comment = models.CharField(max_length=150)
    time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Commented by {self.user.username} on {self.listing.title}"