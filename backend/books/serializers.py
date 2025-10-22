from rest_framework import serializers
from .models import Book


class BookSerializer(serializers.ModelSerializer):
    """
    Serializer para o modelo Book.

    Inclui todos os campos do modelo, incluindo metadados estendidos.
    """

    class Meta:
        model = Book
        fields = [
            'id',
            'title',
            'author',
            'genre',
            'isbn',
            'publisher',
            'publication_year',
            'description',
            'cover_url',
            'page_count',
            'language',
            'categories',
            'average_rating',
            'source',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class BookCreateSerializer(serializers.Serializer):
    """
    Serializer para criação de livros via Builder.

    Suporta três modos de criação:
    1. Manual: campos do livro diretamente
    2. Google Books: google_books_id
    3. Open Library: isbn para busca
    """

    # Campos para criação manual
    title = serializers.CharField(max_length=255, required=False)
    author = serializers.CharField(max_length=255, required=False)
    genre = serializers.CharField(max_length=100, required=False, allow_blank=True)
    isbn = serializers.CharField(max_length=13, required=False, allow_blank=True)
    publisher = serializers.CharField(max_length=255, required=False, allow_blank=True)
    publication_year = serializers.IntegerField(required=False, allow_null=True)
    description = serializers.CharField(required=False, allow_blank=True)
    cover_url = serializers.URLField(required=False, allow_blank=True, allow_null=True)
    page_count = serializers.IntegerField(required=False, allow_null=True)
    language = serializers.CharField(max_length=10, required=False, allow_blank=True)
    categories = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        allow_empty=True
    )
    average_rating = serializers.DecimalField(
        max_digits=3,
        decimal_places=2,
        required=False,
        allow_null=True
    )

    # Campos para importação de APIs externas
    google_books_id = serializers.CharField(required=False, allow_blank=True)
    import_isbn = serializers.CharField(required=False, allow_blank=True, help_text="ISBN para importar do Google Books")


class BookSimpleSerializer(serializers.ModelSerializer):
    """
    Serializer simplificado para listagens.

    Retorna apenas campos essenciais para melhor performance.
    """

    class Meta:
        model = Book
        fields = ['id', 'title', 'author', 'genre', 'cover_url', 'average_rating']
