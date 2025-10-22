"""
Testes para os padrões Builder e Adapter aplicados ao modelo Book.

Testa BookBuilder, BookDirector, BookAPIInterface, Adapters e integração com APIs externas.
"""
from django.test import TestCase
from unittest.mock import patch, MagicMock
from decimal import Decimal

from books.models import Book
from books.builders import BookBuilder, BookDirector
from books.external_apis import GoogleBooksAPI, OpenLibraryAPI
from books.adapters import (
    BookAPIInterface,
    GoogleBooksAdapter,
    OpenLibraryAdapter,
    create_adapter
)


class BookBuilderTestCase(TestCase):
    """Testes unitários do BookBuilder."""

    def setUp(self):
        """Configuração inicial para cada teste."""
        self.builder = BookBuilder()

    def test_builder_reset(self):
        """Testa se reset() limpa os dados do builder."""
        self.builder.set_title("Test")
        self.builder.reset()
        data = self.builder.get_data()

        self.assertNotIn('title', data)
        self.assertEqual(data['source'], 'manual')
        self.assertEqual(data['categories'], [])

    def test_set_title_valid(self):
        """Testa definição de título válido."""
        self.builder.set_title("Clean Code")
        data = self.builder.get_data()

        self.assertEqual(data['title'], "Clean Code")

    def test_set_title_strips_whitespace(self):
        """Testa se set_title remove espaços extras."""
        self.builder.set_title("  Clean Code  ")
        data = self.builder.get_data()

        self.assertEqual(data['title'], "Clean Code")

    def test_set_title_empty_raises_error(self):
        """Testa se título vazio levanta ValueError."""
        with self.assertRaises(ValueError) as context:
            self.builder.set_title("")

        self.assertIn("vazio", str(context.exception).lower())

    def test_set_title_too_long_raises_error(self):
        """Testa se título muito longo levanta ValueError."""
        long_title = "x" * 256

        with self.assertRaises(ValueError) as context:
            self.builder.set_title(long_title)

        self.assertIn("255", str(context.exception))

    def test_set_author_valid(self):
        """Testa definição de autor válido."""
        self.builder.set_author("Robert C. Martin")
        data = self.builder.get_data()

        self.assertEqual(data['author'], "Robert C. Martin")

    def test_set_author_empty_raises_error(self):
        """Testa se autor vazio levanta ValueError."""
        with self.assertRaises(ValueError):
            self.builder.set_author("")

    def test_set_isbn_valid_with_hyphens(self):
        """Testa se ISBN com hífens é aceito e limpo."""
        self.builder.set_isbn("978-0-13-235088-4")
        data = self.builder.get_data()

        self.assertEqual(data['isbn'], "9780132350884")

    def test_set_isbn_valid_without_hyphens(self):
        """Testa ISBN sem hífens."""
        self.builder.set_isbn("9780132350884")
        data = self.builder.get_data()

        self.assertEqual(data['isbn'], "9780132350884")

    def test_set_isbn_invalid_length_raises_error(self):
        """Testa se ISBN com tamanho inválido levanta ValueError."""
        with self.assertRaises(ValueError) as context:
            self.builder.set_isbn("123")

        self.assertIn("10 ou 13", str(context.exception))

    def test_set_publication_year_valid(self):
        """Testa definição de ano válido."""
        self.builder.set_publication_year(2008)
        data = self.builder.get_data()

        self.assertEqual(data['publication_year'], 2008)

    def test_set_publication_year_too_old_raises_error(self):
        """Testa se ano muito antigo levanta ValueError."""
        with self.assertRaises(ValueError):
            self.builder.set_publication_year(999)

    def test_set_publication_year_future_raises_error(self):
        """Testa se ano futuro demais levanta ValueError."""
        with self.assertRaises(ValueError):
            self.builder.set_publication_year(2031)

    def test_set_publication_year_not_int_raises_error(self):
        """Testa se ano não-inteiro levanta ValueError."""
        with self.assertRaises(ValueError):
            self.builder.set_publication_year("2008")

    def test_set_average_rating_valid(self):
        """Testa definição de rating válido."""
        self.builder.set_average_rating(4.5)
        data = self.builder.get_data()

        self.assertEqual(data['average_rating'], 4.5)

    def test_set_average_rating_rounds_to_two_decimals(self):
        """Testa se rating é arredondado para 2 casas decimais."""
        self.builder.set_average_rating(4.567)
        data = self.builder.get_data()

        self.assertEqual(data['average_rating'], 4.57)

    def test_set_average_rating_out_of_range_raises_error(self):
        """Testa se rating fora do intervalo 0-5 levanta ValueError."""
        with self.assertRaises(ValueError):
            self.builder.set_average_rating(5.1)

        with self.assertRaises(ValueError):
            self.builder.set_average_rating(-0.1)

    def test_add_category(self):
        """Testa adição de categoria."""
        self.builder.add_category("Computers")
        self.builder.add_category("Programming")
        data = self.builder.get_data()

        self.assertEqual(data['categories'], ["Computers", "Programming"])

    def test_add_category_duplicate_ignored(self):
        """Testa se categoria duplicada é ignorada."""
        self.builder.add_category("Computers")
        self.builder.add_category("Computers")
        data = self.builder.get_data()

        self.assertEqual(data['categories'], ["Computers"])

    def test_set_categories_replaces_existing(self):
        """Testa se set_categories substitui categorias existentes."""
        self.builder.add_category("Old")
        self.builder.set_categories(["New1", "New2"])
        data = self.builder.get_data()

        self.assertEqual(data['categories'], ["New1", "New2"])

    def test_set_cover_url_valid(self):
        """Testa definição de URL válida."""
        url = "https://books.google.com/cover.jpg"
        self.builder.set_cover_url(url)
        data = self.builder.get_data()

        self.assertEqual(data['cover_url'], url)

    def test_set_cover_url_invalid_raises_error(self):
        """Testa se URL inválida levanta ValueError."""
        with self.assertRaises(ValueError):
            self.builder.set_cover_url("not-a-url")

    def test_set_page_count_valid(self):
        """Testa definição de número de páginas válido."""
        self.builder.set_page_count(464)
        data = self.builder.get_data()

        self.assertEqual(data['page_count'], 464)

    def test_set_page_count_negative_raises_error(self):
        """Testa se número negativo de páginas levanta ValueError."""
        with self.assertRaises(ValueError):
            self.builder.set_page_count(-10)

    def test_build_without_title_raises_error(self):
        """Testa se build() sem título levanta ValueError."""
        self.builder.set_author("Test Author")

        with self.assertRaises(ValueError) as context:
            self.builder.build()

        self.assertIn("título", str(context.exception).lower())

    def test_build_without_author_raises_error(self):
        """Testa se build() sem autor levanta ValueError."""
        self.builder.set_title("Test Title")

        with self.assertRaises(ValueError) as context:
            self.builder.build()

        self.assertIn("autor", str(context.exception).lower())

    def test_build_creates_book_successfully(self):
        """Testa se build() cria livro com sucesso."""
        book = (self.builder
            .set_title("Clean Code")
            .set_author("Robert C. Martin")
            .set_genre("Technical")
            .set_publication_year(2008)
            .build())

        self.assertIsNotNone(book.id)
        self.assertEqual(book.title, "Clean Code")
        self.assertEqual(book.author, "Robert C. Martin")
        self.assertEqual(book.genre, "Technical")
        self.assertEqual(book.publication_year, 2008)
        self.assertEqual(book.source, "manual")

    def test_build_resets_builder(self):
        """Testa se build() reseta o builder após criar o livro."""
        self.builder.set_title("Book 1").set_author("Author 1").build()
        data = self.builder.get_data()

        self.assertNotIn('title', data)
        self.assertNotIn('author', data)

    def test_fluent_interface(self):
        """Testa se todos os métodos retornam self (fluent interface)."""
        result = self.builder.set_title("Test")
        self.assertEqual(result, self.builder)

        result = self.builder.set_author("Test")
        self.assertEqual(result, self.builder)


