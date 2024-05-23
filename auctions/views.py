from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.db import IntegrityError
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render, get_object_or_404, redirect, get_list_or_404
from django.core.exceptions import MultipleObjectsReturned
from django.urls import reverse
from django.utils import timezone
from django.contrib import messages
from .models import User, AuctionListing, Bid, Comment, Category, Watchlist
from .forms import ListingForm, BidForm, CommentForm, CategoryForm


def index(request):
    return render(request, "auctions/index.html")

def login_view(request):
    if request.method == "POST":

        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)


        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")


@login_required
def add_to_watchlist(request, listing_id):
    listing = get_object_or_404(AuctionListing, pk=listing_id)
    try:

        request.user.watchlist.watched_items.add(listing)
    except Exception as e:

        print(f"Error adding listing to watchlist: {e}")

    return redirect('watchlist')


@login_required
def watchlist(request):
    user_watchlist, created = Watchlist.objects.get_or_create(user=request.user)

    return render(request, 'auctions/watchlist.html', {'watchlist': user_watchlist.watched_items.all()})

@login_required
def delete_watchlist(request, listing_id):
    listing = get_object_or_404(AuctionListing, pk=listing_id)
    watchlist = Watchlist.objects.get(user=request.user)

    if listing in watchlist.watched_items.all():
        watchlist.watched_items.remove(listing)

    return redirect('watchlist')



def categories(request):
    categories = Category.objects.values('category').distinct()
    print(f'Listing Categories: {categories}')
    return render(request, "auctions/category.html", {"categories": categories})

def category_listings(request, category):
    try:
        category_objects = Category.objects.filter(category=category)
    except MultipleObjectsReturned:
        category_objects = Category.objects.filter(category=category)

    listings = AuctionListing.objects.filter(categories__in=category_objects)

    return render(
        request,
        "auctions/category_listing.html",
        {"category_objects": category_objects, "listings": listings},
    )




def active_list(request):
    titles = AuctionListing.objects.filter(available=True)
    return render(request, "auctions/active_list.html", {"titles": titles})

@login_required
def detail_list(request, title):
    listing = get_object_or_404(AuctionListing, title=title)
    comments = Comment.objects.filter(listing=listing)
    categories = listing.categories.all()
    bids = Bid.objects.filter(listing=listing)

    max_bid = bids.order_by('-new_price').first()

    print(f'category: {categories}')
    print(f'winner: {listing.winner}')
    print(f'title: {listing.title}')

    return render(request, "auctions/detail_list.html", {"listing": listing, "title": title, "comments": comments, "categories": categories, "bids": bids, "max_bid": max_bid})



@login_required
def comment(request, title):
    listing = get_object_or_404(AuctionListing, title=title)

    if request.method == 'POST':
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.listing = listing
            comment.user = request.user
            comment.save()
            return redirect('detail_list', title=title)
    else:
        comment_form = CommentForm()
    return render(request, "auctions/comment.html", {"comment_form": comment_form, "listing": listing})
@login_required
def create_listing(request):
    categories = Category.objects.all()

    if request.method == 'POST':
        form = ListingForm(request.POST, request.FILES)
        bid_form = BidForm(request.POST)
        category_form = CategoryForm(request.POST)

        if form.is_valid() and bid_form.is_valid() and category_form.is_valid():
            listing = form.save(commit=False)
            category = category_form.save(commit=False)

            if request.user.is_authenticated:
                listing.created_by = request.user
                listing.save()

                category.save()
                listing.categories.add(category)

                bid = bid_form.save(commit=False)
                bid.listing = listing
                bid.bidder = request.user
                bid.save()

                return redirect("index")

    else:
        form = ListingForm()
        bid_form = BidForm()
        category_form = CategoryForm()

    return render(request, 'auctions/create_listing.html', {'form': form, 'bid_form': bid_form, 'category_form': category_form, 'categories': categories})





@login_required
def bid(request, listing_id):
    listing = get_object_or_404(AuctionListing, id=listing_id)

    bids = Bid.objects.filter(listing=listing)
    max_bid = bids.order_by('-new_price').first()

    if not listing.available:
        listing.save()

    if request.method == 'POST':
        form = BidForm(request.POST)
        if form.is_valid():
            new_price = form.cleaned_data['new_price']
            if new_price > listing.current_price:
                Bid.objects.create(bidder=request.user, listing=listing, new_price=new_price)
                listing.current_price = new_price

                if max_bid:
                    listing.winner = max_bid.bidder

                listing.save()
                messages.success(request, 'Bid placed successfully!')
                return redirect('detail_list', title=listing.title)
            else:
                messages.error(request, 'Bid amount must be higher than the current price.')
    else:
        form = BidForm()

    return render(request, 'auctions/bid.html', {'form': form, 'listing': listing})



@login_required(login_url='login')
def close(request, listing_id):
    auction = get_object_or_404(AuctionListing, pk=listing_id)
    bid = Bid.objects.filter(listing_id=listing_id).order_by('-timestamp').first()

    if bid:
        auction.winner = bid.bidder
        auction.current_price = bid.new_price

        print(f'price: {auction.current_price}')
        print(f'winner: {auction.winner}')

    if request.method == 'POST':
        if request.user == auction.created_by:
            auction.available = False
            auction.save()

            return render(request, 'auctions/close.html', {"winner": auction.winner, "current_price": auction.current_price})
    
def closed_listing(request):
    closed_listing = AuctionListing.objects.filter(available=False)
    return render(request, "auctions/close_listing.html", {
        "closed_listing": closed_listing
    })



