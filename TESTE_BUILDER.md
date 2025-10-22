# 🧪 Guia de Testes - Padrão Builder

Este guia explica como testar a implementação do padrão Builder usando Docker.

---

## 📋 Pré-requisitos

- Docker e Docker Compose instalados
- Estar no diretório `backend/`

---

## 🚀 Passo 1: Subir os Containers

```bash
cd backend
docker compose up --build -d
```

**O que isso faz:**
- `-d`: Roda em background
- `--build`: Reconstrói a imagem (importante após adicionar `requests` no requirements.txt)

**Verificar se subiu:**
```bash
docker compose ps
```

Deve mostrar 2 containers rodando:
- `backend-web-1` (Django)
- `backend-db-1` (PostgreSQL)

---

## 🗄️ Passo 2: Criar Migrations

```bash
docker compose exec web python manage.py makemigrations books
```

**Saída esperada:**
```
Migrations for 'books':
  books/migrations/000X_add_book_metadata.py
    - Add field genre to book
    - Add field isbn to book
    - Add field publisher to book
    - Add field publication_year to book
    - Add field description to book
    - Add field cover_url to book
    - Add field page_count to book
    - Add field language to book
    - Add field categories to book
    - Add field average_rating to book
    - Add field created_at to book
    - Add field updated_at to book
    - Add field source to book
    - Alter field author on book
```

---

## ⚙️ Passo 3: Aplicar Migrations

```bash
docker compose exec web python manage.py migrate
```

**Saída esperada:**
```
Operations to perform:
  Apply all migrations: admin, auth, books, contenttypes, library, profiles, reviews, sessions, users
Running migrations:
  Applying books.000X_add_book_metadata... OK
```

---

## 👤 Passo 4: Criar Superusuário

```bash
docker compose exec web python manage.py createsuperuser
```

**Preencher:**
- Username: `admin`
- Email: (deixar em branco ou preencher)
- Password: `admin123` (ou outra senha)

---

## 🧪 Passo 5: Testar no Django Shell

### Teste 1: BookBuilder Simples

```bash
docker compose exec web python manage.py shell
```

Dentro do shell Python:

```python
from books.builders import BookBuilder

# Criar livro simples
builder = BookBuilder()
book = (builder
    .set_title("1984")
    .set_author("George Orwell")
    .set_genre("Ficção")
    .set_publication_year(1949)
    .build())

print(book)
print(f"ID: {book.id}")
print(f"Source: {book.source}")
```

**Resultado esperado:**
```
1984 - George Orwell
ID: 1
Source: manual
```

---

### Teste 2: Validação de ISBN

```python
from books.builders import BookBuilder

builder = BookBuilder()

# ISBN válido (com hífens)
builder.set_isbn("978-0-13-235088-4")
print(builder.get_data()['isbn'])  # 9780132350884

# ISBN inválido
try:
    builder.set_isbn("123")
except ValueError as e:
    print(f"Erro: {e}")
```

**Resultado esperado:**
```
9780132350884
Erro: ISBN inválido. Deve ter 10 ou 13 dígitos. Recebido: 3
```

---

### Teste 3: BookDirector - Criação Manual

```python
from books.builders import BookDirector

director = BookDirector()
book = director.construct_simple_book(
    title="Clean Code",
    author="Robert C. Martin",
    genre="Técnico"
)

print(f"{book.title} por {book.author}")
print(f"Gênero: {book.genre}")
```

**Resultado esperado:**
```
Clean Code por Robert C. Martin
Gênero: Técnico
```

---

### Teste 4: Importação do Google Books (REQUER INTERNET)

```python
from books.builders import BookDirector
from books.external_apis import GoogleBooksAPI

# Buscar no Google Books
volume_id = "hjEFCAAAQBAJ"  # ID do livro "Clean Code"
api_data = GoogleBooksAPI.fetch_by_id(volume_id)

# Criar usando Director
director = BookDirector()
book = director.construct_from_google_books(api_data)

print(f"Título: {book.title}")
print(f"Autor: {book.author}")
print(f"ISBN: {book.isbn}")
print(f"Ano: {book.publication_year}")
print(f"Páginas: {book.page_count}")
print(f"Categorias: {book.categories}")
print(f"Source: {book.source}")
```

**Resultado esperado:**
```
Título: Clean Code
Autor: Robert C. Martin
ISBN: 9780132350884
Ano: 2008
Páginas: 464
Categorias: ['Computers']
Source: google_books
```

---