class BookDirectorTestCase(TestCase):
    """Testes do BookDirector."""

    def setUp(self):
        """Configuração inicial para cada teste."""
        self.director = BookDirector()

    def test_construct_simple_book(self):
        """Testa construção de livro simples."""
        book = self.director.construct_simple_book(
            title="1984",
            author="George Orwell",
            genre="Fiction"
        )

        self.assertEqual(book.title, "1984")
        self.assertEqual(book.author, "George Orwell")
        self.assertEqual(book.genre, "Fiction")
        self.assertEqual(book.source, "manual")

    def test_construct_from_google_books_success(self):
        """Testa construção a partir de dados do Google Books."""
        # Mock data da Google Books API
        api_data = {
            'volumeInfo': {
                'title': 'Clean Code',
                'authors': ['Robert C. Martin'],
                'publisher': 'Prentice Hall',
                'publishedDate': '2008-08-01',
                'description': 'A book about clean code',
                'industryIdentifiers': [
                    {'type': 'ISBN_13', 'identifier': '9780132350884'}
                ],
                'pageCount': 464,
                'categories': ['Computers', 'Programming'],
                'imageLinks': {'thumbnail': 'https://example.com/cover.jpg'},
                'averageRating': 4.5,
                'language': 'en'
            }
        }

        book = self.director.construct_from_google_books(api_data)

        self.assertEqual(book.title, 'Clean Code')
        self.assertEqual(book.author, 'Robert C. Martin')
        self.assertEqual(book.isbn, '9780132350884')
        self.assertEqual(book.publication_year, 2008)
        self.assertEqual(book.publisher, 'Prentice Hall')
        self.assertEqual(book.page_count, 464)
        self.assertEqual(book.genre, 'Computers')
        self.assertIn('Computers', book.categories)
        self.assertEqual(book.source, 'google_books')

    def test_construct_from_google_books_multiple_authors(self):
        """Testa se múltiplos autores são concatenados."""
        api_data = {
            'volumeInfo': {
                'title': 'Test Book',
                'authors': ['Author One', 'Author Two', 'Author Three']
            }
        }

        book = self.director.construct_from_google_books(api_data)

        self.assertEqual(book.author, 'Author One, Author Two, Author Three')

    def test_construct_from_google_books_no_title_raises_error(self):
        """Testa se falta de título levanta ValueError."""
        api_data = {'volumeInfo': {}}

        with self.assertRaises(ValueError) as context:
            self.director.construct_from_google_books(api_data)

        self.assertIn("título", str(context.exception).lower())

    def test_construct_from_google_books_no_author_uses_fallback(self):
        """Testa se sem autor usa 'Autor Desconhecido'."""
        api_data = {
            'volumeInfo': {
                'title': 'Test Book'
            }
        }

        book = self.director.construct_from_google_books(api_data)

        self.assertEqual(book.author, 'Autor Desconhecido')

    def test_construct_from_google_books_prefers_isbn13(self):
        """Testa se ISBN-13 é preferido ao ISBN-10."""
        api_data = {
            'volumeInfo': {
                'title': 'Test',
                'authors': ['Test'],
                'industryIdentifiers': [
                    {'type': 'ISBN_10', 'identifier': '0132350882'},
                    {'type': 'ISBN_13', 'identifier': '9780132350884'}
                ]
            }
        }

        book = self.director.construct_from_google_books(api_data)

        self.assertEqual(book.isbn, '9780132350884')


