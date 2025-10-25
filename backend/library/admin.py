from django.contrib import admin
from .models import ReadingList

class ReadListAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'owner', 'books_list')

    def books_list(self, obj):
        # Make sure to access 'title' or your actual Book field
        return ", ".join([book.title for book in obj.books.all()]) or "—"

    books_list.short_description = "Books"

admin.site.register(ReadingList, ReadListAdmin)