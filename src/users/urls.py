from django.urls import path
from .views import signup_view, demo_register_book_view

urlpatterns = [
    path("signup/", signup_view, name="signup"),
    path("register-book/", demo_register_book_view, name="register-book"), 
]
