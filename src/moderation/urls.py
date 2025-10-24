from django.urls import path
from .views import submit_review

urlpatterns = [
    path("reviews/", submit_review, name="submit_review"),
]
