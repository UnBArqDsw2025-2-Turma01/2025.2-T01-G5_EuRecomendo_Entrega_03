"""
Testes para o padrão Iterator em books/iterators.py

Testa todos os componentes do padrão Iterator:
- UnifiedAPIIterator
- LazyAPIIterator
- MultiSourceIterator
- BookAPICollection
- IteratorBookBuilder
"""
from unittest.mock import Mock, MagicMock, patch
from django.test import TestCase

from books.iterators import (
    UnifiedAPIIterator,
    LazyAPIIterator,
    MultiSourceIterator,
    BookAPICollection,
    IteratorBookBuilder
)
from books.adapters import BookAPIInterface
from books.models import Book


class UnifiedAPIIteratorTest(TestCase):
    """Testes para UnifiedAPIIterator."""

    def setUp(self):
        """Configura dados de teste."""
        self.sample_results = [
            {
                'title': 'Clean Code',
                'authors': ['Robert C. Martin'],
                'isbn': '9780132350884',
                'publisher': 'Prentice Hall',
                'published_date': '2008',
                'description': 'A handbook of agile software craftsmanship',
                'cover_url': 'http://example.com/cover1.jpg',
                'page_count': 464,
                'categories': ['Computers'],
                'language': 'en',
                'average_rating': 4.5
            },
            {
                'title': 'The Pragmatic Programmer',
                'authors': ['Andy Hunt', 'Dave Thomas'],
                'isbn': '9780135957059',
                'publisher': 'Addison-Wesley',
                'published_date': '2019',
                'description': 'Your journey to mastery',
                'cover_url': 'http://example.com/cover2.jpg',
                'page_count': 352,
                'categories': ['Computers'],
                'language': 'en',
                'average_rating': 4.7
            },
            {
                'title': 'Refactoring',
                'authors': ['Martin Fowler'],
                'isbn': '9780134757599',
                'publisher': 'Addison-Wesley',
                'published_date': '2018',
                'description': 'Improving the design of existing code',
                'cover_url': 'http://example.com/cover3.jpg',
                'page_count': 448,
                'categories': ['Computers'],
                'language': 'en',
                'average_rating': 4.6
            }
        ]

    def test_iterator_initialization(self):
        """Testa inicialização do iterador."""
        iterator = UnifiedAPIIterator(self.sample_results, api_name='google_books')

        self.assertEqual(iterator.total_count(), 3)
        self.assertEqual(iterator.current_position(), 0)
        self.assertEqual(iterator.get_api_name(), 'google_books')
        self.assertTrue(iterator.has_next())

    def test_iteration(self):
        """Testa iteração básica."""
        iterator = UnifiedAPIIterator(self.sample_results, api_name='google_books')

        # Primeira iteração
        book1 = next(iterator)
        self.assertEqual(book1['title'], 'Clean Code')
        self.assertEqual(iterator.current_position(), 1)

        # Segunda iteração
        book2 = next(iterator)
        self.assertEqual(book2['title'], 'The Pragmatic Programmer')
        self.assertEqual(iterator.current_position(), 2)

        # Terceira iteração
        book3 = next(iterator)
        self.assertEqual(book3['title'], 'Refactoring')
        self.assertEqual(iterator.current_position(), 3)

        # Não há mais elementos
        self.assertFalse(iterator.has_next())
        with self.assertRaises(StopIteration):
            next(iterator)

    def test_for_loop_iteration(self):
        """Testa iteração usando for loop."""
        iterator = UnifiedAPIIterator(self.sample_results, api_name='google_books')

        titles = []
        for book in iterator:
            titles.append(book['title'])

        self.assertEqual(len(titles), 3)
        self.assertIn('Clean Code', titles)
        self.assertIn('The Pragmatic Programmer', titles)
        self.assertIn('Refactoring', titles)

    def test_reset(self):
        """Testa reinicialização do iterador."""
        iterator = UnifiedAPIIterator(self.sample_results, api_name='google_books')

        # Itera até o fim
        for _ in iterator:
            pass

        self.assertEqual(iterator.current_position(), 3)
        self.assertFalse(iterator.has_next())

        # Reset
        iterator.reset()
        self.assertEqual(iterator.current_position(), 0)
        self.assertTrue(iterator.has_next())

        # Deve poder iterar novamente
        book1 = next(iterator)
        self.assertEqual(book1['title'], 'Clean Code')

    def test_peek(self):
        """Testa peek sem avançar iterador."""
        iterator = UnifiedAPIIterator(self.sample_results, api_name='google_books')

        # Peek não avança
        peeked = iterator.peek()
        self.assertEqual(peeked['title'], 'Clean Code')
        self.assertEqual(iterator.current_position(), 0)

        # Peek novamente retorna o mesmo
        peeked_again = iterator.peek()
        self.assertEqual(peeked_again['title'], 'Clean Code')

        # Next avança
        next_book = next(iterator)
        self.assertEqual(next_book['title'], 'Clean Code')
        self.assertEqual(iterator.current_position(), 1)

        # Peek agora retorna o próximo
        peeked_next = iterator.peek()
        self.assertEqual(peeked_next['title'], 'The Pragmatic Programmer')

    def test_skip(self):
        """Testa pular elementos."""
        iterator = UnifiedAPIIterator(self.sample_results, api_name='google_books')

        # Pula 2 elementos
        iterator.skip(2)
        self.assertEqual(iterator.current_position(), 2)

        # Próximo deve ser o terceiro
        book = next(iterator)
        self.assertEqual(book['title'], 'Refactoring')

    def test_empty_results(self):
        """Testa iterador com resultados vazios."""
        iterator = UnifiedAPIIterator([], api_name='google_books')

        self.assertEqual(iterator.total_count(), 0)
        self.assertFalse(iterator.has_next())
        self.assertIsNone(iterator.peek())

        with self.assertRaises(StopIteration):
            next(iterator)

    def test_none_results(self):
        """Testa iterador com None como resultados."""
        iterator = UnifiedAPIIterator(None, api_name='google_books')

        self.assertEqual(iterator.total_count(), 0)
        self.assertFalse(iterator.has_next())