### Teste 5: Verificar Livros Criados

```python
from books.models import Book

# Listar todos os livros
books = Book.objects.all()
for book in books:
    print(f"{book.id}: {book.title} ({book.source})")

# Contar por fonte
print(f"\nManual: {Book.objects.filter(source='manual').count()}")
print(f"Google Books: {Book.objects.filter(source='google_books').count()}")
```

---

## 🌐 Passo 6: Testar via API (curl)

### 6.1: Obter Token JWT

```bash
curl -X POST http://localhost:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'
```

**Copiar o `access` token** da resposta.

---

### 6.2: Criar Livro Manual

```bash
TOKEN="SEU_TOKEN_AQUI"

curl -X POST http://localhost:8000/api/books/ \
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

**Resposta esperada:** HTTP 201 com dados do livro criado.

---

### 6.3: Importar do Google Books por ID

```bash
curl -X POST http://localhost:8000/api/books/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "google_books_id": "hjEFCAAAQBAJ"
  }'
```

**Resposta esperada:** HTTP 201 com dados completos do "Clean Code".

---

### 6.4: Importar por ISBN

```bash
curl -X POST http://localhost:8000/api/books/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "import_isbn": "9780132350884"
  }'
```

---

### 6.5: Buscar no Google Books (sem criar)

```bash
curl "http://localhost:8000/api/books/search-google-books/?q=clean+code"
```

**Resposta:** JSON com resultados da busca no Google Books.

---

### 6.6: Listar Livros

```bash
curl http://localhost:8000/api/books/
```

---

## 🖥️ Passo 7: Testar no Django Admin

1. Abrir navegador: http://localhost:8000/admin
2. Login: `admin` / `admin123`
3. Clicar em **Books**
4. Verificar livros criados com todos os campos
5. Testar filtros (Source, Genre, Language)
6. Testar busca (por título, autor, ISBN)

---

## 🧹 Passo 8: Limpar Testes

### Deletar todos os livros:

```bash
docker compose exec web python manage.py shell
```

```python
from books.models import Book
Book.objects.all().delete()
```

### Parar containers:

```bash
docker compose down
```

### Resetar banco completamente:

```bash
docker compose down -v  # Remove volumes (CUIDADO: perde dados!)
docker compose up -d
docker compose exec web python manage.py migrate
docker compose exec web python manage.py createsuperuser
```

---

## 🐛 Troubleshooting

### Erro: "No module named 'requests'"

```bash
# Rebuild com requirements atualizado
docker compose down
docker compose build --no-cache
docker compose up -d
```

### Erro: "relation 'books_book' does not exist"

```bash
# Rodar migrations
docker compose exec web python manage.py migrate
```

### Erro: "Invalid ISBN"

- Verificar se ISBN tem 10 ou 13 dígitos (sem hífens)
- Exemplo válido: `9780132350884`
- Exemplo inválido: `978-0-13-235088-4` (o Builder remove hífens automaticamente)

### Erro ao importar do Google Books: "Livro não encontrado"

- Verificar conexão com internet
- Volume ID pode estar incorreto
- Testar diretamente: https://www.googleapis.com/books/v1/volumes/hjEFCAAAQBAJ

---

## ✅ Checklist de Testes

- [ ] Container subiu sem erros
- [ ] Migrations aplicadas com sucesso
- [ ] BookBuilder cria livro simples
- [ ] Validações funcionam (ISBN, ano, rating)
- [ ] BookDirector cria livro manual
- [ ] Importação do Google Books funciona
- [ ] API cria livro manual (POST /api/books/)
- [ ] API importa do Google Books
- [ ] API importa por ISBN
- [ ] Busca no Google Books funciona
- [ ] Django Admin mostra todos os campos
- [ ] Filtros e busca funcionam no Admin

---

## 📊 Exemplos de Volume IDs (Google Books)

Para testar importação:

| Livro | Volume ID |
|-------|-----------|
| Clean Code | `hjEFCAAAQBAJ` |
| The Pragmatic Programmer | `5wBQEp6ruIAC` |
| Design Patterns (GoF) | `6oHuKQe3TjQC` |
| Refactoring | `1MsETFPD3I0C` |
| Code Complete | `QnghAQAAIAAJ` |

---

## 🎯 Próximos Passos

Após confirmar que tudo funciona:
1. Criar testes unitários automatizados
2. Escrever documentação UC-Builder.md
3. Criar diagrama UML
4. Atualizar coleção Postman

---

**Boa sorte nos testes! 🚀**
