from rest_framework import routers
from django.urls import path, include
from .views import LibraryEntryViewSet

router = routers.DefaultRouter()
router.register(r'library', LibraryEntryViewSet, basename='library')

urlpatterns = [
    path('', include(router.urls)),
]
