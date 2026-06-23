from django.urls import path

from . import views


urlpatterns = [
    path("", views.index, name="index"),
    path("wiki/edit/<str:title>", views.edit, name="edit"),
    path("wiki/<str:title>", views.get_page, name="get"),
    path("create", views.create, name="create"),
    path("search", views.search, name="search"),
    path("random", views.random, name="random")
]