class LazyAPIIteratorTest(TestCase):
    """Testes para LazyAPIIterator."""

    def setUp(self):
        """Configura mock do adapter."""
        self.mock_adapter = Mock(spec=BookAPIInterface)
        self.mock_adapter.get_api_name.return_value = 'google_books'

        # Simula resultados paginados
        self.page1_results = [
            {'title': f'Book {i}', 'authors': ['Author'], 'isbn': f'123456789{i}'}
            for i in range(1, 6)
        ]
        self.page2_results = [
            {'title': f'Book {i}', 'authors': ['Author'], 'isbn': f'123456789{i}'}
            for i in range(6, 11)
        ]

    def test_lazy_loading_first_page(self):
        """Testa carregamento lazy da primeira página."""
        self.mock_adapter.search_by_query.return_value = self.page1_results

        iterator = LazyAPIIterator(self.mock_adapter, query="python", page_size=5)

        # Deve ter carregado primeira página
        self.mock_adapter.search_by_query.assert_called_once_with("python", limit=5)
        self.assertTrue(iterator.has_next())

    def test_iteration_single_page(self):
        """Testa iteração em uma única página."""
        self.mock_adapter.search_by_query.return_value = self.page1_results

        iterator = LazyAPIIterator(self.mock_adapter, query="python", page_size=5, max_pages=1)

        books = list(iterator)
        self.assertEqual(len(books), 5)
        self.assertEqual(books[0]['title'], 'Book 1')
        self.assertEqual(books[4]['title'], 'Book 5')

    def test_empty_results(self):
        """Testa quando API retorna resultados vazios."""
        self.mock_adapter.search_by_query.return_value = []

        iterator = LazyAPIIterator(self.mock_adapter, query="nonexistent", page_size=5)

        self.assertFalse(iterator.has_next())
        with self.assertRaises(StopIteration):
            next(iterator)

    def test_api_error_handling(self):
        """Testa tratamento de erros da API."""
        self.mock_adapter.search_by_query.side_effect = Exception("API Error")

        iterator = LazyAPIIterator(self.mock_adapter, query="error", page_size=5)

        # Iterator deve marcar como exhausted
        self.assertFalse(iterator.has_next())

    def test_reset(self):
        """Testa reset do iterador lazy."""
        self.mock_adapter.search_by_query.return_value = self.page1_results

        iterator = LazyAPIIterator(self.mock_adapter, query="python", page_size=5, max_pages=1)

        # Consome alguns elementos
        next(iterator)
        next(iterator)
        self.assertEqual(iterator.current_position(), 2)

        # Reset
        iterator.reset()
        self.assertEqual(iterator.current_position(), 0)
        self.assertTrue(iterator.has_next())


