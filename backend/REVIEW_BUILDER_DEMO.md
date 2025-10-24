# Passo a Passo para Rodar e Testar o Review Builder

Este guia demonstra como rodar e testar o código do `review_builders.py` localmente.

## Pré-requisitos

- Docker e Docker Compose instalados
- Git (para clonar o repositório se necessário)

## Passo a Passo

### 1. Navegar para o diretório do backend

```bash
cd backend
```

### 2. Subir containers Docker

```bash
docker compose up --build -d
```

Verificar se os containers estão rodando:

```bash
docker compose ps
```

**Esperado:**
- `backend-web-1` (Django) rodando na porta 8000
- `backend-db-1` (PostgreSQL) rodando na porta 5432

### 3. Aplicar migrações

```bash
# Criar migrações para reviews (se necessário)
docker compose exec web python manage.py makemigrations reviews

# Aplicar todas as migrações
docker compose exec web python manage.py migrate
```

### 4. Criar superusuário

```bash
docker compose exec web python manage.py createsuperuser
```

**Exemplo:**
- Username: `admin`
- Password: `admin123`

### 5. Testar o Review Builder via script Python

```bash
# Executar o script de teste
docker compose exec web python test_review_builders.py
```

Este script irá:
- Testar o `ReviewBuilder` individualmente
- Testar o `ReviewDirector` 
- Criar diferentes tipos de reviews
- Validar regras de negócio
- Listar todas as reviews criadas

### 6. Testar via API REST

#### 6.1 Obter token JWT

```bash
curl -X POST http://localhost:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'
```

**Nota:** Se der erro 404, reinicie o container para aplicar as mudanças:
```bash
docker compose restart web
```

**Resposta esperada:**
```json
{
  "access": "<access_token>",
  "refresh": "<refresh_token>"
}
```

#### 6.2 Definir variável de ambiente com o token

```bash
TOKEN="<access_token_aqui>"
```

#### 6.3 Criar review via API

```bash
# Review básica
curl -X POST http://localhost:8000/api/reviews/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "book_title": "Clean Code",
    "rating": 5,
    "text": "Excelente livro sobre programação limpa!"
  }'
```

```bash
# Review com período de leitura
curl -X POST http://localhost:8000/api/reviews/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "book_title": "The Pragmatic Programmer",
    "rating": 4,
    "text": "Livro fundamental para desenvolvedores",
    "start_date": "2024-01-01",
    "end_date": "2024-01-15"
  }'
```

#### 6.4 Listar reviews criadas

```bash
curl http://localhost:8000/api/reviews/ \
  -H "Authorization: Bearer $TOKEN"
```

#### 6.5 Buscar review específica

```bash
curl http://localhost:8000/api/reviews/1/ \
  -H "Authorization: Bearer $TOKEN"
```

### 7. Verificar no Django Admin

1. Acessar: http://localhost:8000/admin
2. Login: `admin` / `admin123`
3. Navegar para **Reviews**
4. Verificar reviews criadas com todos os metadados

### 8. Testar validações

#### 8.1 Rating inválido (deve falhar)

```bash
curl -X POST http://localhost:8000/api/reviews/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "book_title": "Test Book",
    "rating": 6
  }'
```

#### 8.2 Dados obrigatórios faltando (deve falhar)

```bash
curl -X POST http://localhost:8000/api/reviews/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "book_title": "Test Book"
  }'
```

## Demonstração do Padrão Builder

### Uso do ReviewBuilder

```python
from reviews.review_builders import ReviewBuilder
from datetime import date

# Criar review básica
review = (ReviewBuilder()
          .set_book_title("Clean Code")
          .set_rating(5)
          .build())

# Criar review detalhada
review = (ReviewBuilder()
          .set_book_title("Design Patterns")
          .set_rating(4)
          .set_comment("Padrões essenciais")
          .set_reading_period(date(2024, 1, 1), date(2024, 1, 15))
          .build())
```

### Uso do ReviewDirector

```python
from reviews.review_builders import ReviewBuilder, ReviewDirector
from datetime import date

builder = ReviewBuilder()
director = ReviewDirector(builder)

# Review rápida
review = director.build_quick_review("Python Cookbook", 4)

# Review detalhada
review = director.build_detailed_review(
    book_title="Effective Python",
    rating=5,
    comment="Livro fundamental",
    start_date=date(2024, 1, 10),
    end_date=date(2024, 1, 25)
)

# Review em progresso
review = director.build_reading_in_progress(
    book_title="Fluent Python",
    rating=4,
    comment="Lendo aos poucos...",
    start_date=date(2024, 2, 1)
)
```

## Limpeza

Para limpar os dados de teste:

```bash
# Parar containers
docker compose down

# Remover volumes (CUIDADO: remove todos os dados)
docker compose down -v
```

## Troubleshooting

### Container não sobe
```bash
# Ver logs
docker compose logs web
docker compose logs db

# Rebuild completo
docker compose down
docker compose up --build -d
```

### Erro de migração
```bash
# Resetar migrações (CUIDADO: remove dados)
docker compose exec web python manage.py migrate reviews zero
docker compose exec web python manage.py migrate reviews
```

### Erro de permissão
```bash
# Verificar permissões
docker compose exec web ls -la
```

## Funcionalidades Demonstradas

1. **Padrão Builder**: Construção flexível de objetos Review
2. **Padrão Director**: Métodos pré-definidos para casos comuns
3. **Validações**: Rating entre 1-5, dados obrigatórios
4. **API REST**: Endpoints para CRUD de reviews
5. **Django Admin**: Interface administrativa
6. **Testes automatizados**: Script de demonstração completo

