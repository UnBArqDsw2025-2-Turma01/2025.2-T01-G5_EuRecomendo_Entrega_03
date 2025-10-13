from rest_framework import routers
from .views import BookViewSet
from django.urls import path, include

router = routers.DefaultRouter()
router.register(r'books', BookViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