class MultiSourceIteratorTest(TestCase):
    """Testes para MultiSourceIterator."""

    def setUp(self):
        """Configura mocks de múltiplos adapters."""
        self.mock_google = Mock(spec=BookAPIInterface)
        self.mock_google.get_api_name.return_value = 'google_books'

        self.mock_openlibrary = Mock(spec=BookAPIInterface)
        self.mock_openlibrary.get_api_name.return_value = 'open_library'

        # Resultados do Google Books
        self.google_results = [
            {'title': 'Book A', 'authors': ['Author 1'], 'isbn': '1111111111'},
            {'title': 'Book B', 'authors': ['Author 2'], 'isbn': '2222222222'},
        ]

        # Resultados do Open Library
        self.openlibrary_results = [
            {'title': 'Book C', 'authors': ['Author 3'], 'isbn': '3333333333'},
            {'title': 'Book D', 'authors': ['Author 4'], 'isbn': '4444444444'},
        ]

    def test_multi_source_aggregation(self):
        """Testa agregação de múltiplas fontes."""
        self.mock_google.search_by_query.return_value = self.google_results
        self.mock_openlibrary.search_by_query.return_value = self.openlibrary_results

        iterator = MultiSourceIterator(
            [self.mock_google, self.mock_openlibrary],
            query="python",
            limit_per_api=10,
            deduplicate_by_isbn=False
        )

        # Deve ter 4 resultados (2 de cada API)
        self.assertEqual(iterator.total_count(), 4)

        # Itera sobre todos
        books = list(iterator)
        self.assertEqual(len(books), 4)

        # Verifica metadados de origem
        sources = [book['_api_source'] for book in books]
        self.assertEqual(sources.count('google_books'), 2)
        self.assertEqual(sources.count('open_library'), 2)

    def test_deduplication_by_isbn(self):
        """Testa deduplicação por ISBN."""
        # Open Library tem um livro duplicado
        duplicated_openlibrary = [
            {'title': 'Book A Duplicate', 'authors': ['Author 1'], 'isbn': '1111111111'},  # Mesmo ISBN
            {'title': 'Book E', 'authors': ['Author 5'], 'isbn': '5555555555'},
        ]

        self.mock_google.search_by_query.return_value = self.google_results
        self.mock_openlibrary.search_by_query.return_value = duplicated_openlibrary

        iterator = MultiSourceIterator(
            [self.mock_google, self.mock_openlibrary],
            query="python",
            deduplicate_by_isbn=True
        )

        # Deve ter 3 resultados (1 duplicata removida)
        self.assertEqual(iterator.total_count(), 3)

        # Verifica que não há ISBN duplicado
        isbns = [book['isbn'] for book in iterator]
        self.assertEqual(len(isbns), len(set(isbns)))  # Sem duplicatas

    def test_group_by_source(self):
        """Testa agrupamento por fonte."""
        self.mock_google.search_by_query.return_value = self.google_results
        self.mock_openlibrary.search_by_query.return_value = self.openlibrary_results

        iterator = MultiSourceIterator(
            [self.mock_google, self.mock_openlibrary],
            query="python",
            deduplicate_by_isbn=False
        )

        grouped = iterator.group_by_source()

        self.assertIn('google_books', grouped)
        self.assertIn('open_library', grouped)
        self.assertEqual(len(grouped['google_books']), 2)
        self.assertEqual(len(grouped['open_library']), 2)

    def test_api_failure_resilience(self):
        """Testa resiliência a falhas de API."""
        self.mock_google.search_by_query.return_value = self.google_results
        self.mock_openlibrary.search_by_query.side_effect = Exception("API Down")

        iterator = MultiSourceIterator(
            [self.mock_google, self.mock_openlibrary],
            query="python"
        )

        # Deve ter apenas resultados do Google (Open Library falhou)
        self.assertEqual(iterator.total_count(), 2)
        books = list(iterator)
        self.assertTrue(all(b['_api_source'] == 'google_books' for b in books))

    def test_reset(self):
        """Testa reset do iterador multi-fonte."""
        self.mock_google.search_by_query.return_value = self.google_results
        self.mock_openlibrary.search_by_query.return_value = self.openlibrary_results

        iterator = MultiSourceIterator([self.mock_google, self.mock_openlibrary], query="python")

        # Consome alguns elementos
        next(iterator)
        next(iterator)
        self.assertEqual(iterator.current_position(), 2)

        # Reset
        iterator.reset()
        self.assertEqual(iterator.current_position(), 0)
        self.assertTrue(iterator.has_next())


