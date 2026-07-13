from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create", views.create, name="create"),
    path("listing/<int:id>", views.get_listing, name="listing"),
    path("categories", views.categories, name="categories"),
    path("categories/<str:cat>", views.get_cat, name="get_cat"),
    path("watchlist", views.watchlist, name="watchlist"),
]