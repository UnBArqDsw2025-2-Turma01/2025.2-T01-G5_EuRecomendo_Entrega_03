# 3.1.2 Builder — BookBuilder e BookDirector

## Introdução
O Builder é um padrão criacional que separa a construção de um objeto complexo de sua representação, permitindo criar diferentes representações usando o mesmo processo de construção. Na aplicação "EuRecomendo", aplicamos este padrão para criar objetos `Book` a partir de múltiplas fontes de dados: entrada manual, Google Books API e Open Library API. O padrão é implementado através das classes `BookBuilder` (construtor com validações) e `BookDirector` (receitas de construção).

## Objetivo
- Desacoplar a criação de objetos `Book` complexos da lógica de negócio da API.
- Fornecer interface fluente (method chaining) para construção incremental.
- Validar dados progressivamente durante a construção.
- Encapsular diferentes "receitas" de construção via Director (manual, Google Books, Open Library).
- Garantir consistência dos dados independentemente da fonte.

## Vantagens
- **Separação de responsabilidades**: A lógica de construção fica isolada do modelo Django.
- **Validação incremental**: Cada setter valida os dados antes de armazená-los.
- **Interface fluente**: Melhora a legibilidade do código através de method chaining.
- **Reutilização**: Director encapsula receitas complexas, evitando duplicação.
- **Flexibilidade**: Novos campos ou fontes de dados podem ser adicionados sem quebrar código existente.

## Desvantagens
- **Complexidade adicional**: Introduz mais classes (Builder + Director) para problemas simples.
- **Overhead de memória**: Mantém estado intermediário antes de criar o objeto final.
- **Curva de aprendizado**: Desenvolvedores precisam entender o padrão antes de usar.

