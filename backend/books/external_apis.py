"""
Helpers para integração com APIs externas de livros.

Este módulo fornece funções para buscar informações de livros
em APIs externas como Google Books e Open Library.
"""
import requests
from typing import Optional, Dict
import logging

logger = logging.getLogger(__name__)


class GoogleBooksAPI:
    """
    Cliente para interagir com a Google Books API.

    API Documentation: https://developers.google.com/books/docs/v1/using
    """

    BASE_URL = "https://www.googleapis.com/books/v1/volumes"

    @classmethod
    def fetch_by_id(cls, volume_id: str, api_key: Optional[str] = None) -> Optional[Dict]:
        """
        Busca um livro pelo ID do volume no Google Books.

        Args:
            volume_id: ID do volume no Google Books (ex: "hjEFCAAAQBAJ")
            api_key: API key do Google Books (opcional, mas recomendado para evitar rate limits)

        Returns:
            dict: Dados do livro ou None se não encontrado

        Raises:
            requests.exceptions.RequestException: Se houver erro na requisição

        Example:
            >>> data = GoogleBooksAPI.fetch_by_id("hjEFCAAAQBAJ")
            >>> print(data['volumeInfo']['title'])
            'Clean Code'
        """
        url = f"{cls.BASE_URL}/{volume_id}"
        params = {}
        if api_key:
            params['key'] = api_key

        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                logger.warning(f"Livro não encontrado no Google Books: {volume_id}")
                return None
            logger.error(f"Erro ao buscar livro no Google Books: {e}")
            raise
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro de conexão com Google Books API: {e}")
            raise

    @classmethod
    def search(cls, query: str, max_results: int = 10, api_key: Optional[str] = None) -> Optional[Dict]:
        """
        Busca livros por termo de pesquisa.

        Args:
            query: Termo de busca (título, autor, ISBN, etc.)
            max_results: Número máximo de resultados (padrão: 10, máx: 40)
            api_key: API key do Google Books (opcional)

        Returns:
            dict: Resultados da busca com lista de livros

        Example:
            >>> results = GoogleBooksAPI.search("Clean Code Robert Martin")
            >>> for item in results['items']:
            ...     print(item['volumeInfo']['title'])
        """
        params = {
            'q': query,
            'maxResults': min(max_results, 40)  # API limita a 40
        }
        if api_key:
            params['key'] = api_key

        try:
            response = requests.get(cls.BASE_URL, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro ao buscar livros no Google Books: {e}")
            raise

    @classmethod
    def search_by_isbn(cls, isbn: str, api_key: Optional[str] = None) -> Optional[Dict]:
        """
        Busca um livro por ISBN.

        Args:
            isbn: ISBN-10 ou ISBN-13
            api_key: API key do Google Books (opcional)

        Returns:
            dict: Dados do primeiro livro encontrado ou None

        Example:
            >>> data = GoogleBooksAPI.search_by_isbn("9780132350884")
            >>> print(data['volumeInfo']['title'])
            'Clean Code'
        """
        results = cls.search(f"isbn:{isbn}", max_results=1, api_key=api_key)

        if results and 'items' in results and len(results['items']) > 0:
            return results['items'][0]

        logger.warning(f"Livro não encontrado no Google Books com ISBN: {isbn}")
        return None


class OpenLibraryAPI:
    """
    Cliente para interagir com a Open Library API.

    API Documentation: https://openlibrary.org/developers/api
    """

    SEARCH_URL = "https://openlibrary.org/search.json"
    ISBN_URL = "https://openlibrary.org/isbn"

    @classmethod
    def search(cls, query: str, limit: int = 10) -> Optional[Dict]:
        """
        Busca livros por termo de pesquisa.

        Args:
            query: Termo de busca (título, autor, etc.)
            limit: Número máximo de resultados

        Returns:
            dict: Resultados da busca

        Example:
            >>> results = OpenLibraryAPI.search("1984 George Orwell")
            >>> for doc in results['docs']:
            ...     print(doc['title'])
        """
        params = {
            'q': query,
            'limit': limit
        }

        try:
            response = requests.get(cls.SEARCH_URL, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro ao buscar livros no Open Library: {e}")
            raise

    @classmethod
    def fetch_by_isbn(cls, isbn: str) -> Optional[Dict]:
        """
        Busca um livro por ISBN.

        Args:
            isbn: ISBN-10 ou ISBN-13

        Returns:
            dict: Dados do livro ou None se não encontrado

        Example:
            >>> data = OpenLibraryAPI.fetch_by_isbn("0451524934")
            >>> print(data['title'])
            '1984'
        """
        url = f"{cls.ISBN_URL}/{isbn}.json"

        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                logger.warning(f"Livro não encontrado no Open Library: {isbn}")
                return None
            logger.error(f"Erro ao buscar livro no Open Library: {e}")
            raise
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro de conexão com Open Library API: {e}")
            raise