class GoogleBooksAPITestCase(TestCase):
    """Testes para o helper GoogleBooksAPI."""

    @patch('books.external_apis.requests.get')
    def test_fetch_by_id_success(self, mock_get):
        """Testa busca por ID com sucesso."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'volumeInfo': {'title': 'Test'}}
        mock_get.return_value = mock_response

        result = GoogleBooksAPI.fetch_by_id('test_id')

        self.assertIsNotNone(result)
        self.assertEqual(result['volumeInfo']['title'], 'Test')
        mock_get.assert_called_once()

    @patch('books.external_apis.requests.get')
    def test_fetch_by_id_not_found_returns_none(self, mock_get):
        """Testa se livro não encontrado retorna None."""
        from requests.exceptions import HTTPError

        # Cria mock da response com status 404
        mock_response = MagicMock()
        mock_response.status_code = 404

        # Cria exceção HTTPError com response anexada
        http_error = HTTPError()
        http_error.response = mock_response

        # Configura raise_for_status para levantar a exceção
        mock_response.raise_for_status.side_effect = http_error
        mock_get.return_value = mock_response

        result = GoogleBooksAPI.fetch_by_id('invalid_id')

        self.assertIsNone(result)

    @patch('books.external_apis.requests.get')
    def test_search_by_isbn(self, mock_get):
        """Testa busca por ISBN."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'items': [{'volumeInfo': {'title': 'Test Book'}}]
        }
        mock_get.return_value = mock_response

        result = GoogleBooksAPI.search_by_isbn('9780132350884')

        self.assertIsNotNone(result)
        self.assertEqual(result['volumeInfo']['title'], 'Test Book')


