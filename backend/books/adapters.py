"""
Padrão Adapter para APIs externas de livros.

O padrão Adapter (GoF Estrutural) permite que interfaces incompatíveis trabalhem juntas.
Este módulo cria uma interface unificada para diferentes APIs de livros (Google Books, Open Library),
facilitando a adição de novas APIs e tornando o código mais flexível e testável.

Componentes:
    - Target: BookAPIInterface (interface esperada pelo cliente)
    - Adapters: GoogleBooksAdapter, OpenLibraryAdapter (convertem APIs para interface comum)
    - Adaptees: GoogleBooksAPI, OpenLibraryAPI (classes existentes com interfaces diferentes)
"""
from abc import ABC, abstractmethod
from typing import Optional, Dict, List
import logging

from .external_apis import GoogleBooksAPI, OpenLibraryAPI

logger = logging.getLogger(__name__)


class BookAPIInterface(ABC):
    """
    Interface Target do padrão Adapter.

    Define o contrato comum que todos os adapters de APIs de livros devem seguir.
    Permite que o código cliente trabalhe com qualquer API de forma uniforme.

    Estrutura padronizada de resposta:
    {
        'title': str,
        'authors': List[str],
        'isbn': Optional[str],
        'publisher': Optional[str],
        'published_date': Optional[str],  # Formato: 'YYYY' ou 'YYYY-MM-DD'
        'description': Optional[str],
        'cover_url': Optional[str],
        'page_count': Optional[int],
        'categories': List[str],
        'language': Optional[str],
        'average_rating': Optional[float]
    }
    """

    @abstractmethod
    def search_by_isbn(self, isbn: str) -> Optional[Dict]:
        """
        Busca um livro por ISBN.

        Args:
            isbn: ISBN-10 ou ISBN-13

        Returns:
            dict: Dados do livro em formato padronizado ou None se não encontrado
        """
        pass

    @abstractmethod
    def search_by_query(self, query: str, limit: int = 10) -> List[Dict]:
        """
        Busca livros por termo de pesquisa.

        Args:
            query: Termo de busca (título, autor, etc.)
            limit: Número máximo de resultados

        Returns:
            list: Lista de livros em formato padronizado
        """
        pass

    @abstractmethod
    def fetch_by_id(self, resource_id: str) -> Optional[Dict]:
        """
        Busca um livro por ID específico da API.

        Args:
            resource_id: ID do recurso na API específica

        Returns:
            dict: Dados do livro em formato padronizado ou None se não encontrado
        """
        pass

    @abstractmethod
    def normalize_to_standard_format(self, api_data: dict) -> Dict:
        """
        Converte dados da API específica para formato padronizado.

        Args:
            api_data: Dados brutos da API

        Returns:
            dict: Dados normalizados no formato padrão
        """
        pass

    @abstractmethod
    def get_api_name(self) -> str:
        """
        Retorna o nome da API para identificação.

        Returns:
            str: Nome da API (ex: 'google_books', 'open_library')
        """
        pass


