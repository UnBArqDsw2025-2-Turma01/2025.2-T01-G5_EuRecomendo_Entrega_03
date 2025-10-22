"""
Padrão Builder para construção de objetos Book.

O padrão Builder separa a construção de um objeto complexo de sua representação,
permitindo que o mesmo processo de construção crie diferentes representações.
"""
from typing import Optional, List, Dict
from .models import Book
from .adapters import BookAPIInterface


class BookBuilder:
    """
    Builder para construção progressiva e validada de objetos Book.

    Permite criar livros de forma fluente (fluent interface) com validação
    incremental de cada campo.

    Exemplo de uso:
        builder = BookBuilder()
        book = (builder
            .set_title("Clean Code")
            .set_author("Robert C. Martin")
            .set_isbn("9780132350884")
            .set_publication_year(2008)
            .build())
    """

    def __init__(self):
        """Inicializa o builder e reseta o estado interno."""
        self.reset()

    def reset(self):
        """
        Limpa o builder para uma nova construção.

        Returns:
            self: Para permitir method chaining
        """
        self._book_data = {
            'categories': [],
            'language': 'pt-BR',
            'source': 'manual'
        }
        return self

    # === Campos Básicos (Obrigatórios) ===

    def set_title(self, title: str):
        """
        Define o título do livro (campo obrigatório).

        Args:
            title: Título do livro

        Returns:
            self: Para permitir method chaining

        Raises:
            ValueError: Se título vazio ou muito longo
        """
        if not title or not title.strip():
            raise ValueError("Título não pode ser vazio")
        if len(title) > 255:
            raise ValueError("Título não pode exceder 255 caracteres")
        self._book_data['title'] = title.strip()
        return self

    def set_author(self, author: str):
        """
        Define o autor do livro (campo obrigatório).

        Suporta múltiplos autores separados por vírgula.

        Args:
            author: Nome do(s) autor(es)

        Returns:
            self: Para permitir method chaining

        Raises:
            ValueError: Se autor vazio ou muito longo
        """
        if not author or not author.strip():
            raise ValueError("Autor não pode ser vazio")
        if len(author) > 255:
            raise ValueError("Autor não pode exceder 255 caracteres")
        self._book_data['author'] = author.strip()
        return self

    def set_genre(self, genre: str):
        """
        Define o gênero principal do livro.

        Args:
            genre: Gênero principal (ex: "Ficção", "Romance", "Técnico")

        Returns:
            self: Para permitir method chaining
        """
        if genre and len(genre) > 100:
            raise ValueError("Gênero não pode exceder 100 caracteres")
        self._book_data['genre'] = genre.strip() if genre else ''
        return self

    # === Metadados ===

    def set_isbn(self, isbn: str):
        """
        Define o ISBN do livro com validação de formato.

        Aceita ISBN-10 ou ISBN-13. Remove automaticamente hífens e espaços.

        Args:
            isbn: Código ISBN

        Returns:
            self: Para permitir method chaining

        Raises:
            ValueError: Se ISBN não tiver 10 ou 13 dígitos
        """
        if not isbn:
            return self

        # Remove hífens, espaços e caracteres especiais
        cleaned_isbn = ''.join(c for c in isbn if c.isdigit())

        if len(cleaned_isbn) not in [10, 13]:
            raise ValueError(f"ISBN inválido. Deve ter 10 ou 13 dígitos. Recebido: {len(cleaned_isbn)}")

        self._book_data['isbn'] = cleaned_isbn
        return self

    def set_publisher(self, publisher: str):
        """
        Define a editora do livro.

        Args:
            publisher: Nome da editora

        Returns:
            self: Para permitir method chaining
        """
        if publisher and len(publisher) > 255:
            raise ValueError("Editora não pode exceder 255 caracteres")
        self._book_data['publisher'] = publisher.strip() if publisher else ''
        return self

    def set_publication_year(self, year: int):
        """
        Define o ano de publicação com validação de intervalo.

        Args:
            year: Ano de publicação (1000-2030)

        Returns:
            self: Para permitir method chaining

        Raises:
            ValueError: Se ano fora do intervalo válido
        """
        if year is None:
            return self

        if not isinstance(year, int):
            raise ValueError(f"Ano deve ser um inteiro. Recebido: {type(year).__name__}")

        if year < 1000 or year > 2030:
            raise ValueError(f"Ano de publicação inválido: {year}. Deve estar entre 1000 e 2030")

        self._book_data['publication_year'] = year
        return self

    def set_description(self, description: str):
        """
        Define a sinopse/descrição do livro.

        Args:
            description: Sinopse ou descrição do livro

        Returns:
            self: Para permitir method chaining
        """
        self._book_data['description'] = description.strip() if description else ''
        return self

    def set_cover_url(self, url: str):
        """
        Define a URL da capa do livro.

        Args:
            url: URL da imagem da capa

        Returns:
            self: Para permitir method chaining

        Raises:
            ValueError: Se URL inválida (validação básica)
        """
        if url and not (url.startswith('http://') or url.startswith('https://')):
            raise ValueError(f"URL da capa inválida: {url}")

        self._book_data['cover_url'] = url if url else None
        return self

    def set_page_count(self, pages: int):
        """
        Define o número de páginas do livro.

        Args:
            pages: Número de páginas

        Returns:
            self: Para permitir method chaining

        Raises:
            ValueError: Se número de páginas negativo ou zero
        """
        if pages is None:
            return self

        if not isinstance(pages, int):
            raise ValueError(f"Número de páginas deve ser um inteiro. Recebido: {type(pages).__name__}")

        if pages <= 0:
            raise ValueError(f"Número de páginas deve ser positivo: {pages}")

        self._book_data['page_count'] = pages
        return self

    def set_language(self, language: str):
        """
        Define o idioma do livro (código ISO 639-1).

        Args:
            language: Código do idioma (ex: 'pt-BR', 'en', 'es')

        Returns:
            self: Para permitir method chaining
        """
        if language and len(language) > 10:
            raise ValueError("Código de idioma não pode exceder 10 caracteres")
        self._book_data['language'] = language if language else 'pt-BR'
        return self

    # === Campos JSON ===

    def add_category(self, category: str):
        """
        Adiciona uma categoria/gênero à lista de categorias.

        Args:
            category: Nome da categoria

        Returns:
            self: Para permitir method chaining
        """
        if category and category.strip():
            if 'categories' not in self._book_data:
                self._book_data['categories'] = []
            if category.strip() not in self._book_data['categories']:
                self._book_data['categories'].append(category.strip())
        return self

    def set_categories(self, categories: List[str]):
        """
        Define a lista completa de categorias (substitui existentes).

        Args:
            categories: Lista de categorias

        Returns:
            self: Para permitir method chaining
        """
        self._book_data['categories'] = [c.strip() for c in categories if c and c.strip()]
        return self

    def set_average_rating(self, rating: float):
        """
        Define a avaliação média do livro.

        Args:
            rating: Avaliação de 0.0 a 5.0

        Returns:
            self: Para permitir method chaining

        Raises:
            ValueError: Se rating fora do intervalo 0.0-5.0
        """
        if rating is None:
            return self

        if not isinstance(rating, (int, float)):
            raise ValueError(f"Rating deve ser um número. Recebido: {type(rating).__name__}")

        if rating < 0.0 or rating > 5.0:
            raise ValueError(f"Rating deve estar entre 0.0 e 5.0. Recebido: {rating}")

        self._book_data['average_rating'] = round(float(rating), 2)
        return self

    # === Metadados de Controle ===

    def set_source(self, source: str):
        """
        Define a origem dos dados do livro.

        Args:
            source: Origem ('manual', 'google_books', 'open_library')

        Returns:
            self: Para permitir method chaining
        """
        valid_sources = ['manual', 'google_books', 'open_library']
        if source and source not in valid_sources:
            raise ValueError(f"Source inválido: {source}. Deve ser um de: {valid_sources}")
        self._book_data['source'] = source if source else 'manual'
        return self

    # === Build ===

    def build(self) -> Book:
        """
        Valida os dados e constrói o objeto Book.

        Realiza validação final e cria/salva o objeto no banco de dados.

        Returns:
            Book: Objeto Book criado e salvo

        Raises:
            ValueError: Se campos obrigatórios estiverem faltando
        """
        # Validação final: campos obrigatórios
        if 'title' not in self._book_data or not self._book_data['title']:
            raise ValueError("Título é obrigatório para criar um livro")

        if 'author' not in self._book_data or not self._book_data['author']:
            raise ValueError("Autor é obrigatório para criar um livro")

        # Cria o objeto Book
        book = Book(**self._book_data)

        # Salva no banco de dados
        book.save()

        # Reset para permitir reutilização do builder
        self.reset()

        return book

    def get_data(self) -> dict:
        """
        Retorna os dados atuais do builder sem criar o objeto.

        Útil para debug ou preview.

        Returns:
            dict: Dados atuais do builder
        """
        return self._book_data.copy()


