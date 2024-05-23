from django.contrib.auth.models import AbstractUser, Group, Permission, User
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone



class User(AbstractUser):
    groups = models.ManyToManyField(Group, related_name='auctions_users')
    user_permissions = models.ManyToManyField(Permission, related_name='auctions_users_permissions')







class AuctionListing(models.Model):
    title = models.CharField(max_length=255, default='unknown')
    description = models.TextField()
    start_price = models.DecimalField(max_digits=10, decimal_places=2, default=1.00)
    current_price = models.DecimalField(max_digits=10, decimal_places=2, default=2.00)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='auction_listings')
    created_at = models.DateTimeField(auto_now_add=True)
    categories = models.ManyToManyField('Category', related_name='auction_listings')
    starting_bid = models.DecimalField(max_digits=10, decimal_places=2, default=2.00)
    image_url = models.URLField(default='https://example.com/placeholder.jpg')
    comments = models.ManyToManyField('Comment', related_name='auction_listings')
    winner = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    available = models.BooleanField(default=True)

    def __str__(self):
        return f'{self.title}'


class Category(models.Model):
    CATEGORY_NAME = [
        ("Art", "art"),
        ("Education", "educational"),
        ("Digital", "digi"),
        ("Antique", "antique"),
        ("Toys", "toy"),
        ("Games", "game"),
        ("Sports", "sport"),
    ]
    category = models.CharField(max_length=10, choices=CATEGORY_NAME)
    # listing = models.ForeignKey(AuctionListing, on_delete=models.CASCADE)

    def __str__(self):
        return f"Category: {self.category}"





class Watchlist(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='watchlist')
    watched_items = models.ManyToManyField('AuctionListing', blank=True)



class Bid(models.Model):

    bidder = models.ForeignKey(User, on_delete=models.CASCADE)
    listing = models.ForeignKey(AuctionListing, on_delete=models.CASCADE)
    new_price = models.DecimalField(max_digits=10, decimal_places=1)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Bid of ${self.new_price} on {self.listing}"


class Comment(models.Model):
    text = models.TextField()
    listing = models.ForeignKey(AuctionListing, on_delete=models.CASCADE, default=None)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f'Comment {self.text} by {self.user.username} on {self.listing.title}'



# Create your models here.
