"""
Padrão Iterator para navegação em resultados de APIs de livros.

O padrão Iterator (GoF Comportamental) permite acessar sequencialmente elementos de uma coleção
sem expor sua representação interna. Este módulo implementa iteradores para resultados de
múltiplas APIs de livros, permitindo iteração unificada e lazy loading.

Componentes:
    - Iterator: BookIterator (interface de iteração)
    - ConcreteIterators: UnifiedAPIIterator, LazyAPIIterator, MultiSourceIterator
    - Aggregate: BookAPICollection (coleção agregada de APIs)
    - Integration: Integra com Adapter e Builder para criar objetos Book

Benefícios:
    - Permite iterar sobre resultados de múltiplas APIs de forma uniforme
    - Suporta lazy loading para economizar requisições
    - Separa a lógica de iteração da lógica de busca
    - Facilita adicionar novos tipos de iteração sem modificar código existente
"""
from abc import ABC, abstractmethod
from typing import Optional, Dict, List, Iterator
import logging

from .adapters import BookAPIInterface, GoogleBooksAdapter, OpenLibraryAdapter
from .builders import BookDirector
from .models import Book

logger = logging.getLogger(__name__)


class BookIterator(ABC):
    """
    Interface Iterator do padrão Iterator.

    Define o contrato que todos os iteradores de livros devem seguir.
    Permite iterar sobre resultados de APIs sem expor detalhes de implementação.
    """

    @abstractmethod
    def __iter__(self):
        """
        Retorna o próprio iterador.

        Returns:
            BookIterator: O próprio iterador
        """
        pass

    @abstractmethod
    def __next__(self) -> Dict:
        """
        Retorna o próximo item normalizado da iteração.

        Returns:
            dict: Próximo livro em formato normalizado (padrão BookAPIInterface)

        Raises:
            StopIteration: Quando não há mais elementos
        """
        pass

    @abstractmethod
    def has_next(self) -> bool:
        """
        Verifica se há mais elementos para iterar.

        Returns:
            bool: True se há mais elementos, False caso contrário
        """
        pass

    @abstractmethod
    def reset(self):
        """
        Reinicia o iterador para a posição inicial.
        """
        pass

    @abstractmethod
    def current_position(self) -> int:
        """
        Retorna a posição atual do iterador.

        Returns:
            int: Índice do elemento atual (0-based)
        """
        pass


class UnifiedAPIIterator(BookIterator):
    """
    Iterador concreto que navega por resultados de uma única API.

    Permite iterar sobre uma lista de resultados de forma controlada,
    mantendo estado da posição atual e oferecendo operações de navegação.

    Exemplo de uso:
        >>> adapter = GoogleBooksAdapter()
        >>> results = adapter.search_by_query("clean code", limit=10)
        >>> iterator = UnifiedAPIIterator(results, api_name='google_books')
        >>> for book_data in iterator:
        ...     print(book_data['title'])
    """

    def __init__(self, results: List[Dict], api_name: str = 'unknown'):
        """
        Inicializa o iterador com uma lista de resultados normalizados.

        Args:
            results: Lista de dicionários com dados normalizados de livros
            api_name: Nome da API origem dos resultados
        """
        self._results = results or []
        self._api_name = api_name
        self._position = 0
        self._total = len(self._results)

    def __iter__(self):
        """Retorna o próprio iterador."""
        return self

    def __next__(self) -> Dict:
        """
        Retorna o próximo livro da lista.

        Returns:
            dict: Próximo livro normalizado

        Raises:
            StopIteration: Quando não há mais elementos
        """
        if not self.has_next():
            raise StopIteration

        result = self._results[self._position]
        self._position += 1
        return result

    def has_next(self) -> bool:
        """Verifica se há mais elementos."""
        return self._position < self._total

    def reset(self):
        """Reinicia o iterador."""
        self._position = 0

    def current_position(self) -> int:
        """Retorna a posição atual."""
        return self._position

    def total_count(self) -> int:
        """
        Retorna o total de elementos na coleção.

        Returns:
            int: Total de livros
        """
        return self._total

    def get_api_name(self) -> str:
        """
        Retorna o nome da API origem.

        Returns:
            str: Nome da API
        """
        return self._api_name

    def peek(self) -> Optional[Dict]:
        """
        Retorna o próximo elemento sem avançar o iterador.

        Returns:
            dict: Próximo livro ou None se não houver mais elementos
        """
        if not self.has_next():
            return None
        return self._results[self._position]

    def skip(self, count: int):
        """
        Pula um número específico de elementos.

        Args:
            count: Número de elementos a pular
        """
        self._position = min(self._position + count, self._total)


