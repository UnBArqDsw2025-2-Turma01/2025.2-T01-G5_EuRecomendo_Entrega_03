from rest_framework import routers
from .views import ReadingListViewSet
from django.urls import path, include

router = routers.DefaultRouter()
router.register(r'reading-lists', ReadingListViewSet)

urlpatterns = [
    path('', include(router.urls)),
]