## Metodologia
- **Ferramentas**: VS Code, Django/DRF (implementação), PostgreSQL (persistência), Docker (execução), Postman (testes de API), pytest/Django TestCase (testes unitários).
- **APIs externas**: Google Books API (https://www.googleapis.com/books/v1/volumes), Open Library API (https://openlibrary.org/api).
- **Referências**: GoF Design Patterns, Django Best Practices, REST API Design.

## Desenvolvimento

### Modelo Book Expandido
O modelo `Book` foi expandido para suportar metadados ricos:

```python
class Book(models.Model):
    # Campos básicos
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    genre = models.CharField(max_length=100, blank=True)

    # Metadados do livro
    isbn = models.CharField(max_length=13, blank=True, null=True, unique=True)
    publisher = models.CharField(max_length=255, blank=True)
    publication_year = models.IntegerField(blank=True, null=True)
    description = models.TextField(blank=True)
    cover_url = models.URLField(max_length=500, blank=True, null=True)
    page_count = models.IntegerField(blank=True, null=True)
    language = models.CharField(max_length=10, default='pt-BR')

    # Campos JSON para dados flexíveis
    categories = models.JSONField(default=list, blank=True)
    average_rating = models.DecimalField(max_digits=3, decimal_places=2,
                                        blank=True, null=True)

    # Metadados de controle
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    source = models.CharField(max_length=50, default='manual')
```

### BookBuilder (backend/books/builders.py)
Implementa a interface fluente com validações:

```python
class BookBuilder:
    def __init__(self):
        self.reset()

    def reset(self):
        """Limpa os dados para nova construção."""
        self._book_data = {
            'categories': [],
            'language': 'pt-BR',
            'source': 'manual'
        }
        return self

    def set_title(self, title: str):
        """Define o título com validação de tamanho."""
        if not title or not title.strip():
            raise ValueError("Título não pode ser vazio")
        title = title.strip()
        if len(title) > 255:
            raise ValueError(f"Título muito longo (máx. 255 caracteres). "
                           f"Recebido: {len(title)}")
        self._book_data['title'] = title
        return self

    def set_isbn(self, isbn: str):
        """Valida e limpa ISBN (10 ou 13 dígitos)."""
        if not isbn:
            return self
        cleaned_isbn = ''.join(c for c in isbn if c.isdigit())
        if len(cleaned_isbn) not in [10, 13]:
            raise ValueError(f"ISBN inválido. Deve ter 10 ou 13 dígitos. "
                           f"Recebido: {len(cleaned_isbn)}")
        self._book_data['isbn'] = cleaned_isbn
        return self

    def set_publication_year(self, year: int):
        """Valida ano de publicação."""
        if year is None:
            return self
        if not isinstance(year, int):
            raise ValueError(f"Ano deve ser um inteiro. "
                           f"Recebido: {type(year).__name__}")
        if year < 1000 or year > 2030:
            raise ValueError(f"Ano de publicação inválido: {year}. "
                           f"Deve estar entre 1000 e 2030")
        self._book_data['publication_year'] = year
        return self

    def build(self) -> Book:
        """Cria e persiste o objeto Book."""
        if 'title' not in self._book_data or not self._book_data['title']:
            raise ValueError("Título é obrigatório para criar um livro")
        if 'author' not in self._book_data or not self._book_data['author']:
            raise ValueError("Autor é obrigatório para criar um livro")

        book = Book(**self._book_data)
        book.save()
        self.reset()  # Limpa para próxima construção
        return book
```

### BookDirector (backend/books/builders.py)
Encapsula receitas de construção para diferentes fontes:

```python
class BookDirector:
    def __init__(self):
        self.builder = BookBuilder()

    def construct_simple_book(self, title: str, author: str,
                             genre: str = "") -> Book:
        """Cria livro com dados mínimos (entrada manual)."""
        return (self.builder
            .reset()
            .set_title(title)
            .set_author(author)
            .set_genre(genre)
            .set_source('manual')
            .build())

    def construct_from_google_books(self, api_data: dict) -> Book:
        """Constrói livro a partir de dados do Google Books."""
        volume_info = api_data.get('volumeInfo', {})
        self.builder.reset()

        # Título (obrigatório)
        title = volume_info.get('title', '')
        if not title:
            raise ValueError("Google Books API retornou livro sem título")
        self.builder.set_title(title)

        # Autores
        authors = volume_info.get('authors', [])
        if authors:
            self.builder.set_author(', '.join(authors))
        else:
            self.builder.set_author('Autor Desconhecido')

        # ISBN (preferir ISBN-13)
        identifiers = volume_info.get('industryIdentifiers', [])
        for identifier in identifiers:
            if identifier.get('type') == 'ISBN_13':
                self.builder.set_isbn(identifier.get('identifier', ''))
                break
        else:
            # Fallback para ISBN-10
            for identifier in identifiers:
                if identifier.get('type') == 'ISBN_10':
                    self.builder.set_isbn(identifier.get('identifier', ''))
                    break

        # Ano (extrair de "2008-08-01" -> 2008)
        published_date = volume_info.get('publishedDate', '')
        if published_date:
            try:
                year = int(published_date[:4])
                self.builder.set_publication_year(year)
            except (ValueError, IndexError):
                pass

        # Outros metadados
        self.builder.set_publisher(volume_info.get('publisher', ''))
        self.builder.set_description(volume_info.get('description', ''))
        self.builder.set_page_count(volume_info.get('pageCount'))
        self.builder.set_language(volume_info.get('language', 'pt-BR'))
        self.builder.set_average_rating(volume_info.get('averageRating'))

        # Capa
        image_links = volume_info.get('imageLinks', {})
        cover_url = image_links.get('thumbnail', '')
        if cover_url:
            self.builder.set_cover_url(cover_url)

        # Categorias e gênero
        categories = volume_info.get('categories', [])
        if categories:
            self.builder.set_genre(categories[0])
            self.builder.set_categories(categories)

        self.builder.set_source('google_books')
        return self.builder.build()
```

### Integração com API (backend/books/views.py)
O `BookViewSet` usa o Builder para suportar três modos de criação:

```python
class BookViewSet(viewsets.ModelViewSet):
    def create(self, request, *args, **kwargs):
        serializer = BookCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        try:
            if data.get('google_books_id'):
                book = self._create_from_google_books_id(
                    data['google_books_id']
                )
            elif data.get('import_isbn'):
                book = self._create_from_isbn(data['import_isbn'])
            else:
                book = self._create_manual(data)

            output_serializer = BookSerializer(book)
            return Response(output_serializer.data,
                          status=status.HTTP_201_CREATED)
        except ValueError as e:
            return Response({'error': str(e)},
                          status=status.HTTP_400_BAD_REQUEST)

    def _create_manual(self, data: dict) -> Book:
        """Criação manual usando Builder."""
        builder = BookBuilder()
        if 'title' in data and data['title']:
            builder.set_title(data['title'])
        if 'author' in data and data['author']:
            builder.set_author(data['author'])
        # ... outros campos
        builder.set_source('manual')
        return builder.build()

    def _create_from_google_books_id(self, volume_id: str) -> Book:
        """Importação via Google Books ID."""
        api_data = GoogleBooksAPI.fetch_by_id(volume_id)
        if not api_data:
            raise ValueError(f"Livro não encontrado: {volume_id}")

        director = BookDirector()
        return director.construct_from_google_books(api_data)
```

## Diagrama
![Diagrama](../assets/diagramaBuilderBooks.png)

## Demonstração (resultado)

### 1. Criação Manual
```bash
POST /api/books/
{
  "title": "Clean Code",
  "author": "Robert C. Martin",
  "genre": "Técnico",
  "isbn": "9780132350884",
  "publication_year": 2008,
  "page_count": 464
}
```

Resposta: **201 CREATED**
```json
{
  "id": 1,
  "title": "Clean Code",
  "author": "Robert C. Martin",
  "genre": "Técnico",
  "isbn": "9780132350884",
  "publication_year": 2008,
  "page_count": 464,
  "source": "manual",
  "created_at": "2025-10-21T10:30:00Z"
}
```

### 2. Importação por Google Books ID
```bash
POST /api/books/
{
  "google_books_id": "hjEFCAAAQBAJ"
}
```

Resposta: **201 CREATED** com todos os metadados da API (título, autor, ISBN, ano, descrição, capa, categorias, rating, etc.)

### 3. Importação por ISBN
```bash
POST /api/books/
{
  "import_isbn": "9780132350884"
}
```

Resposta: **201 CREATED** com dados do Google Books (busca automática pelo ISBN)

### 4. Validação de Erro
```bash
POST /api/books/
{
  "title": "",
  "author": "Test"
}
```

Resposta: **400 BAD REQUEST**
```json
{
  "error": "Título não pode ser vazio"
}
```

## Passo a passo para rodar

### 1. Subir containers Docker
```bash
cd backend
docker compose up --build -d
```

Verificar containers:
```bash
docker compose ps
```

Esperado: `backend-web-1` (Django) e `backend-db-1` (PostgreSQL) rodando.

### 2. Aplicar migrações
```bash
docker compose exec web python manage.py makemigrations books
docker compose exec web python manage.py migrate
```

### 3. Criar superusuário
```bash
docker compose exec web python manage.py createsuperuser
```

Exemplo:
- Username: `admin`
- Password: `admin123`

### 4. Obter token JWT
```bash
curl -X POST http://localhost:8001/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'
```

Resposta:
```json
{
  "access": "<access_token>",
  "refresh": "<refresh_token>"
}
```

### 5. Testar criação manual
```bash
TOKEN="<access_token>"

curl -X POST http://localhost:8001/api/books/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "title": "The Pragmatic Programmer",
    "author": "Andrew Hunt, David Thomas",
    "genre": "Técnico",
    "isbn": "9780135957059",
    "publication_year": 2019,
    "page_count": 352
  }'
```

### 6. Testar importação do Google Books
```bash
curl -X POST http://localhost:8001/api/books/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"google_books_id": "hjEFCAAAQBAJ"}'
```

### 7. Testar importação por ISBN
```bash
curl -X POST http://localhost:8001/api/books/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"import_isbn": "9780132350884"}'
```

### 8. Buscar no Google Books (sem criar)
```bash
curl "http://localhost:8001/api/books/search-google-books/?q=clean+code"
```

### 9. Listar livros criados
```bash
curl http://localhost:8001/api/books/
```

### 10. Verificar no Django Admin
1. Acessar: http://localhost:8001/admin
2. Login: `admin` / `admin123`
3. Navegar para **Books**
4. Verificar livros com todos os metadados
5. Testar filtros (Source, Genre, Language)

## Testes Unitários
O projeto inclui 38 testes automatizados cobrindo:

- **BookBuilder**: validações de título, autor, ISBN, ano, rating, URL, categorias
- **BookDirector**: receitas para criação manual, Google Books e Open Library
- **GoogleBooksAPI**: mocks de requisições HTTP e tratamento de erros

Executar testes:
```bash
docker compose exec web python manage.py test books
```

Resultado esperado:
```
Ran 38 tests in 0.102s

OK
```

## Vídeo (demonstração)
- Espaço reservado para link de vídeo (YouTube) demonstrando o fluxo completo.

## Bibliografia
- Gamma, E. et al. **Design Patterns: Elements of Reusable Object-Oriented Software**. Addison-Wesley, 1995.
- Google Books API Documentation: https://developers.google.com/books/docs/v1/using
- Open Library API Documentation: https://openlibrary.org/developers/api
- Django Best Practices: https://docs.djangoproject.com/en/stable/

## Histórico de Versões
| Versão | Data       | Descrição                                   | Autor(es)          | Revisor(es) |
|--------|------------|---------------------------------------------|--------------------|-------------|
| 1.0    | 21/10/2025 | Criação do documento, implementação completa do Builder com testes | Luis Bruno | A revisar |