# ========================================
# TESTES DO PADRÃO ADAPTER
# ========================================

class GoogleBooksAdapterTestCase(TestCase):
    """Testes para o GoogleBooksAdapter (padrão Adapter)."""

    def setUp(self):
        """Configuração inicial para cada teste."""
        self.adapter = GoogleBooksAdapter()

    @patch('books.adapters.GoogleBooksAPI.search_by_isbn')
    def test_search_by_isbn_success(self, mock_search):
        """Testa busca por ISBN com sucesso e normalização."""
        # Mock da resposta do Google Books
        mock_search.return_value = {
            'volumeInfo': {
                'title': 'Clean Code',
                'authors': ['Robert C. Martin'],
                'industryIdentifiers': [
                    {'type': 'ISBN_13', 'identifier': '9780132350884'}
                ],
                'publisher': 'Prentice Hall',
                'publishedDate': '2008-08-01',
                'pageCount': 464,
                'language': 'en'
            }
        }

        result = self.adapter.search_by_isbn('9780132350884')

        # Verifica estrutura normalizada
        self.assertIsNotNone(result)
        self.assertEqual(result['title'], 'Clean Code')
        self.assertEqual(result['authors'], ['Robert C. Martin'])
        self.assertEqual(result['isbn'], '9780132350884')
        self.assertEqual(result['publisher'], 'Prentice Hall')
        self.assertEqual(result['published_date'], '2008-08-01')
        self.assertEqual(result['page_count'], 464)
        self.assertEqual(result['language'], 'en')

    @patch('books.adapters.GoogleBooksAPI.search_by_isbn')
    def test_search_by_isbn_not_found(self, mock_search):
        """Testa busca por ISBN não encontrado."""
        mock_search.return_value = None

        result = self.adapter.search_by_isbn('9999999999999')

        self.assertIsNone(result)

    @patch('books.adapters.GoogleBooksAPI.search')
    def test_search_by_query(self, mock_search):
        """Testa busca por query."""
        mock_search.return_value = {
            'items': [
                {
                    'volumeInfo': {
                        'title': 'Book 1',
                        'authors': ['Author 1']
                    }
                },
                {
                    'volumeInfo': {
                        'title': 'Book 2',
                        'authors': ['Author 2']
                    }
                }
            ]
        }

        results = self.adapter.search_by_query('clean code', limit=2)

        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]['title'], 'Book 1')
        self.assertEqual(results[1]['title'], 'Book 2')

    @patch('books.adapters.GoogleBooksAPI.fetch_by_id')
    def test_fetch_by_id(self, mock_fetch):
        """Testa busca por ID do volume."""
        mock_fetch.return_value = {
            'volumeInfo': {
                'title': 'Test Book',
                'authors': ['Test Author']
            }
        }

        result = self.adapter.fetch_by_id('test_volume_id')

        self.assertIsNotNone(result)
        self.assertEqual(result['title'], 'Test Book')

    def test_normalize_prefers_isbn13(self):
        """Testa se normalização prefere ISBN-13 sobre ISBN-10."""
        api_data = {
            'volumeInfo': {
                'title': 'Test',
                'industryIdentifiers': [
                    {'type': 'ISBN_10', 'identifier': '0132350882'},
                    {'type': 'ISBN_13', 'identifier': '9780132350884'}
                ]
            }
        }

        normalized = self.adapter.normalize_to_standard_format(api_data)

        self.assertEqual(normalized['isbn'], '9780132350884')

    def test_normalize_handles_missing_fields(self):
        """Testa normalização com campos faltando."""
        api_data = {
            'volumeInfo': {
                'title': 'Minimal Book'
            }
        }

        normalized = self.adapter.normalize_to_standard_format(api_data)

        self.assertEqual(normalized['title'], 'Minimal Book')
        self.assertEqual(normalized['authors'], [])
        self.assertIsNone(normalized['isbn'])
        self.assertIsNone(normalized['publisher'])

    def test_get_api_name(self):
        """Testa se retorna o nome correto da API."""
        self.assertEqual(self.adapter.get_api_name(), 'google_books')


