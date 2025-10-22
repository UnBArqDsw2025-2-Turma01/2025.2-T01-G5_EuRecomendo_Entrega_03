# Testes Manuais - Padrão Adapter

Este documento contém instruções para testar manualmente a implementação do padrão Adapter para as APIs externas de livros.

## Pré-requisitos

- Docker e Docker Compose instalados
- Backend rodando em http://localhost:8001

## Iniciar o Ambiente

```bash
# No diretório backend
cd backend

# Iniciar containers
docker compose up -d

# Verificar se está rodando
docker compose ps

# Ver logs (opcional)
docker compose logs -f web
```

## 1. Testes Unitários

### Executar Todos os Testes

```bash
# Via Docker (no diretório backend)
docker compose exec web python manage.py test books

# Ou especificamente testes de adapter
docker compose exec web python manage.py test books.tests.GoogleBooksAdapterTestCase
docker compose exec web python manage.py test books.tests.OpenLibraryAdapterTestCase
docker compose exec web python manage.py test books.tests.AdapterFactoryTestCase
docker compose exec web python manage.py test books.tests.BookDirectorAdapterIntegrationTestCase
```

### Resultado Esperado

```
...........................................................
----------------------------------------------------------------------
Ran 59 tests in X.XXs

OK
```

## 2. Testes via API REST

### 2.1 Buscar Livro no Google Books (GET)

**Endpoint:** `GET /api/books/search-google-books/?q=clean+code`

```bash
curl -X GET "http://localhost:8001/api/books/search-google-books/?q=clean+code"
```

**Resposta Esperada:**
```json
{
  "count": 10,
  "api_source": "google_books",
  "results": [
    {
      "title": "Clean Code",
      "authors": ["Robert C. Martin"],
      "isbn": "9780132350884",
      "publisher": "Prentice Hall",
      "published_date": "2008-08-01",
      "description": "...",
      "cover_url": "https://...",
      "page_count": 464,
      "categories": ["Computers"],
      "language": "en",
      "average_rating": 4.5
    },
    ...
  ]
}
```

### 2.2 Buscar Livro no Open Library (GET)

**Endpoint:** `GET /api/books/search-open-library/?q=1984+orwell`

```bash
curl -X GET "http://localhost:8001/api/books/search-open-library/?q=1984+orwell"
```

**Resposta Esperada:**
```json
{
  "count": 10,
  "api_source": "open_library",
  "results": [
    {
      "title": "1984",
      "authors": ["George Orwell"],
      "isbn": "9780451524935",
      "publisher": "Signet Classic",
      "published_date": "1949",
      "description": null,
      "cover_url": "https://covers.openlibrary.org/b/id/...-L.jpg",
      "page_count": 328,
      "categories": ["Fiction", "Dystopian"],
      "language": "en",
      "average_rating": null
    },
    ...
  ]
}
```

### 2.3 Importar Livro do Google Books por ISBN (POST)

**Endpoint:** `POST /api/books/`

```bash
curl -X POST "http://localhost:8001/api/books/" \
  -H "Content-Type: application/json" \
  -d '{
    "import_isbn": "9780132350884"
  }'
```

**Resposta Esperada (201 Created):**
```json
{
  "id": 1,
  "title": "Clean Code",
  "author": "Robert C. Martin",
  "genre": "Computers",
  "isbn": "9780132350884",
  "publisher": "Prentice Hall",
  "publication_year": 2008,
  "description": "...",
  "cover_url": "https://...",
  "page_count": 464,
  "language": "en",
  "categories": ["Computers"],
  "average_rating": "4.50",
  "source": "google_books",
  "created_at": "2025-10-22T...",
  "updated_at": "2025-10-22T..."
}
```

### 2.4 Importar Livro do Google Books por Volume ID (POST)

**Endpoint:** `POST /api/books/import-google-books/`

```bash
curl -X POST "http://localhost:8001/api/books/import-google-books/" \
  -H "Content-Type: application/json" \
  -d '{
    "volume_id": "hjEFCAAAQBAJ"
  }'
```