class GoogleBooksAdapter(BookAPIInterface):
    """
    Adapter que converte a interface do GoogleBooksAPI para BookAPIInterface.

    Adaptee: GoogleBooksAPI
    Target: BookAPIInterface

    Exemplo de uso:
        adapter = GoogleBooksAdapter(api_key='YOUR_KEY')
        book_data = adapter.search_by_isbn('9780132350884')
        print(book_data['title'])  # 'Clean Code'
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Inicializa o adapter com uma instância do GoogleBooksAPI.

        Args:
            api_key: API key do Google Books (opcional, mas recomendado)
        """
        self.api = GoogleBooksAPI()
        self.api_key = api_key

    def search_by_isbn(self, isbn: str) -> Optional[Dict]:
        """
        Adapta GoogleBooksAPI.search_by_isbn() para interface padronizada.

        Args:
            isbn: ISBN-10 ou ISBN-13

        Returns:
            dict: Dados do livro normalizados ou None se não encontrado
        """
        try:
            api_data = self.api.search_by_isbn(isbn, self.api_key)
            if not api_data:
                return None
            return self.normalize_to_standard_format(api_data)
        except Exception as e:
            logger.error(f"Erro ao buscar ISBN {isbn} no Google Books: {e}")
            return None

    def search_by_query(self, query: str, limit: int = 10) -> List[Dict]:
        """
        Adapta GoogleBooksAPI.search() para interface padronizada.

        Args:
            query: Termo de busca
            limit: Número máximo de resultados (máx: 40)

        Returns:
            list: Lista de livros normalizados
        """
        try:
            api_data = self.api.search(query, max_results=limit, api_key=self.api_key)
            if not api_data or 'items' not in api_data:
                return []

            results = []
            for item in api_data.get('items', []):
                try:
                    normalized = self.normalize_to_standard_format(item)
                    results.append(normalized)
                except Exception as e:
                    logger.warning(f"Erro ao normalizar item do Google Books: {e}")
                    continue

            return results
        except Exception as e:
            logger.error(f"Erro ao buscar '{query}' no Google Books: {e}")
            return []

    def fetch_by_id(self, resource_id: str) -> Optional[Dict]:
        """
        Adapta GoogleBooksAPI.fetch_by_id() para interface padronizada.

        Args:
            resource_id: Volume ID do Google Books (ex: 'hjEFCAAAQBAJ')

        Returns:
            dict: Dados do livro normalizados ou None se não encontrado
        """
        try:
            api_data = self.api.fetch_by_id(resource_id, self.api_key)
            if not api_data:
                return None
            return self.normalize_to_standard_format(api_data)
        except Exception as e:
            logger.error(f"Erro ao buscar ID {resource_id} no Google Books: {e}")
            return None

    def normalize_to_standard_format(self, api_data: dict) -> Dict:
        """
        Converte estrutura do Google Books para formato padronizado.

        Estrutura Google Books:
        {
          "volumeInfo": {
            "title": "...",
            "authors": [...],
            "industryIdentifiers": [{...}],
            ...
          }
        }

        Args:
            api_data: Dados brutos do Google Books

        Returns:
            dict: Dados normalizados
        """
        volume_info = api_data.get('volumeInfo', {})

        # Extrair ISBN (preferir ISBN-13)
        isbn = None
        identifiers = volume_info.get('industryIdentifiers', [])
        for identifier in identifiers:
            if identifier.get('type') == 'ISBN_13':
                isbn = identifier.get('identifier', '').replace('-', '')
                break
        else:
            # Fallback para ISBN-10
            for identifier in identifiers:
                if identifier.get('type') == 'ISBN_10':
                    isbn = identifier.get('identifier', '').replace('-', '')
                    break

        # Extrair ano de publicação
        published_date = volume_info.get('publishedDate', '')

        # Extrair URL da capa (preferir melhor qualidade)
        image_links = volume_info.get('imageLinks', {})
        cover_url = (
            image_links.get('extraLarge') or
            image_links.get('large') or
            image_links.get('medium') or
            image_links.get('thumbnail') or
            image_links.get('smallThumbnail')
        )

        return {
            'title': volume_info.get('title', ''),
            'authors': volume_info.get('authors', []),
            'isbn': isbn,
            'publisher': volume_info.get('publisher'),
            'published_date': published_date,
            'description': volume_info.get('description'),
            'cover_url': cover_url,
            'page_count': volume_info.get('pageCount'),
            'categories': volume_info.get('categories', []),
            'language': volume_info.get('language'),
            'average_rating': volume_info.get('averageRating')
        }

    def get_api_name(self) -> str:
        """Retorna o nome da API."""
        return 'google_books'