class LazyAPIIterator(BookIterator):
    """
    Iterador lazy que busca resultados sob demanda (página por página).

    Evita carregar todos os resultados de uma vez, buscando páginas conforme necessário.
    Ideal para economizar memória e requisições quando não se sabe quantos resultados serão necessários.

    Exemplo de uso:
        >>> adapter = GoogleBooksAdapter()
        >>> iterator = LazyAPIIterator(adapter, query="python programming", page_size=10)
        >>> for i, book_data in enumerate(iterator):
        ...     if i >= 5:  # Processa apenas 5 livros, economizando requisições
        ...         break
        ...     print(book_data['title'])
    """

    def __init__(self, adapter: BookAPIInterface, query: str,
                 page_size: int = 10, max_pages: int = 5):
        """
        Inicializa o iterador lazy.

        Args:
            adapter: Adapter da API a ser consultada
            query: Termo de busca
            page_size: Número de resultados por página
            max_pages: Número máximo de páginas a buscar
        """
        self._adapter = adapter
        self._query = query
        self._page_size = page_size
        self._max_pages = max_pages

        self._current_page = 0
        self._position_in_page = 0
        self._current_results = []
        self._exhausted = False

        # Carrega primeira página
        self._load_next_page()

    def _load_next_page(self):
        """Carrega a próxima página de resultados da API."""
        if self._current_page >= self._max_pages:
            self._exhausted = True
            return

        try:
            # Busca próxima página
            # Nota: Algumas APIs suportam offset/paginação, outras não
            # Para simplificar, estamos buscando page_size resultados
            results = self._adapter.search_by_query(
                self._query,
                limit=self._page_size
            )

            if not results:
                self._exhausted = True
                return

            self._current_results = results
            self._position_in_page = 0
            self._current_page += 1

            logger.debug(f"Loaded page {self._current_page} with {len(results)} results")

        except Exception as e:
            logger.error(f"Erro ao carregar página {self._current_page + 1}: {e}")
            self._exhausted = True

    def __iter__(self):
        """Retorna o próprio iterador."""
        return self

    def __next__(self) -> Dict:
        """
        Retorna o próximo livro, carregando nova página se necessário.

        Returns:
            dict: Próximo livro normalizado

        Raises:
            StopIteration: Quando não há mais elementos
        """
        if not self.has_next():
            raise StopIteration

        result = self._current_results[self._position_in_page]
        self._position_in_page += 1

        # Se chegou ao fim da página atual, tenta carregar próxima
        if self._position_in_page >= len(self._current_results):
            self._load_next_page()

        return result

    def has_next(self) -> bool:
        """Verifica se há mais elementos."""
        if self._exhausted:
            return False
        if self._position_in_page < len(self._current_results):
            return True
        return False

    def reset(self):
        """Reinicia o iterador (requer nova busca)."""
        self._current_page = 0
        self._position_in_page = 0
        self._current_results = []
        self._exhausted = False
        self._load_next_page()

    def current_position(self) -> int:
        """Retorna a posição global atual."""
        return (self._current_page - 1) * self._page_size + self._position_in_page

    def get_api_name(self) -> str:
        """Retorna o nome da API."""
        return self._adapter.get_api_name()


