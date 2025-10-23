from django.urls import path
from . import views

app_name = "biblioteca"

urlpatterns = [
    path("", views.index, name="index"),
    path("home/", views.index, name="home"),
    path("livros/", views.lista_livros, name="lista_livros"),
]