class OpenLibraryAdapterTestCase(TestCase):
    """Testes para o OpenLibraryAdapter (padrão Adapter)."""

    def setUp(self):
        """Configuração inicial para cada teste."""
        self.adapter = OpenLibraryAdapter()

    @patch('books.adapters.OpenLibraryAPI.fetch_by_isbn')
    def test_search_by_isbn_success(self, mock_fetch):
        """Testa busca por ISBN com sucesso."""
        mock_fetch.return_value = {
            'title': '1984',
            'authors': [{'name': 'George Orwell'}],
            'isbn': ['0451524934', '9780451524935'],
            'publishers': ['Signet Classic'],
            'first_publish_year': 1949
        }

        result = self.adapter.search_by_isbn('0451524934')

        self.assertIsNotNone(result)
        self.assertEqual(result['title'], '1984')
        self.assertEqual(result['authors'], ['George Orwell'])
        self.assertEqual(result['isbn'], '9780451524935')  # Prefere o mais longo
        self.assertEqual(result['publisher'], 'Signet Classic')

    @patch('books.adapters.OpenLibraryAPI.fetch_by_isbn')
    def test_search_by_isbn_not_found(self, mock_fetch):
        """Testa busca por ISBN não encontrado."""
        mock_fetch.return_value = None

        result = self.adapter.search_by_isbn('9999999999')

        self.assertIsNone(result)

    @patch('books.adapters.OpenLibraryAPI.search')
    def test_search_by_query(self, mock_search):
        """Testa busca por query."""
        mock_search.return_value = {
            'docs': [
                {
                    'title': '1984',
                    'author_name': ['George Orwell'],
                    'first_publish_year': 1949
                },
                {
                    'title': 'Animal Farm',
                    'author_name': ['George Orwell'],
                    'first_publish_year': 1945
                }
            ]
        }

        results = self.adapter.search_by_query('george orwell', limit=2)

        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]['title'], '1984')
        self.assertEqual(results[1]['title'], 'Animal Farm')

    def test_fetch_by_id_not_supported(self):
        """Testa que fetch_by_id não é suportado."""
        result = self.adapter.fetch_by_id('any_id')
        self.assertIsNone(result)

    def test_normalize_builds_cover_url(self):
        """Testa se normalização constrói URL da capa corretamente."""
        api_data = {
            'title': 'Test',
            'cover_i': 12345678
        }

        normalized = self.adapter.normalize_to_standard_format(api_data)

        self.assertEqual(
            normalized['cover_url'],
            'https://covers.openlibrary.org/b/id/12345678-L.jpg'
        )

    def test_normalize_maps_language_codes(self):
        """Testa mapeamento de códigos de idioma."""
        api_data = {
            'title': 'Test',
            'language': ['eng']
        }

        normalized = self.adapter.normalize_to_standard_format(api_data)

        self.assertEqual(normalized['language'], 'en')

    def test_normalize_selects_longest_isbn(self):
        """Testa se seleciona ISBN mais longo (geralmente ISBN-13)."""
        api_data = {
            'title': 'Test',
            'isbn': ['123456789', '12345678901', '1234567890123']
        }

        normalized = self.adapter.normalize_to_standard_format(api_data)

        self.assertEqual(normalized['isbn'], '1234567890123')

    def test_get_api_name(self):
        """Testa se retorna o nome correto da API."""
        self.assertEqual(self.adapter.get_api_name(), 'open_library')


