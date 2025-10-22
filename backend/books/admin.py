from django.contrib import admin
from .models import Book


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    """Interface administrativa para gerenciamento de livros."""

    list_display = (
        'title',
        'author',
        'genre',
        'publication_year',
        'source',
        'average_rating',
        'created_at'
    )

    list_filter = (
        'source',
        'genre',
        'language',
        'publication_year'
    )

    search_fields = (
        'title',
        'author',
        'isbn',
        'publisher',
        'description'
    )

    readonly_fields = (
        'id',
        'source',
        'created_at',
        'updated_at'
    )

    fieldsets = (
        ('Informações Básicas', {
            'fields': ('title', 'author', 'genre')
        }),
        ('Metadados', {
            'fields': (
                'isbn',
                'publisher',
                'publication_year',
                'description',
                'page_count',
                'language'
            )
        }),
        ('Mídia', {
            'fields': ('cover_url',)
        }),
        ('Categorização', {
            'fields': ('categories', 'average_rating')
        }),
        ('Sistema', {
            'fields': ('source', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    ordering = ('-created_at',)
