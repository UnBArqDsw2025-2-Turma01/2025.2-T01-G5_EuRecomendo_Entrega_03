# config/urls.py
from django.contrib import admin
from django.urls import path
from recommendations.api import RecommendMeView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/recommendations/<int:user_id>/', RecommendMeView.as_view()),
]