class BookAPICollectionTest(TestCase):
    """Testes para BookAPICollection (Aggregate)."""

    def setUp(self):
        """Configura collection com mocks."""
        self.mock_google = Mock(spec=BookAPIInterface)
        self.mock_google.get_api_name.return_value = 'google_books'
        self.mock_google.search_by_query.return_value = [
            {'title': 'Book 1', 'authors': ['Author 1'], 'isbn': '1111111111'}
        ]

        self.mock_openlibrary = Mock(spec=BookAPIInterface)
        self.mock_openlibrary.get_api_name.return_value = 'open_library'
        self.mock_openlibrary.search_by_query.return_value = [
            {'title': 'Book 2', 'authors': ['Author 2'], 'isbn': '2222222222'}
        ]

    def test_add_api(self):
        """Testa adição de APIs."""
        collection = BookAPICollection()

        collection.add_api(self.mock_google)
        collection.add_api(self.mock_openlibrary)

        apis = collection.get_apis()
        self.assertEqual(len(apis), 2)

    def test_add_api_chaining(self):
        """Testa method chaining ao adicionar APIs."""
        collection = BookAPICollection()

        result = collection.add_api(self.mock_google).add_api(self.mock_openlibrary)

        self.assertIsInstance(result, BookAPICollection)
        self.assertEqual(len(collection.get_apis()), 2)

    def test_create_unified_iterator(self):
        """Testa criação de iterador unificado."""
        collection = BookAPICollection()
        collection.add_api(self.mock_google)

        iterator = collection.create_iterator("python", api_index=0, limit=10)

        self.assertIsInstance(iterator, UnifiedAPIIterator)
        self.assertEqual(iterator.get_api_name(), 'google_books')
        self.mock_google.search_by_query.assert_called_once_with("python", limit=10)

    def test_create_lazy_iterator(self):
        """Testa criação de iterador lazy."""
        collection = BookAPICollection()
        collection.add_api(self.mock_google)

        iterator = collection.create_lazy_iterator("python", api_index=0, page_size=5)

        self.assertIsInstance(iterator, LazyAPIIterator)

    def test_create_multi_source_iterator(self):
        """Testa criação de iterador multi-fonte."""
        collection = BookAPICollection()
        collection.add_api(self.mock_google)
        collection.add_api(self.mock_openlibrary)

        iterator = collection.create_multi_source_iterator("python", limit_per_api=10)

        self.assertIsInstance(iterator, MultiSourceIterator)

    def test_empty_collection_error(self):
        """Testa erro ao criar iterador em coleção vazia."""
        collection = BookAPICollection()

        with self.assertRaises(ValueError):
            collection.create_iterator("python")

        with self.assertRaises(ValueError):
            collection.create_lazy_iterator("python")

        with self.assertRaises(ValueError):
            collection.create_multi_source_iterator("python")