**Resposta Esperada (201 Created):**
```json
{
  "id": 2,
  "title": "Clean Code: A Handbook of Agile Software Craftsmanship",
  "author": "Robert C. Martin",
  "source": "google_books",
  ...
}
```

### 2.5 Importar Livro do Open Library por ISBN (POST)

**Endpoint:** `POST /api/books/import-open-library/`

```bash
curl -X POST "http://localhost:8001/api/books/import-open-library/" \
  -H "Content-Type: application/json" \
  -d '{
    "isbn": "0451524934"
  }'
```

**Resposta Esperada (201 Created):**
```json
{
  "id": 3,
  "title": "1984",
  "author": "George Orwell",
  "genre": "Fiction",
  "isbn": "0451524934",
  "publisher": "Signet Classic",
  "publication_year": 1949,
  "source": "open_library",
  ...
}
```

## 3. Testes de Fallback

### 3.1 ISBN Existente Apenas no Open Library

Alguns ISBNs podem não estar no Google Books, mas estar no Open Library.

```bash
# Tentar importar (Google Books tentará primeiro, depois fallback para Open Library)
curl -X POST "http://localhost:8001/api/books/" \
  -H "Content-Type: application/json" \
  -d '{
    "import_isbn": "0451524934"
  }'
```

**Comportamento Esperado:**
- Google Books não encontra
- Sistema faz fallback para Open Library
- Livro é importado com `source: "open_library"`

## 4. Testes de Erro

### 4.1 ISBN Inválido

```bash
curl -X POST "http://localhost:8001/api/books/import-open-library/" \
  -H "Content-Type: application/json" \
  -d '{
    "isbn": "9999999999999"
  }'
```

**Resposta Esperada (404 Not Found):**
```json
{
  "error": "Livro não encontrado no Open Library com ISBN: 9999999999999"
}
```

### 4.2 Parâmetro Faltando

```bash
curl -X GET "http://localhost:8001/api/books/search-google-books/"
```

**Resposta Esperada (400 Bad Request):**
```json
{
  "error": "Parâmetro q (query) é obrigatório"
}
```

### 4.3 Volume ID Inválido

```bash
curl -X POST "http://localhost:8001/api/books/import-google-books/" \
  -H "Content-Type: application/json" \
  -d '{
    "volume_id": "invalid_id_12345"
  }'
```

**Resposta Esperada (404 Not Found):**
```json
{
  "error": "Livro não encontrado no Google Books: invalid_id_12345"
}
```

## 5. Testes de Integração

### 5.1 Criar e Listar Livros de Diferentes APIs

```bash
# 1. Importar do Google Books
curl -X POST "http://localhost:8001/api/books/" \
  -H "Content-Type: application/json" \
  -d '{"import_isbn": "9780132350884"}'

# 2. Importar do Open Library
curl -X POST "http://localhost:8001/api/books/import-open-library/" \
  -H "Content-Type: application/json" \
  -d '{"isbn": "0451524934"}'

# 3. Criar manualmente
curl -X POST "http://localhost:8001/api/books/" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Manual Book",
    "author": "Test Author",
    "genre": "Fiction"
  }'

# 4. Listar todos
curl -X GET "http://localhost:8001/api/books/"
```

**Resultado Esperado:**
```json
[
  {
    "id": 1,
    "title": "Clean Code",
    "source": "google_books",
    ...
  },
  {
    "id": 2,
    "title": "1984",
    "source": "open_library",
    ...
  },
  {
    "id": 3,
    "title": "Manual Book",
    "source": "manual",
    ...
  }
]
```

## 6. Testes Python Interativos

### 6.1 Testar Adapter Diretamente

```bash
# Entrar no shell do Django
docker compose exec web python manage.py shell
```