class OpenLibraryAdapter(BookAPIInterface):
    """
    Adapter que converte a interface do OpenLibraryAPI para BookAPIInterface.

    Adaptee: OpenLibraryAPI
    Target: BookAPIInterface

    Exemplo de uso:
        adapter = OpenLibraryAdapter()
        book_data = adapter.search_by_isbn('0451524934')
        print(book_data['title'])  # '1984'
    """

    def __init__(self):
        """Inicializa o adapter com uma instância do OpenLibraryAPI."""
        self.api = OpenLibraryAPI()

    def search_by_isbn(self, isbn: str) -> Optional[Dict]:
        """
        Adapta OpenLibraryAPI.fetch_by_isbn() para interface padronizada.

        Args:
            isbn: ISBN-10 ou ISBN-13

        Returns:
            dict: Dados do livro normalizados ou None se não encontrado
        """
        try:
            api_data = self.api.fetch_by_isbn(isbn)
            if not api_data:
                return None
            return self.normalize_to_standard_format(api_data)
        except Exception as e:
            logger.error(f"Erro ao buscar ISBN {isbn} no Open Library: {e}")
            return None

    def search_by_query(self, query: str, limit: int = 10) -> List[Dict]:
        """
        Adapta OpenLibraryAPI.search() para interface padronizada.

        Args:
            query: Termo de busca
            limit: Número máximo de resultados

        Returns:
            list: Lista de livros normalizados
        """
        try:
            api_data = self.api.search(query, limit=limit)
            if not api_data or 'docs' not in api_data:
                return []

            results = []
            for doc in api_data.get('docs', []):
                try:
                    normalized = self.normalize_to_standard_format(doc)
                    results.append(normalized)
                except Exception as e:
                    logger.warning(f"Erro ao normalizar item do Open Library: {e}")
                    continue

            return results
        except Exception as e:
            logger.error(f"Erro ao buscar '{query}' no Open Library: {e}")
            return []

    def fetch_by_id(self, resource_id: str) -> Optional[Dict]:
        """
        Open Library não possui fetch por ID direto.

        Args:
            resource_id: Não utilizado

        Returns:
            None: Não implementado para Open Library
        """
        logger.warning("fetch_by_id não é suportado pelo Open Library")
        return None

    def normalize_to_standard_format(self, api_data: dict) -> Dict:
        """
        Converte estrutura do Open Library para formato padronizado.

        Estrutura Open Library (search):
        {
          "title": "...",
          "author_name": [...],
          "isbn": [...],
          "first_publish_year": 1984,
          "cover_i": 12345,
          ...
        }

        Estrutura Open Library (ISBN):
        {
          "title": "...",
          "authors": [{"name": "..."}],
          "publishers": [...],
          ...
        }

        Args:
            api_data: Dados brutos do Open Library

        Returns:
            dict: Dados normalizados
        """
        # Extrair autores (formato varia entre search e ISBN endpoints)
        authors = []
        if 'author_name' in api_data:
            # Formato search
            authors = api_data.get('author_name', [])
        elif 'authors' in api_data:
            # Formato ISBN
            authors = [author.get('name', '') for author in api_data.get('authors', [])]

        # Extrair ISBN (preferir o mais longo, geralmente ISBN-13)
        isbn = None
        isbns = api_data.get('isbn', [])
        if isbns:
            isbn = max(isbns, key=len).replace('-', '')

        # Extrair editora (pegar primeira da lista)
        publisher = None
        publishers = api_data.get('publisher', api_data.get('publishers', []))
        if publishers and len(publishers) > 0:
            publisher = publishers[0]

        # Extrair ano de publicação
        published_date = None
        year = api_data.get('first_publish_year', api_data.get('publish_date'))
        if year:
            published_date = str(year) if isinstance(year, int) else year

        # Construir URL da capa
        cover_url = None
        cover_id = api_data.get('cover_i', api_data.get('covers', [None])[0])
        if cover_id:
            cover_url = f"https://covers.openlibrary.org/b/id/{cover_id}-L.jpg"

        # Extrair categorias/assuntos (limitar a 5)
        categories = api_data.get('subject', [])[:5]

        # Mapear idioma (Open Library usa códigos de 3 letras)
        language = None
        languages = api_data.get('language', [])
        if languages:
            lang_code = languages[0] if isinstance(languages, list) else languages
            # Mapeamento simples
            lang_map = {
                'eng': 'en',
                'por': 'pt-BR',
                'spa': 'es',
                'fre': 'fr',
                'ger': 'de'
            }
            language = lang_map.get(lang_code, lang_code)

        # Extrair número de páginas
        page_count = api_data.get('number_of_pages')

        return {
            'title': api_data.get('title', ''),
            'authors': authors,
            'isbn': isbn,
            'publisher': publisher,
            'published_date': published_date,
            'description': None,  # Open Library search não retorna descrição
            'cover_url': cover_url,
            'page_count': page_count,
            'categories': categories,
            'language': language,
            'average_rating': None  # Open Library não fornece rating
        }

    def get_api_name(self) -> str:
        """Retorna o nome da API."""
        return 'open_library'


# Factory para facilitar criação de adapters
def create_adapter(api_name: str, **kwargs) -> BookAPIInterface:
    """
    Factory method para criar adapters de forma dinâmica.

    Args:
        api_name: Nome da API ('google_books' ou 'open_library')
        **kwargs: Argumentos adicionais para o construtor do adapter

    Returns:
        BookAPIInterface: Instância do adapter apropriado

    Raises:
        ValueError: Se api_name não for reconhecido

    Example:
        >>> adapter = create_adapter('google_books', api_key='YOUR_KEY')
        >>> book = adapter.search_by_isbn('9780132350884')
    """
    adapters = {
        'google_books': GoogleBooksAdapter,
        'open_library': OpenLibraryAdapter
    }

    if api_name not in adapters:
        raise ValueError(f"API desconhecida: {api_name}. Opções: {list(adapters.keys())}")

    return adapters[api_name](**kwargs)
