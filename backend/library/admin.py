from django.contrib import admin
from .models import LibraryEntry


@admin.register(LibraryEntry)
class LibraryEntryAdmin(admin.ModelAdmin):
    list_display = ("user", "book", "status", "created_at")
    list_filter = ("status",)
    search_fields = ("user__username", "book__title")