```python
# No shell Python
from books.adapters import GoogleBooksAdapter, OpenLibraryAdapter, create_adapter

# Testar Google Books
google = GoogleBooksAdapter()
result = google.search_by_isbn('9780132350884')
print(result['title'])  # 'Clean Code'
print(result['authors'])  # ['Robert C. Martin']

# Testar Open Library
openlib = OpenLibraryAdapter()
result = openlib.search_by_isbn('0451524934')
print(result['title'])  # '1984'
print(result['authors'])  # ['George Orwell']

# Testar Factory
adapter = create_adapter('google_books')
print(adapter.get_api_name())  # 'google_books'

# Testar busca por query
results = google.search_by_query('python programming', limit=5)
for book in results:
    print(f"{book['title']} - {', '.join(book['authors'])}")
```

### 6.2 Testar Integração com Director

```python
from books.adapters import GoogleBooksAdapter
from books.builders import BookDirector

# Buscar dados
adapter = GoogleBooksAdapter()
normalized = adapter.search_by_isbn('9780132350884')

# Criar livro
director = BookDirector()
book = director.construct_from_adapter(normalized, adapter.get_api_name())

# Verificar
print(f"Livro criado: {book.title}")
print(f"ID: {book.id}")
print(f"Source: {book.source}")
```

## 7. Checklist de Validação

### Funcionalidades do Adapter

- [ ] GoogleBooksAdapter busca por ISBN
- [ ] GoogleBooksAdapter busca por query
- [ ] GoogleBooksAdapter busca por volume ID
- [ ] GoogleBooksAdapter normaliza dados corretamente
- [ ] OpenLibraryAdapter busca por ISBN
- [ ] OpenLibraryAdapter busca por query
- [ ] OpenLibraryAdapter normaliza dados corretamente
- [ ] Factory cria adapters dinamicamente
- [ ] Adapters são intercambiáveis

### Endpoints da API

- [ ] GET /api/books/search-google-books/ funciona
- [ ] GET /api/books/search-open-library/ funciona
- [ ] POST /api/books/ com import_isbn funciona
- [ ] POST /api/books/import-google-books/ funciona
- [ ] POST /api/books/import-open-library/ funciona
- [ ] Fallback funciona quando Google Books não encontra

### Tratamento de Erros

- [ ] ISBN inválido retorna 404
- [ ] Parâmetros faltando retornam 400
- [ ] Errors são logados corretamente

### Qualidade de Dados

- [ ] ISBN-13 é preferido sobre ISBN-10
- [ ] Múltiplos autores são concatenados corretamente
- [ ] URLs de capa são válidas
- [ ] Categorias são armazenadas corretamente
- [ ] Campo `source` identifica API corretamente

## 8. Métricas de Sucesso

### Testes Unitários
- **Mínimo:** 90% de cobertura
- **Esperado:** 59 testes passando

### Performance
- **Busca por ISBN:** < 2 segundos
- **Busca por query:** < 3 segundos

### Confiabilidade
- **Fallback:** Funciona quando API primária falha
- **Tratamento de erros:** Não quebra o sistema

## 9. Troubleshooting

### Problema: "Module not found"

```bash
# Reinstalar dependências
docker compose exec web pip install -r requirements.txt
```

### Problema: API externa não responde

```bash
# Verificar conectividade
docker compose exec web python -c "import requests; print(requests.get('https://www.googleapis.com/books/v1/volumes?q=test').status_code)"
```

### Problema: Testes falhando

```bash
# Limpar banco de dados de teste
docker compose exec web python manage.py flush --no-input

# Rodar migrações
docker compose exec web python manage.py migrate

# Rodar testes novamente
docker compose exec web python manage.py test books
```

## 10. Limpeza

```bash
# Parar containers (no diretório backend)
docker compose down

# Remover volumes (cuidado: apaga banco de dados)
docker compose down -v
```

## Conclusão

Após executar todos os testes acima, você deve ter validado:

1. Interface `BookAPIInterface` funciona como contrato
2. Adapters convertem APIs específicas para formato padrão
3. Director usa adapters de forma uniforme
4. Endpoints REST funcionam com ambas APIs
5. Fallback automático funciona
6. Tratamento de erros é adequado
7. Qualidade de dados é mantida

**Status:** Implementação do Padrão Adapter completa e funcional!
