from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('users.urls')),
    path('api/', include('profiles.urls')),
    path('api/', include('books.urls')),
    path('api/', include('reviews.urls')),
    path('api/', include('recommender.urls')),
    path('api/', include('library.urls')),
]