class BookDirector:
    """
    Director que encapsula 'receitas' para construir Books de diferentes fontes.

    O Director conhece a estrutura de dados de cada API externa e sabe como
    usar o Builder para transformá-los em objetos Book válidos.

    Exemplo de uso:
        director = BookDirector()
        book = director.construct_from_google_books(google_api_response)
    """

    def __init__(self):
        """Inicializa o director com um BookBuilder."""
        self.builder = BookBuilder()

    def construct_simple_book(self, title: str, author: str, genre: str = '') -> Book:
        """
        Constrói um livro simples com apenas título, autor e gênero.

        Usado para criação manual rápida.

        Args:
            title: Título do livro
            author: Autor do livro
            genre: Gênero do livro (opcional)

        Returns:
            Book: Objeto Book criado e salvo

        Example:
            >>> director = BookDirector()
            >>> book = director.construct_simple_book("1984", "George Orwell", "Ficção")
        """
        self.builder.reset()
        self.builder.set_title(title)
        self.builder.set_author(author)
        if genre:
            self.builder.set_genre(genre)
        self.builder.set_source('manual')
        return self.builder.build()

    def construct_from_adapter(self, normalized_data: Dict, api_name: str) -> Book:
        """
        Constrói um Book a partir de dados já normalizados por um Adapter.

        Este método trabalha com a saída padronizada dos Adapters (BookAPIInterface),
        tornando a construção independente da API específica usada.

        Args:
            normalized_data: Dados normalizados pelo adapter com estrutura:
                {
                    'title': str,
                    'authors': List[str],
                    'isbn': Optional[str],
                    'publisher': Optional[str],
                    'published_date': Optional[str],
                    'description': Optional[str],
                    'cover_url': Optional[str],
                    'page_count': Optional[int],
                    'categories': List[str],
                    'language': Optional[str],
                    'average_rating': Optional[float]
                }
            api_name: Nome da API origem ('google_books', 'open_library', etc.)

        Returns:
            Book: Objeto Book criado e salvo

        Raises:
            ValueError: Se dados essenciais (título) estiverem faltando

        Example:
            >>> from books.adapters import GoogleBooksAdapter
            >>> adapter = GoogleBooksAdapter()
            >>> normalized = adapter.search_by_isbn('9780132350884')
            >>> director = BookDirector()
            >>> book = director.construct_from_adapter(normalized, 'google_books')
        """
        # Reseta o builder
        self.builder.reset()

        # Título (obrigatório)
        title = normalized_data.get('title', '')
        if not title:
            raise ValueError("Dados normalizados sem título")
        self.builder.set_title(title)

        # Autores (obrigatório, pode ser lista)
        authors = normalized_data.get('authors', [])
        if authors:
            # Junta múltiplos autores com vírgula
            author_str = ', '.join(authors) if isinstance(authors, list) else str(authors)
            self.builder.set_author(author_str)
        else:
            # Fallback se não houver autor
            self.builder.set_author('Autor Desconhecido')

        # ISBN
        isbn = normalized_data.get('isbn')
        if isbn:
            self.builder.set_isbn(isbn)

        # Editora
        publisher = normalized_data.get('publisher')
        if publisher:
            self.builder.set_publisher(publisher)

        # Ano de publicação (extrair de published_date)
        published_date = normalized_data.get('published_date')
        if published_date:
            try:
                # Extrai os primeiros 4 caracteres (ano)
                year = int(str(published_date)[:4])
                self.builder.set_publication_year(year)
            except (ValueError, IndexError):
                pass  # Ignora se não conseguir extrair o ano

        # Descrição
        description = normalized_data.get('description')
        if description:
            self.builder.set_description(description)

        # Imagem da capa
        cover_url = normalized_data.get('cover_url')
        if cover_url:
            self.builder.set_cover_url(cover_url)

        # Número de páginas
        page_count = normalized_data.get('page_count')
        if page_count and isinstance(page_count, int):
            self.builder.set_page_count(page_count)

        # Idioma
        language = normalized_data.get('language')
        if language:
            self.builder.set_language(language)

        # Categorias (pegar primeira como gênero principal)
        categories = normalized_data.get('categories', [])
        if categories:
            self.builder.set_genre(categories[0])
            for category in categories:
                self.builder.add_category(category)

        # Avaliação média
        average_rating = normalized_data.get('average_rating')
        if average_rating:
            try:
                self.builder.set_average_rating(float(average_rating))
            except (ValueError, TypeError):
                pass  # Ignora se não conseguir converter

        # Marca a origem
        self.builder.set_source(api_name)

        return self.builder.build()

    def construct_from_google_books(self, api_data: dict) -> Book:
        """
        Constrói um Book a partir da resposta da Google Books API.

        Estrutura esperada da API:
        {
          "volumeInfo": {
            "title": "Clean Code",
            "authors": ["Robert C. Martin"],
            "publisher": "Prentice Hall",
            "publishedDate": "2008-08-01",
            "description": "...",
            "industryIdentifiers": [
              {"type": "ISBN_13", "identifier": "9780132350884"}
            ],
            "pageCount": 464,
            "categories": ["Computers"],
            "imageLinks": {"thumbnail": "http://..."},
            "averageRating": 4.5,
            "language": "en"
          }
        }

        Args:
            api_data: Dicionário com resposta da Google Books API

        Returns:
            Book: Objeto Book criado e salvo

        Raises:
            ValueError: Se dados essenciais (título) estiverem faltando

        Example:
            >>> response = requests.get('https://www.googleapis.com/books/v1/volumes/BOOK_ID')
            >>> book = director.construct_from_google_books(response.json())
        """
        volume_info = api_data.get('volumeInfo', {})

        # Reseta o builder
        self.builder.reset()

        # Título (obrigatório)
        title = volume_info.get('title', '')
        if not title:
            raise ValueError("Google Books API retornou livro sem título")
        self.builder.set_title(title)

        # Autores (obrigatório, pode ser múltiplos)
        authors = volume_info.get('authors', [])
        if authors:
            # Junta múltiplos autores com vírgula
            self.builder.set_author(', '.join(authors))
        else:
            # Fallback se não houver autor
            self.builder.set_author('Autor Desconhecido')

        # ISBN (preferir ISBN-13)
        identifiers = volume_info.get('industryIdentifiers', [])
        for identifier in identifiers:
            if identifier.get('type') == 'ISBN_13':
                self.builder.set_isbn(identifier.get('identifier', ''))
                break
        else:
            # Se não encontrou ISBN-13, tenta ISBN-10
            for identifier in identifiers:
                if identifier.get('type') == 'ISBN_10':
                    self.builder.set_isbn(identifier.get('identifier', ''))
                    break

        # Editora
        publisher = volume_info.get('publisher')
        if publisher:
            self.builder.set_publisher(publisher)

        # Ano de publicação (pode vir como "2008-08-01", pegar só o ano)
        published_date = volume_info.get('publishedDate', '')
        if published_date:
            try:
                # Extrai os primeiros 4 caracteres (ano)
                year = int(published_date[:4])
                self.builder.set_publication_year(year)
            except (ValueError, IndexError):
                pass  # Ignora se não conseguir extrair o ano

        # Descrição
        description = volume_info.get('description')
        if description:
            self.builder.set_description(description)

        # Imagem da capa (preferir melhor qualidade)
        image_links = volume_info.get('imageLinks', {})
        cover_url = (
            image_links.get('extraLarge') or
            image_links.get('large') or
            image_links.get('medium') or
            image_links.get('thumbnail') or
            image_links.get('smallThumbnail')
        )
        if cover_url:
            self.builder.set_cover_url(cover_url)

        # Número de páginas
        page_count = volume_info.get('pageCount')
        if page_count and isinstance(page_count, int):
            self.builder.set_page_count(page_count)

        # Idioma
        language = volume_info.get('language')
        if language:
            self.builder.set_language(language)

        # Categorias (pegar primeira como gênero principal)
        categories = volume_info.get('categories', [])
        if categories:
            self.builder.set_genre(categories[0])
            for category in categories:
                self.builder.add_category(category)

        # Avaliação média
        average_rating = volume_info.get('averageRating')
        if average_rating:
            try:
                self.builder.set_average_rating(float(average_rating))
            except (ValueError, TypeError):
                pass  # Ignora se não conseguir converter

        # Marca a origem como Google Books
        self.builder.set_source('google_books')

        return self.builder.build()

    def construct_from_open_library(self, api_data: dict) -> Book:
        """
        Constrói um Book a partir da resposta da Open Library API.

        Estrutura esperada da API:
        {
          "title": "1984",
          "author_name": ["George Orwell"],
          "first_publish_year": 1949,
          "isbn": ["0451524934", "9780451524935"],
          "publisher": ["Signet Classic"],
          "subject": ["Fiction", "Dystopian"],
          "cover_i": 12345678,
          "language": ["eng"]
        }

        Args:
            api_data: Dicionário com resposta da Open Library API

        Returns:
            Book: Objeto Book criado e salvo

        Raises:
            ValueError: Se dados essenciais (título) estiverem faltando

        Example:
            >>> response = requests.get('https://openlibrary.org/search.json?q=1984')
            >>> book = director.construct_from_open_library(response.json()['docs'][0])
        """
        # Reseta o builder
        self.builder.reset()

        # Título (obrigatório)
        title = api_data.get('title', '')
        if not title:
            raise ValueError("Open Library API retornou livro sem título")
        self.builder.set_title(title)

        # Autores
        authors = api_data.get('author_name', [])
        if authors:
            self.builder.set_author(', '.join(authors))
        else:
            self.builder.set_author('Autor Desconhecido')

        # ISBN (preferir o mais longo, geralmente ISBN-13)
        isbns = api_data.get('isbn', [])
        if isbns:
            # Ordena por tamanho (desc) e pega o primeiro
            longest_isbn = max(isbns, key=len)
            self.builder.set_isbn(longest_isbn)

        # Editora (pegar primeira da lista)
        publishers = api_data.get('publisher', [])
        if publishers:
            self.builder.set_publisher(publishers[0])

        # Ano de publicação
        year = api_data.get('first_publish_year')
        if year and isinstance(year, int):
            self.builder.set_publication_year(year)

        # Categorias/Assuntos (pegar primeiro como gênero principal)
        subjects = api_data.get('subject', [])
        if subjects:
            self.builder.set_genre(subjects[0])
            # Limita a 5 categorias para não poluir
            for subject in subjects[:5]:
                self.builder.add_category(subject)

        # Imagem da capa
        cover_id = api_data.get('cover_i')
        if cover_id:
            # URL padrão da Open Library para capas
            cover_url = f"https://covers.openlibrary.org/b/id/{cover_id}-L.jpg"
            self.builder.set_cover_url(cover_url)

        # Idioma (pegar primeiro da lista)
        languages = api_data.get('language', [])
        if languages:
            # Converte código de 3 letras para formato padrão
            lang_code = languages[0]
            # Mapeamento simples (pode ser expandido)
            lang_map = {
                'eng': 'en',
                'por': 'pt-BR',
                'spa': 'es',
                'fre': 'fr',
                'ger': 'de'
            }
            self.builder.set_language(lang_map.get(lang_code, lang_code))

        # Marca a origem como Open Library
        self.builder.set_source('open_library')

        return self.builder.build()
