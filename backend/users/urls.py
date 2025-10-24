from rest_framework import routers
from .views import UserProfileViewSet
from django.urls import path, include

router = routers.DefaultRouter()
router.register(r'users', UserProfileViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
