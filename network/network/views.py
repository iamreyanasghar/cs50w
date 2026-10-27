from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.db import IntegrityError
from django.contrib import messages
from django.urls import reverse
from django.contrib.auth.models import User


from .models import User, Post, Follow


def index(request):
    posts = Post.objects.all().order_by("id").reverse()

    return render(request, "network/index.html", {
        "posts": posts
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
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


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
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")


@login_required
def new_post(request):
    if request.method == "POST":

        # collect data
        post = request.POST["new_post"]
        user = request.user

        # verify if user enter all required data
        if post:
            post = Post(
                content=post,
                user=user
            )

            post.save()
            messages.success(request, "Post posted successfully!")
            return redirect('index')

        else:
            messages.error(request, "Missing Required Fields! Please fill in all required fields.")
    
    return render(request, "network/new_post.html")


@login_required
def edit_post(request, id):
    post = Post.objects.get(id=id)

    if request.method == "POST":
        post = request.POST["new_post"]
        user = request.user

        if post:
            post = Post(
                    content=post.content,
                    user=user
            )

            post.save()
            messages.success(request, "Post edited successfully!")

        else:
            message.error(request, "Missing Required Fields! Please fill in all required fields.")

    return render(request, "network/edit_post.html",{
        "post": post
    })


def profile(request, id):
    user = User.objects.get(id=id)
    posts =  Post.objects.filter(user=user).order_by("id").reverse()

    following = Follow.objects.filter(follower=user)
    followers = Follow.objects.filter(followed=user)

    # let user is not following
    current_user = Follow.objects.filter(followed=user)
    if current_user:
        is_following = True

    else:
        is_following = False

    return render(request, "network/profile.html", {
            "posts": posts,
            "following": following,
            "followers": followers,
            "user_profile": user,
            "isFollowing": is_following,
            "current": current_user
        })



def follow(request, id):
    user_to_follow = get_object_or_404(User, id=id)
    current_user = request.user

    print(f"id: {id}, current_user: {current_user.id}, user_to_follow: {user_to_follow.id}")

    follow_relation = Follow(
        follower=current_user,
        followed=user_to_follow
    )

    follow_relation.save()

    return redirect('profile', id=id)


def unfollow(request, id):
    user_to_unfollow = get_object_or_404(User, id=id)
    current_user = request.user

    Follow.objects.filter(
        follower__id=current_user.id, 
        followed__id=user_to_unfollow.id
    ).delete()
                                
    return redirect('profile', id=id)

@login_required
def following(request, id):
    user = User.objects.get(id=id)
    following = Follow.objects.filter(follower=user)

    ids = list(following.values_list("followed", flat=True))
    
    # negative sign does the work of arranging in descending order instead of default ascending
    posts = Post.objects.filter(user__in=ids).order_by("-id")   

    return render(request, "network/following.html", {
        "posts": posts
    })
