from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Book
from .serializers import BookSerializer, BookCreateSerializer, BookSimpleSerializer
from .builders import BookBuilder, BookDirector
from .external_apis import GoogleBooksAPI, OpenLibraryAPI
from .adapters import GoogleBooksAdapter, OpenLibraryAdapter
import logging

logger = logging.getLogger(__name__)


class BookViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gerenciamento de livros.

    Suporta criação via padrão Builder com múltiplas fontes de dados:
    - Criação manual
    - Importação do Google Books
    - Importação do Open Library
    """

    queryset = Book.objects.all()
    serializer_class = BookSerializer

    def get_serializer_class(self):
        """Retorna serializer apropriado baseado na action."""
        if self.action == 'create':
            return BookCreateSerializer
        elif self.action == 'list':
            return BookSimpleSerializer
        return BookSerializer

    def create(self, request, *args, **kwargs):
        """
        Cria um livro usando o padrão Builder.

        Aceita três modos de criação:
        1. Manual: fornece campos do livro diretamente
        2. Google Books: fornece google_books_id
        3. Import ISBN: fornece import_isbn para buscar no Google Books

        Examples:
            Manual:
            POST /api/books/
            {
                "title": "Clean Code",
                "author": "Robert C. Martin",
                "genre": "Técnico",
                "isbn": "9780132350884"
            }

            Google Books:
            POST /api/books/
            {
                "google_books_id": "hjEFCAAAQBAJ"
            }

            Import ISBN:
            POST /api/books/
            {
                "import_isbn": "9780132350884"
            }
        """
        serializer = BookCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        try:
            # Modo 1: Importação do Google Books por ID
            if data.get('google_books_id'):
                book = self._create_from_google_books_id(data['google_books_id'])

            # Modo 2: Importação por ISBN (busca no Google Books)
            elif data.get('import_isbn'):
                book = self._create_from_isbn(data['import_isbn'])

            # Modo 3: Criação manual com Builder
            else:
                book = self._create_manual(data)

            # Serializa e retorna
            output_serializer = BookSerializer(book)
            return Response(output_serializer.data, status=status.HTTP_201_CREATED)

        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Erro ao criar livro: {e}", exc_info=True)
            return Response(
                {'error': 'Erro interno ao criar livro'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def _create_manual(self, data: dict) -> Book:
        """
        Cria livro manualmente usando BookBuilder.

        Args:
            data: Dicionário com campos do livro

        Returns:
            Book: Livro criado

        Raises:
            ValueError: Se campos obrigatórios estiverem faltando
        """
        builder = BookBuilder()

        # Campos obrigatórios
        if 'title' in data and data['title']:
            builder.set_title(data['title'])
        if 'author' in data and data['author']:
            builder.set_author(data['author'])

        # Campos opcionais
        if data.get('genre'):
            builder.set_genre(data['genre'])
        if data.get('isbn'):
            builder.set_isbn(data['isbn'])
        if data.get('publisher'):
            builder.set_publisher(data['publisher'])
        if data.get('publication_year'):
            builder.set_publication_year(data['publication_year'])
        if data.get('description'):
            builder.set_description(data['description'])
        if data.get('cover_url'):
            builder.set_cover_url(data['cover_url'])
        if data.get('page_count'):
            builder.set_page_count(data['page_count'])
        if data.get('language'):
            builder.set_language(data['language'])
        if data.get('categories'):
            builder.set_categories(data['categories'])
        if data.get('average_rating'):
            builder.set_average_rating(float(data['average_rating']))

        builder.set_source('manual')

        return builder.build()

    def _create_from_google_books_id(self, volume_id: str) -> Book:
        """
        Cria livro importando do Google Books por ID usando Adapter.

        Args:
            volume_id: ID do volume no Google Books

        Returns:
            Book: Livro criado

        Raises:
            ValueError: Se livro não for encontrado
        """
        # Usa o Adapter para buscar e normalizar dados
        adapter = GoogleBooksAdapter()
        normalized_data = adapter.fetch_by_id(volume_id)

        if not normalized_data:
            raise ValueError(f"Livro não encontrado no Google Books: {volume_id}")

        # Usa o Director com dados normalizados
        director = BookDirector()
        return director.construct_from_adapter(normalized_data, adapter.get_api_name())

    def _create_from_isbn(self, isbn: str, api_source: str = 'google_books') -> Book:
        """
        Cria livro buscando por ISBN usando Adapter.

        Suporta múltiplas APIs através do padrão Adapter, permitindo fallback.

        Args:
            isbn: ISBN-10 ou ISBN-13
            api_source: API a usar ('google_books' ou 'open_library')

        Returns:
            Book: Livro criado

        Raises:
            ValueError: Se livro não for encontrado em nenhuma API
        """
        # Tenta primeiro com a API especificada
        if api_source == 'google_books':
            adapter = GoogleBooksAdapter()
        elif api_source == 'open_library':
            adapter = OpenLibraryAdapter()
        else:
            raise ValueError(f"API source inválida: {api_source}")

        normalized_data = adapter.search_by_isbn(isbn)

        # Se não encontrou, tenta fallback para outra API
        if not normalized_data and api_source == 'google_books':
            logger.info(f"ISBN {isbn} não encontrado no Google Books, tentando Open Library...")
            adapter = OpenLibraryAdapter()
            normalized_data = adapter.search_by_isbn(isbn)

        if not normalized_data:
            raise ValueError(f"Livro não encontrado com ISBN: {isbn}")

        director = BookDirector()
        return director.construct_from_adapter(normalized_data, adapter.get_api_name())

    @action(detail=False, methods=['post'], url_path='import-google-books')
    def import_from_google_books(self, request):
        """
        Endpoint dedicado para importar livro do Google Books.

        POST /api/books/import-google-books/
        {
            "volume_id": "hjEFCAAAQBAJ"
        }
        """
        volume_id = request.data.get('volume_id')
        if not volume_id:
            return Response(
                {'error': 'volume_id é obrigatório'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            book = self._create_from_google_books_id(volume_id)
            serializer = BookSerializer(book)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Erro ao importar do Google Books: {e}", exc_info=True)
            return Response(
                {'error': 'Erro ao importar livro'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['get'], url_path='search-google-books')
    def search_google_books(self, request):
        """
        Busca livros no Google Books sem criar no banco (usando Adapter).

        GET /api/books/search-google-books/?q=clean+code
        """
        query = request.query_params.get('q')
        if not query:
            return Response(
                {'error': 'Parâmetro q (query) é obrigatório'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            adapter = GoogleBooksAdapter()
            results = adapter.search_by_query(query, limit=10)
            return Response({
                'count': len(results),
                'results': results,
                'api_source': 'google_books'
            }, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Erro ao buscar no Google Books: {e}", exc_info=True)
            return Response(
                {'error': 'Erro ao buscar livros'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['post'], url_path='import-open-library')
    def import_from_open_library(self, request):
        """
        Endpoint para importar livro do Open Library por ISBN.

        POST /api/books/import-open-library/
        {
            "isbn": "0451524934"
        }
        """
        isbn = request.data.get('isbn')
        if not isbn:
            return Response(
                {'error': 'isbn é obrigatório'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            adapter = OpenLibraryAdapter()
            normalized_data = adapter.search_by_isbn(isbn)

            if not normalized_data:
                return Response(
                    {'error': f'Livro não encontrado no Open Library com ISBN: {isbn}'},
                    status=status.HTTP_404_NOT_FOUND
                )

            director = BookDirector()
            book = director.construct_from_adapter(normalized_data, adapter.get_api_name())

            serializer = BookSerializer(book)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Erro ao importar do Open Library: {e}", exc_info=True)
            return Response(
                {'error': 'Erro ao importar livro'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['get'], url_path='search-open-library')
    def search_open_library(self, request):
        """
        Busca livros no Open Library sem criar no banco (usando Adapter).

        GET /api/books/search-open-library/?q=1984+orwell
        """
        query = request.query_params.get('q')
        if not query:
            return Response(
                {'error': 'Parâmetro q (query) é obrigatório'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            adapter = OpenLibraryAdapter()
            results = adapter.search_by_query(query, limit=10)
            return Response({
                'count': len(results),
                'results': results,
                'api_source': 'open_library'
            }, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Erro ao buscar no Open Library: {e}", exc_info=True)
            return Response(
                {'error': 'Erro ao buscar livros'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
