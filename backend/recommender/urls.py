from django.urls import path
from .views import RecommendView

urlpatterns = [
    path('recommend/', RecommendView.as_view(), name='recommend'),
]
