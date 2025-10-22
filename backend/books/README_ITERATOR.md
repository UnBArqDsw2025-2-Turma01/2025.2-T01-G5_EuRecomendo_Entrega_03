# Padrão Iterator - Guia Rápido

## Visão Geral

O padrão **Iterator** permite navegar sequencialmente por resultados de APIs de livros sem expor detalhes de implementação. Integra perfeitamente com os padrões **Adapter** e **Builder**.

## Uso Rápido

### 1. Iterador Simples (Carrega Tudo)

```python
from books.adapters import GoogleBooksAdapter
from books.iterators import UnifiedAPIIterator

adapter = GoogleBooksAdapter()
results = adapter.search_by_query("clean code", limit=10)
iterator = UnifiedAPIIterator(results, api_name='google_books')

for book_data in iterator:
    print(f"{book_data['title']} - {book_data['authors']}")
```

### 2. Iterador Lazy (Carrega Sob Demanda)

```python
from books.adapters import GoogleBooksAdapter
from books.iterators import LazyAPIIterator

adapter = GoogleBooksAdapter()
iterator = LazyAPIIterator(adapter, query="python", page_size=10, max_pages=5)

# Processa apenas 5 resultados (economiza requisições)
for i, book in enumerate(iterator):
    if i >= 5:
        break
    print(book['title'])
```

### 3. Iterador Multi-Fonte (Combina APIs)

```python
from books.adapters import GoogleBooksAdapter, OpenLibraryAdapter
from books.iterators import MultiSourceIterator

google = GoogleBooksAdapter()
open_lib = OpenLibraryAdapter()

iterator = MultiSourceIterator(
    adapters=[google, open_lib],
    query="1984",
    deduplicate_by_isbn=True
)

for book in iterator:
    print(f"{book['title']} (fonte: {book['_api_source']})")
```

### 4. Uso com Collection (Recomendado)

```python
from books.adapters import GoogleBooksAdapter, OpenLibraryAdapter
from books.iterators import BookAPICollection

# Setup
collection = BookAPICollection()
collection.add_api(GoogleBooksAdapter())
collection.add_api(OpenLibraryAdapter())

# Cria iteradores facilmente
unified = collection.create_iterator("django", api_index=0, limit=20)
lazy = collection.create_lazy_iterator("flask", api_index=0, page_size=5)
multi = collection.create_multi_source_iterator("fastapi", limit_per_api=15)
```

### 5. Integração com Builder (Importa para Banco)

```python
from books.adapters import GoogleBooksAdapter
from books.iterators import BookAPICollection, IteratorBookBuilder

collection = BookAPICollection()
collection.add_api(GoogleBooksAdapter())

iterator = collection.create_iterator("clean code", limit=20)
builder = IteratorBookBuilder(iterator)

# Importa todos os livros
books = builder.build_all(skip_existing=True)
print(f"Importados {len(books)} livros")
```

## Tipos de Iteradores

| Iterador | Quando Usar | Vantagens |
|----------|-------------|-----------|
| `UnifiedAPIIterator` | Conjuntos pequenos (<50 itens) | Acesso rápido, operações peek/skip |
| `LazyAPIIterator` | Exploração/busca específica | Economia de memória e requisições |
| `MultiSourceIterator` | Máxima cobertura de resultados | Agrega APIs, deduplica automaticamente |

## Métodos Úteis

### Todos os Iteradores

```python
iterator.has_next()          # Verifica se há próximo elemento
iterator.current_position()  # Retorna posição atual (0-based)
iterator.reset()            # Reinicia para posição inicial
next(iterator)              # Retorna próximo elemento
```

### UnifiedAPIIterator

```python
iterator.total_count()      # Total de elementos
iterator.peek()             # Próximo elemento sem avançar
iterator.skip(n)           # Pula n elementos
iterator.get_api_name()    # Nome da API fonte
```

### MultiSourceIterator

```python
iterator.total_count()      # Total de elementos agregados
iterator.group_by_source()  # Agrupa resultados por API
```

## Exemplos Práticos

### Buscar Livro Específico (Lazy)

```python
def find_book(query: str, title_contains: str):
    adapter = GoogleBooksAdapter()
    iterator = LazyAPIIterator(adapter, query, page_size=10, max_pages=10)

    for book in iterator:
        if title_contains.lower() in book['title'].lower():
            return book
    return None

book = find_book("software engineering", "Clean Code")
```

### Importar de Múltiplas APIs

```python
def import_from_all_sources(query: str):
    adapters = [GoogleBooksAdapter(), OpenLibraryAdapter()]
    iterator = MultiSourceIterator(adapters, query, limit_per_api=20, deduplicate_by_isbn=True)

    builder = IteratorBookBuilder(iterator)
    books = builder.build_all(skip_existing=True)

    return books

books = import_from_all_sources("django")
```

### Processamento em Lote

```python
def import_in_batches(query: str, batch_size: int = 10):
    collection = BookAPICollection()
    collection.add_api(GoogleBooksAdapter())

    iterator = collection.create_lazy_iterator(query, page_size=batch_size)
    builder = IteratorBookBuilder(iterator)

    total = 0
    while iterator.has_next():
        batch = builder.build_batch(count=batch_size, skip_existing=True)
        total += len(batch)
        print(f"Lote: {len(batch)} livros")

    return total
```

## Testes

```bash
# Executar todos os testes do iterator
docker-compose exec backend python manage.py test books.test_iterators -v 2

# Testes específicos
python manage.py test books.test_iterators.UnifiedAPIIteratorTest
python manage.py test books.test_iterators.LazyAPIIteratorTest
python manage.py test books.test_iterators.MultiSourceIteratorTest
python manage.py test books.test_iterators.IntegrationTest
```

## Arquitetura

```
BookAPICollection (Aggregate)
    ├── cria → UnifiedAPIIterator
    ├── cria → LazyAPIIterator
    └── cria → MultiSourceIterator
                    │
                    │ usa
                    ▼
            BookAPIInterface (Adapter)
                    │
                    │ integra
                    ▼
            IteratorBookBuilder
                    │
                    │ usa
                    ▼
            BookDirector (Builder)
                    │
                    ▼
                  Book
```

## Arquivos

- **Implementação**: `backend/books/iterators.py` (~620 linhas)
- **Testes**: `backend/books/test_iterators.py` (~525 linhas)
- **Documentação Completa**: `docs/Projeto/UC-Iterator.md`
- **Documentação Técnica**: `TESTE_ITERATOR.md` (raiz do projeto)

## Links Úteis

- [Documentação Completa](../../docs/Projeto/UC-Iterator.md)
- [Testes Detalhados](./test_iterators.py)
- [Padrão Adapter](../../docs/Projeto/UC-Adapter.md)
- [Padrão Builder](../../docs/Projeto/UC-Builder.md)

## Integração de 3 Padrões GoF

```python
# ADAPTER: Normaliza dados de APIs diferentes
adapter = GoogleBooksAdapter()

# ITERATOR: Navega pelos resultados
iterator = LazyAPIIterator(adapter, query="python", page_size=10)

# BUILDER: Constrói objetos Book
builder_helper = IteratorBookBuilder(iterator)
books = builder_helper.build_all()

# 3 padrões trabalhando juntos! 🎯
```

## Benefícios

✅ Lazy loading (economia de memória e requisições)
✅ Agregação de múltiplas APIs
✅ Deduplicação automática por ISBN
✅ Separação de responsabilidades
✅ Extensível (fácil adicionar novos iteradores)
✅ Testável (30+ testes)
✅ Integração perfeita com Adapter e Builder