class MultiSourceIterator(BookIterator):
    """
    Iterador que combina resultados de múltiplas APIs em sequência.

    Permite iterar sobre resultados de várias APIs como se fossem uma única coleção,
    fornecendo fallback automático e agregação de resultados.

    Exemplo de uso:
        >>> google = GoogleBooksAdapter()
        >>> open_lib = OpenLibraryAdapter()
        >>> iterator = MultiSourceIterator([google, open_lib], query="1984 orwell")
        >>> for book_data in iterator:
        ...     print(f"{book_data['title']} (from {book_data['_api_source']})")
    """

    def __init__(self, adapters: List[BookAPIInterface], query: str,
                 limit_per_api: int = 10, deduplicate_by_isbn: bool = True):
        """
        Inicializa o iterador multi-fonte.

        Args:
            adapters: Lista de adapters de APIs a consultar
            query: Termo de busca
            limit_per_api: Limite de resultados por API
            deduplicate_by_isbn: Se True, remove duplicatas baseado em ISBN
        """
        self._adapters = adapters
        self._query = query
        self._limit_per_api = limit_per_api
        self._deduplicate = deduplicate_by_isbn

        self._all_results = []
        self._position = 0
        self._seen_isbns = set()

        # Carrega resultados de todas as APIs
        self._load_all_results()

    def _load_all_results(self):
        """Carrega e combina resultados de todas as APIs."""
        for adapter in self._adapters:
            try:
                results = adapter.search_by_query(self._query, limit=self._limit_per_api)
                api_name = adapter.get_api_name()

                for result in results:
                    # Adiciona metadado de origem
                    result['_api_source'] = api_name

                    # Deduplicação por ISBN se habilitada
                    if self._deduplicate:
                        isbn = result.get('isbn')
                        if isbn and isbn in self._seen_isbns:
                            logger.debug(f"Skipping duplicate ISBN: {isbn}")
                            continue
                        if isbn:
                            self._seen_isbns.add(isbn)

                    self._all_results.append(result)

                logger.info(f"Loaded {len(results)} results from {api_name}")

            except Exception as e:
                logger.error(f"Erro ao buscar em {adapter.get_api_name()}: {e}")
                continue

        logger.info(f"Total de resultados combinados: {len(self._all_results)}")

    def __iter__(self):
        """Retorna o próprio iterador."""
        return self

    def __next__(self) -> Dict:
        """
        Retorna o próximo livro da coleção agregada.

        Returns:
            dict: Próximo livro normalizado com metadado '_api_source'

        Raises:
            StopIteration: Quando não há mais elementos
        """
        if not self.has_next():
            raise StopIteration

        result = self._all_results[self._position]
        self._position += 1
        return result

    def has_next(self) -> bool:
        """Verifica se há mais elementos."""
        return self._position < len(self._all_results)

    def reset(self):
        """Reinicia o iterador."""
        self._position = 0

    def current_position(self) -> int:
        """Retorna a posição atual."""
        return self._position

    def total_count(self) -> int:
        """
        Retorna o total de resultados agregados.

        Returns:
            int: Total de livros
        """
        return len(self._all_results)

    def group_by_source(self) -> Dict[str, List[Dict]]:
        """
        Agrupa resultados por API de origem.

        Returns:
            dict: Dicionário {api_name: [resultados]}
        """
        grouped = {}
        for result in self._all_results:
            api_source = result.get('_api_source', 'unknown')
            if api_source not in grouped:
                grouped[api_source] = []
            grouped[api_source].append(result)
        return grouped


class BookAPICollection:
    """
    Aggregate (Coleção Agregada) do padrão Iterator.

    Encapsula a lógica de criação de iteradores para diferentes estratégias de busca.
    Fornece uma interface fluente para criar e configurar iteradores.

    Exemplo de uso:
        >>> collection = BookAPICollection()
        >>> collection.add_api(GoogleBooksAdapter())
        >>> collection.add_api(OpenLibraryAdapter())
        >>>
        >>> # Iterador simples (carrega tudo de uma vez)
        >>> iterator = collection.create_iterator("python", strategy='unified')
        >>>
        >>> # Iterador lazy (carrega sob demanda)
        >>> iterator = collection.create_lazy_iterator("django", page_size=5)
        >>>
        >>> # Iterador multi-fonte (combina APIs)
        >>> iterator = collection.create_multi_source_iterator("clean code")
    """

    def __init__(self):
        """Inicializa a coleção vazia."""
        self._apis: List[BookAPIInterface] = []

    def add_api(self, adapter: BookAPIInterface):
        """
        Adiciona um adapter de API à coleção.

        Args:
            adapter: Adapter de API a adicionar

        Returns:
            self: Para permitir method chaining
        """
        self._apis.append(adapter)
        return self

    def create_iterator(self, query: str, api_index: int = 0,
                       limit: int = 10) -> UnifiedAPIIterator:
        """
        Cria um iterador unificado para uma API específica.

        Args:
            query: Termo de busca
            api_index: Índice da API a usar (default: 0)
            limit: Limite de resultados

        Returns:
            UnifiedAPIIterator: Iterador configurado

        Raises:
            IndexError: Se api_index inválido
        """
        if not self._apis:
            raise ValueError("Nenhuma API adicionada à coleção")

        adapter = self._apis[api_index]
        results = adapter.search_by_query(query, limit=limit)
        return UnifiedAPIIterator(results, api_name=adapter.get_api_name())

    def create_lazy_iterator(self, query: str, api_index: int = 0,
                           page_size: int = 10, max_pages: int = 5) -> LazyAPIIterator:
        """
        Cria um iterador lazy para carregamento sob demanda.

        Args:
            query: Termo de busca
            api_index: Índice da API a usar (default: 0)
            page_size: Número de resultados por página
            max_pages: Número máximo de páginas

        Returns:
            LazyAPIIterator: Iterador lazy configurado

        Raises:
            IndexError: Se api_index inválido
        """
        if not self._apis:
            raise ValueError("Nenhuma API adicionada à coleção")

        adapter = self._apis[api_index]
        return LazyAPIIterator(adapter, query, page_size, max_pages)

    def create_multi_source_iterator(self, query: str, limit_per_api: int = 10,
                                   deduplicate: bool = True) -> MultiSourceIterator:
        """
        Cria um iterador que combina resultados de todas as APIs.

        Args:
            query: Termo de busca
            limit_per_api: Limite de resultados por API
            deduplicate: Se True, remove duplicatas por ISBN

        Returns:
            MultiSourceIterator: Iterador multi-fonte configurado
        """
        if not self._apis:
            raise ValueError("Nenhuma API adicionada à coleção")

        return MultiSourceIterator(self._apis, query, limit_per_api, deduplicate)

    def get_apis(self) -> List[BookAPIInterface]:
        """
        Retorna lista de APIs registradas.

        Returns:
            list: Lista de adapters
        """
        return self._apis.copy()


