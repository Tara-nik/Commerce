from django import forms
from .models import AuctionListing, Bid, Comment, Category


class ListingForm(forms.ModelForm):

    class Meta:
        model = AuctionListing
        fields = ['title', 'description', 'start_price', 'image_url']

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['category']


class BidForm(forms.ModelForm):
    class Meta:
        model = Bid
        fields = ['new_price']


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text', 'user']


