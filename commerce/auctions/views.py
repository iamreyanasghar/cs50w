from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import User, Listing, Bid, Comment


def index(request):
    return render(request, "auctions/index.html", {
        "listings": Listing.objects.filter(active=True)
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
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

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
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
def create(request):
    if request.method == "POST":
        title = request.POST.get("title")
        description = request.POST.get("description")
        price = request.POST.get("price")
        image = request.FILES.get("image")
        category = request.POST.get("category")

        if title and description and price:
            try:
                listing = Listing(
                    user=request.user,
                    title=title,
                    description=description,
                    price=float(price),
                    starting_price=float(price),
                    category=category if category else None,
                    active=True
                )
                
                if image:
                    listing.image = image
                
                listing.save()
                
                messages.success(request, "Listing created successfully!")
                return redirect('index')
                
            except ValueError:
                messages.error(request, "Please enter a valid number for the price.")
            except Exception as e:
                messages.error(request, f"Error creating listing: {str(e)}")
        else:
            messages.error(request, "Missing Required Fields! Please fill in all required fields.")
    
    return render(request, "auctions/create.html")

@login_required
def watchlist(request):
    listings = request.user.watchlist.all()
    return render(request, "auctions/watchlist.html", {
        "listings": listings
    })


def categories(request):
    return render(request, "auctions/categories.html", {
        "categories": Listing.objects.values_list('category', flat=True).distinct()
    })


def get_cat(request, cat):
    listing = Listing.objects.filter(category=cat, active=True)

    return render(request, "auctions/get_cat.html", {
        "listings": listing,
        "category": cat
    })


@login_required
def get_listing(request, id):
    listing = get_object_or_404(Listing, id=id)
    user = request.user

    if listing.active:

        if request.method == "POST":
            close = request.POST.get("close")
            bid = request.POST.get("bid")
            comment = request.POST.get("comment")
            add = request.POST.get("add")
            remove = request.POST.get("remove")
        
    
            if close:
                listing.active = False
                highest_bid = listing.bids.order_by('-bid_price').first()
    
                if highest_bid:
                    listing.winner = highest_bid.user
    
                listing.save()
                
                return redirect('index')
    
            if bid:
                try:
                    bid_amount = int(bid)
                    if bid_amount > listing.price:
                        # Create a new bid
                        new_bid = Bid(
                            listing=listing,
                            user=request.user,
                            bid_price=bid_amount
                        )
                        new_bid.save()
                        
                        # Update the listing price to the new highest bid
                        listing.price = bid_amount
                        listing.save()
                        
                        messages.success(request, "Bid placed successfully!")
                    else:
                        messages.error(request, "Bid must be higher than current price.")
                except ValueError:
                    messages.error(request, "Please enter a valid number.") 

            if comment:
                new_comment = Comment(
                    listing=listing,
                    user=request.user,
                    comment=comment
                )

                new_comment.save()

            if add:
                if not user.watchlist.filter(id=listing.id).exists():
                    user.watchlist.add(listing)
                    messages.success(request, "Added to watchlist!")
                return redirect('listing', id=listing.id)
            if remove:
                if user.watchlist.filter(id=listing.id).exists():
                    user.watchlist.remove(listing)
                    messages.success(request, "Removed from watchlist!")
                return redirect('listing', id=listing.id)

    return render(request, "auctions/listing.html", {
        "listing": listing,
        "comments": listing.comments.all()
    })
