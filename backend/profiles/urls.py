from rest_framework import routers
from .views import ProfileViewSet
from django.urls import path, include

router = routers.DefaultRouter()
router.register(r'profiles', ProfileViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
