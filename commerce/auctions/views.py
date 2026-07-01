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
        price = request.POST.get("bid")
        image = request.FILES.get("image")
        category = request.POST.get("category")

        if title and description and price:
            try:
                listing = Listing(
                    user=request.user,
                    title=title,
                    description=description,
                    price=int(price),
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


def watchlist(request):
    return render(request, "auctions/watchlist.html")


def categories(request):
    return render(request, "auctions/categories.html")


def get_listing(request, id):
    listing = get_object_or_404(Listing, id=id, active=True)

    if request.method == "POST":
        close = request.POST.get("close")
        bid = request.POST.get("bid")

        if close:
            listing.active = False
            highest_bid = listing.bids.order_by('-amount').first()

            listing.save()
            
            return redirect('index')

        if bid:
            if int(bid) > listing.price:
                listing.bid = bid
                listing.save()

            else:
                pass          


    return render(request, "auctions/listing.html", {
        "listing": listing
    })