class IteratorBookBuilder:
    """
    Helper que integra Iterator com Builder para converter resultados em objetos Book.

    Permite iterar sobre resultados de APIs e criar objetos Book automaticamente
    usando o padrão Builder, integrando os três padrões GoF.

    Exemplo de uso:
        >>> collection = BookAPICollection()
        >>> collection.add_api(GoogleBooksAdapter())
        >>> iterator = collection.create_iterator("clean code")
        >>>
        >>> builder_helper = IteratorBookBuilder(iterator)
        >>> books = builder_helper.build_all()  # Cria todos os Books
        >>> print(f"Criados {len(books)} livros no banco")
    """

    def __init__(self, iterator: BookIterator):
        """
        Inicializa o helper com um iterador.

        Args:
            iterator: Iterador de resultados de API
        """
        self._iterator = iterator
        self._director = BookDirector()

    def build_all(self, skip_existing: bool = True) -> List[Book]:
        """
        Constrói objetos Book para todos os resultados do iterador.

        Args:
            skip_existing: Se True, pula livros que já existem (por ISBN)

        Returns:
            list: Lista de objetos Book criados
        """
        books = []

        for normalized_data in self._iterator:
            try:
                # Verifica se livro já existe (por ISBN)
                if skip_existing:
                    isbn = normalized_data.get('isbn')
                    if isbn and Book.objects.filter(isbn=isbn).exists():
                        logger.debug(f"Livro com ISBN {isbn} já existe, pulando")
                        continue

                # Obtém nome da API
                api_name = normalized_data.get('_api_source', 'unknown')

                # Usa o Director para construir o Book
                book = self._director.construct_from_adapter(normalized_data, api_name)
                books.append(book)

                logger.info(f"Criado livro: {book.title}")

            except Exception as e:
                logger.error(f"Erro ao criar livro: {e}")
                continue

        return books

    def build_next(self) -> Optional[Book]:
        """
        Constrói o próximo Book do iterador.

        Returns:
            Book: Próximo livro criado ou None se não houver mais elementos
        """
        try:
            normalized_data = next(self._iterator)
            api_name = normalized_data.get('_api_source', 'unknown')
            return self._director.construct_from_adapter(normalized_data, api_name)
        except StopIteration:
            return None
        except Exception as e:
            logger.error(f"Erro ao criar livro: {e}")
            return None

    def build_batch(self, count: int, skip_existing: bool = True) -> List[Book]:
        """
        Constrói um número específico de Books.

        Args:
            count: Número de livros a criar
            skip_existing: Se True, pula livros existentes

        Returns:
            list: Lista de Books criados (pode ter menos que count se iterador acabar)
        """
        books = []
        created = 0

        while created < count and self._iterator.has_next():
            try:
                normalized_data = next(self._iterator)

                # Verifica se livro já existe
                if skip_existing:
                    isbn = normalized_data.get('isbn')
                    if isbn and Book.objects.filter(isbn=isbn).exists():
                        continue

                api_name = normalized_data.get('_api_source', 'unknown')
                book = self._director.construct_from_adapter(normalized_data, api_name)
                books.append(book)
                created += 1

            except StopIteration:
                break
            except Exception as e:
                logger.error(f"Erro ao criar livro: {e}")
                continue

        return books