class IteratorBookBuilderTest(TestCase):
    """Testes para IteratorBookBuilder."""

    def setUp(self):
        """Configura dados de teste."""
        self.sample_results = [
            {
                'title': 'Test Book 1',
                'authors': ['Test Author 1'],
                'isbn': '9781111111111',
                'publisher': 'Test Publisher',
                'published_date': '2020',
                'description': 'Test description',
                'cover_url': 'http://example.com/cover1.jpg',
                'page_count': 300,
                'categories': ['Test'],
                'language': 'en',
                'average_rating': 4.0,
                '_api_source': 'google_books'
            },
            {
                'title': 'Test Book 2',
                'authors': ['Test Author 2'],
                'isbn': '9782222222222',
                'publisher': 'Test Publisher',
                'published_date': '2021',
                'description': 'Test description 2',
                'cover_url': 'http://example.com/cover2.jpg',
                'page_count': 400,
                'categories': ['Test'],
                'language': 'en',
                'average_rating': 4.5,
                '_api_source': 'open_library'
            }
        ]

    def test_build_all(self):
        """Testa construção de todos os livros."""
        iterator = UnifiedAPIIterator(self.sample_results, api_name='google_books')
        builder_helper = IteratorBookBuilder(iterator)

        books = builder_helper.build_all(skip_existing=False)

        self.assertEqual(len(books), 2)
        self.assertEqual(books[0].title, 'Test Book 1')
        self.assertEqual(books[1].title, 'Test Book 2')
        self.assertEqual(books[0].isbn, '9781111111111')
        self.assertEqual(books[1].isbn, '9782222222222')

    def test_build_next(self):
        """Testa construção do próximo livro."""
        iterator = UnifiedAPIIterator(self.sample_results, api_name='google_books')
        builder_helper = IteratorBookBuilder(iterator)

        # Primeiro livro
        book1 = builder_helper.build_next()
        self.assertIsNotNone(book1)
        self.assertEqual(book1.title, 'Test Book 1')

        # Segundo livro
        book2 = builder_helper.build_next()
        self.assertIsNotNone(book2)
        self.assertEqual(book2.title, 'Test Book 2')

        # Não há mais livros
        book3 = builder_helper.build_next()
        self.assertIsNone(book3)

    def test_build_batch(self):
        """Testa construção em lote."""
        iterator = UnifiedAPIIterator(self.sample_results, api_name='google_books')
        builder_helper = IteratorBookBuilder(iterator)

        # Constrói apenas 1 livro
        books = builder_helper.build_batch(1, skip_existing=False)
        self.assertEqual(len(books), 1)
        self.assertEqual(books[0].title, 'Test Book 1')

    def test_skip_existing_books(self):
        """Testa skip de livros existentes."""
        # Cria um livro existente
        Book.objects.create(
            title='Existing Book',
            author='Existing Author',
            isbn='9781111111111'
        )

        iterator = UnifiedAPIIterator(self.sample_results, api_name='google_books')
        builder_helper = IteratorBookBuilder(iterator)

        # build_all com skip_existing=True
        books = builder_helper.build_all(skip_existing=True)

        # Deve ter criado apenas 1 livro (o segundo, pois o primeiro já existe)
        self.assertEqual(len(books), 1)
        self.assertEqual(books[0].title, 'Test Book 2')

    def test_build_with_invalid_data(self):
        """Testa construção com dados inválidos."""
        invalid_results = [
            {
                'title': '',  # Título vazio (inválido)
                'authors': ['Author'],
                'isbn': '9783333333333',
                '_api_source': 'google_books'
            }
        ]

        iterator = UnifiedAPIIterator(invalid_results, api_name='google_books')
        builder_helper = IteratorBookBuilder(iterator)

        # Deve lidar com erro e retornar lista vazia
        books = builder_helper.build_all(skip_existing=False)
        self.assertEqual(len(books), 0)


class IntegrationTest(TestCase):
    """Testes de integração entre todos os componentes."""

    def test_complete_workflow(self):
        """Testa workflow completo: Collection -> Iterator -> Builder."""
        # Mock adapters
        mock_google = Mock(spec=BookAPIInterface)
        mock_google.get_api_name.return_value = 'google_books'
        mock_google.search_by_query.return_value = [
            {
                'title': 'Integration Test Book',
                'authors': ['Integration Author'],
                'isbn': '9789999999999',
                'publisher': 'Integration Publisher',
                'published_date': '2023',
                'description': 'Integration test',
                'cover_url': 'http://example.com/integration.jpg',
                'page_count': 500,
                'categories': ['Integration'],
                'language': 'en',
                'average_rating': 5.0
            }
        ]

        # 1. Cria coleção e adiciona API
        collection = BookAPICollection()
        collection.add_api(mock_google)

        # 2. Cria iterador
        iterator = collection.create_iterator("integration test", limit=10)

        # 3. Usa builder helper para criar livros
        builder_helper = IteratorBookBuilder(iterator)
        books = builder_helper.build_all(skip_existing=False)

        # Verificações
        self.assertEqual(len(books), 1)
        self.assertEqual(books[0].title, 'Integration Test Book')
        self.assertEqual(books[0].source, 'google_books')
        self.assertTrue(Book.objects.filter(isbn='9789999999999').exists())