class AdapterFactoryTestCase(TestCase):
    """Testes para a factory de adapters."""

    def test_create_google_books_adapter(self):
        """Testa criação de GoogleBooksAdapter via factory."""
        adapter = create_adapter('google_books')

        self.assertIsInstance(adapter, GoogleBooksAdapter)
        self.assertEqual(adapter.get_api_name(), 'google_books')

    def test_create_open_library_adapter(self):
        """Testa criação de OpenLibraryAdapter via factory."""
        adapter = create_adapter('open_library')

        self.assertIsInstance(adapter, OpenLibraryAdapter)
        self.assertEqual(adapter.get_api_name(), 'open_library')

    def test_create_adapter_with_kwargs(self):
        """Testa factory com argumentos adicionais."""
        adapter = create_adapter('google_books', api_key='TEST_KEY')

        self.assertIsInstance(adapter, GoogleBooksAdapter)
        self.assertEqual(adapter.api_key, 'TEST_KEY')

    def test_create_adapter_unknown_api_raises_error(self):
        """Testa se API desconhecida levanta ValueError."""
        with self.assertRaises(ValueError) as context:
            create_adapter('unknown_api')

        self.assertIn('desconhecida', str(context.exception).lower())


class BookDirectorAdapterIntegrationTestCase(TestCase):
    """Testes de integração entre BookDirector e Adapters."""

    def setUp(self):
        """Configuração inicial para cada teste."""
        self.director = BookDirector()

    def test_construct_from_adapter_google_books(self):
        """Testa construção via adapter do Google Books."""
        normalized_data = {
            'title': 'Clean Code',
            'authors': ['Robert C. Martin'],
            'isbn': '9780132350884',
            'publisher': 'Prentice Hall',
            'published_date': '2008-08-01',
            'description': 'A handbook of agile software craftsmanship',
            'cover_url': 'https://example.com/cover.jpg',
            'page_count': 464,
            'categories': ['Computers', 'Programming'],
            'language': 'en',
            'average_rating': 4.5
        }

        book = self.director.construct_from_adapter(normalized_data, 'google_books')

        self.assertEqual(book.title, 'Clean Code')
        self.assertEqual(book.author, 'Robert C. Martin')
        self.assertEqual(book.isbn, '9780132350884')
        self.assertEqual(book.publication_year, 2008)
        self.assertEqual(book.source, 'google_books')

    def test_construct_from_adapter_open_library(self):
        """Testa construção via adapter do Open Library."""
        normalized_data = {
            'title': '1984',
            'authors': ['George Orwell'],
            'isbn': '0451524934',
            'publisher': 'Signet Classic',
            'published_date': '1949',
            'description': None,
            'cover_url': 'https://covers.openlibrary.org/b/id/123-L.jpg',
            'page_count': 328,
            'categories': ['Fiction', 'Dystopian'],
            'language': 'en',
            'average_rating': None
        }

        book = self.director.construct_from_adapter(normalized_data, 'open_library')

        self.assertEqual(book.title, '1984')
        self.assertEqual(book.author, 'George Orwell')
        self.assertEqual(book.publication_year, 1949)
        self.assertEqual(book.source, 'open_library')

    def test_construct_from_adapter_without_title_raises_error(self):
        """Testa se ausência de título levanta ValueError."""
        normalized_data = {
            'title': '',
            'authors': ['Test Author']
        }

        with self.assertRaises(ValueError) as context:
            self.director.construct_from_adapter(normalized_data, 'google_books')

        self.assertIn('título', str(context.exception).lower())

    def test_adapters_are_interchangeable(self):
        """Testa que adapters diferentes podem ser usados de forma intercambiável."""
        # Dados normalizados (mesmo formato para ambas APIs)
        data1 = {
            'title': 'Book from Google',
            'authors': ['Author 1'],
            'isbn': '1234567890',
            'published_date': '2020',
            'categories': []
        }

        data2 = {
            'title': 'Book from OpenLib',
            'authors': ['Author 2'],
            'isbn': '0987654321',
            'published_date': '2021',
            'categories': []
        }

        book1 = self.director.construct_from_adapter(data1, 'google_books')
        book2 = self.director.construct_from_adapter(data2, 'open_library')

        # Ambos são criados com sucesso
        self.assertIsNotNone(book1.id)
        self.assertIsNotNone(book2.id)

        # Source é diferente mas estrutura é a mesma
        self.assertEqual(book1.source, 'google_books')
        self.assertEqual(book2.source, 'open_library')
