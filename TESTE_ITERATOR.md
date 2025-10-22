# Padrão Iterator - Documentação e Testes

## Índice
1. [Visão Geral](#visão-geral)
2. [Componentes do Padrão](#componentes-do-padrão)
3. [Arquitetura](#arquitetura)
4. [Casos de Uso](#casos-de-uso)
5. [Exemplos Práticos](#exemplos-práticos)
6. [Testes](#testes)
7. [Integração com Outros Padrões](#integração-com-outros-padrões)

---

## Visão Geral

O **padrão Iterator** (GoF Comportamental) foi implementado para fornecer uma maneira uniforme de navegar por resultados de múltiplas APIs de livros sem expor detalhes de implementação. Esta implementação complementa perfeitamente os padrões **Adapter** e **Builder** já existentes no projeto.

### Problema Resolvido

Ao buscar livros em múltiplas APIs externas (Google Books, Open Library), surgem diversos desafios:

1. **Diferentes estruturas de resposta**: Cada API retorna dados em formatos diferentes
2. **Paginação complexa**: Algumas APIs usam offset, outras cursores
3. **Uso de memória**: Carregar todos os resultados de uma vez é ineficiente
4. **Agregação de fontes**: Combinar resultados de múltiplas APIs é trabalhoso
5. **Duplicação**: Mesmo livro pode aparecer em diferentes APIs

### Solução

O padrão Iterator fornece:

- **Iteração uniforme** sobre diferentes fontes de dados
- **Lazy loading** para economizar memória e requisições
- **Agregação transparente** de múltiplas APIs
- **Deduplicação automática** por ISBN
- **Integração com Builder** para criação automática de objetos Book

---

## Componentes do Padrão

### 1. Iterator Interface (`BookIterator`)

Define o contrato que todos os iteradores devem seguir:

```python
class BookIterator(ABC):
    @abstractmethod
    def __iter__(self):
        """Retorna o próprio iterador"""

    @abstractmethod
    def __next__(self) -> Dict:
        """Retorna o próximo item normalizado"""

    @abstractmethod
    def has_next(self) -> bool:
        """Verifica se há mais elementos"""

    @abstractmethod
    def reset(self):
        """Reinicia o iterador"""

    @abstractmethod
    def current_position(self) -> int:
        """Retorna a posição atual"""
```

**Arquivo**: `backend/books/iterators.py:33-82`

---

### 2. Concrete Iterators

#### 2.1 UnifiedAPIIterator

Itera sobre resultados já carregados de uma única API.

**Características**:
- Carrega todos os resultados de uma vez
- Navegação controlada (next, peek, skip)
- Reset para reutilização
- Ideal para conjuntos pequenos de resultados

**Exemplo**:
```python
from books.adapters import GoogleBooksAdapter
from books.iterators import UnifiedAPIIterator

# Busca no Google Books
adapter = GoogleBooksAdapter()
results = adapter.search_by_query("clean code", limit=10)

# Cria iterador
iterator = UnifiedAPIIterator(results, api_name='google_books')

# Itera sobre resultados
for book_data in iterator:
    print(f"{book_data['title']} - {book_data['authors']}")

# Informações úteis
print(f"Total: {iterator.total_count()}")
print(f"Posição atual: {iterator.current_position()}")
print(f"API: {iterator.get_api_name()}")

# Peek sem avançar
next_book = iterator.peek()

# Pular elementos
iterator.skip(5)
```

**Arquivo**: `backend/books/iterators.py:85-175`

---

#### 2.2 LazyAPIIterator

Itera sobre resultados carregando páginas sob demanda.

**Características**:
- Lazy loading (carrega apenas quando necessário)
- Economia de memória e requisições
- Paginação automática
- Ideal para exploração de resultados

**Exemplo**:
```python
from books.adapters import GoogleBooksAdapter
from books.iterators import LazyAPIIterator

adapter = GoogleBooksAdapter()

# Cria iterador lazy (carrega 10 por página, máximo 5 páginas)
iterator = LazyAPIIterator(
    adapter,
    query="python programming",
    page_size=10,
    max_pages=5
)

# Processa apenas os 5 primeiros (economiza requisições!)
for i, book_data in enumerate(iterator):
    if i >= 5:
        break
    print(book_data['title'])
```

**Arquivo**: `backend/books/iterators.py:178-284`

---

#### 2.3 MultiSourceIterator

Combina resultados de múltiplas APIs em uma única iteração.

**Características**:
- Agrega resultados de várias APIs
- Deduplicação automática por ISBN
- Resiliência a falhas de API
- Metadados de origem em cada resultado

**Exemplo**:
```python
from books.adapters import GoogleBooksAdapter, OpenLibraryAdapter
from books.iterators import MultiSourceIterator

# Cria adapters
google = GoogleBooksAdapter()
open_lib = OpenLibraryAdapter()

# Iterador multi-fonte com deduplicação
iterator = MultiSourceIterator(
    adapters=[google, open_lib],
    query="1984 orwell",
    limit_per_api=10,
    deduplicate_by_isbn=True
)

# Itera sobre resultados agregados
for book_data in iterator:
    print(f"{book_data['title']} (fonte: {book_data['_api_source']})")

# Agrupa por fonte
grouped = iterator.group_by_source()
print(f"Google Books: {len(grouped['google_books'])} resultados")
print(f"Open Library: {len(grouped['open_library'])} resultados")
```

**Arquivo**: `backend/books/iterators.py:287-407`

---

### 3. Aggregate (`BookAPICollection`)

Gerencia coleção de APIs e fornece factory methods para criar iteradores.

**Características**:
- Factory para criação de iteradores
- Gerenciamento de múltiplas APIs
- Interface fluente (method chaining)

**Exemplo**:
```python
from books.adapters import GoogleBooksAdapter, OpenLibraryAdapter
from books.iterators import BookAPICollection

# Cria coleção e adiciona APIs
collection = BookAPICollection()
collection.add_api(GoogleBooksAdapter())
collection.add_api(OpenLibraryAdapter())

# Cria diferentes tipos de iteradores
unified = collection.create_iterator("django", api_index=0, limit=20)
lazy = collection.create_lazy_iterator("flask", api_index=1, page_size=5)
multi = collection.create_multi_source_iterator("fastapi", limit_per_api=15)
```

**Arquivo**: `backend/books/iterators.py:410-507`

---

### 4. Integration Helper (`IteratorBookBuilder`)

Integra Iterator com Builder para criar objetos Book automaticamente.

**Características**:
- Converte resultados de API em objetos Book
- Skip de livros já existentes (por ISBN)
- Processamento em lote
- Integra 3 padrões GoF (Iterator + Adapter + Builder)

**Exemplo**:
```python
from books.adapters import GoogleBooksAdapter
from books.iterators import BookAPICollection, IteratorBookBuilder

# Setup
collection = BookAPICollection()
collection.add_api(GoogleBooksAdapter())

# Cria iterador
iterator = collection.create_iterator("clean code", limit=20)

# Helper que integra com Builder
builder_helper = IteratorBookBuilder(iterator)

# Opção 1: Cria todos os livros
books = builder_helper.build_all(skip_existing=True)
print(f"Criados {len(books)} livros no banco de dados")

# Opção 2: Cria um por vez
book = builder_helper.build_next()
if book:
    print(f"Criado: {book.title}")

# Opção 3: Cria em lote
batch = builder_helper.build_batch(count=5, skip_existing=True)
print(f"Criados {len(batch)} livros em lote")
```

**Arquivo**: `backend/books/iterators.py:510-623`

---

## Arquitetura

### Diagrama de Classes

```
┌─────────────────────┐
│   BookIterator      │◄──────────────┐
│    (Interface)      │               │
├─────────────────────┤               │
│ + __iter__()        │               │
│ + __next__()        │               │
│ + has_next()        │               │ implements
│ + reset()           │               │
│ + current_position()│               │
└─────────────────────┘               │
         △                            │
         │                            │
         │ implements                 │
         │                            │
    ┌────┴──────┬──────────────┬──────┴──────────┐
    │           │              │                 │
┌───┴──────┐ ┌──┴────────┐ ┌──┴──────────┐ ┌───┴──────────┐
│ Unified  │ │   Lazy    │ │ MultiSource │ │   (outros)   │
│   API    │ │   API     │ │  Iterator   │ │              │
│ Iterator │ │ Iterator  │ │             │ │              │
└──────────┘ └───────────┘ └─────────────┘ └──────────────┘
     │              │              │
     │              │              │
     │              │              └──────┐
     │              │                     │
     └──────────────┴─────────────────────┤
                                          │
                                          │ uses
                                          │
                                   ┌──────▼──────────┐
                                   │ BookAPIAdapter  │
                                   │  (Interface)    │
                                   └─────────────────┘
                                          △
                                          │
                              ┌───────────┴──────────┐
                              │                      │
                        ┌─────▼──────┐      ┌───────▼────────┐
                        │  Google    │      │  OpenLibrary   │
                        │   Books    │      │    Adapter     │
                        │  Adapter   │      │                │
                        └────────────┘      └────────────────┘


┌──────────────────────┐
│ BookAPICollection    │
│    (Aggregate)       │
├──────────────────────┤        creates
│ - _apis: List        ├─────────────────────► BookIterator
│ + add_api()          │
│ + create_iterator()  │
│ + create_lazy_...()  │
│ + create_multi_...() │
└──────────────────────┘


┌──────────────────────┐         uses          ┌──────────────┐
│ IteratorBookBuilder  ├───────────────────────►│ BookIterator │
├──────────────────────┤                       └──────────────┘
│ - _iterator          │         uses
│ - _director          ├───────────────┐
│ + build_all()        │               │
│ + build_next()       │               ▼
│ + build_batch()      │        ┌──────────────┐
└──────────────────────┘        │ BookDirector │
                                │  (Builder)   │
                                └──────────────┘
```

### Fluxo de Dados

```
1. Cliente solicita busca
         │
         ▼
2. BookAPICollection cria Iterator apropriado
         │
         ├──► UnifiedAPIIterator (carrega tudo)
         │
         ├──► LazyAPIIterator (carrega sob demanda)
         │
         └──► MultiSourceIterator (combina APIs)
                      │
                      ▼
3. Iterator usa BookAPIInterface (Adapter)
                      │
                      ├──► GoogleBooksAdapter
                      │
                      └──► OpenLibraryAdapter
                                │
                                ▼
4. Adapter normaliza dados da API
                                │
                                ▼
5. Iterator fornece dados normalizados
                                │
                                ▼
6. IteratorBookBuilder + BookDirector
                                │
                                ▼
7. Objetos Book criados no banco de dados
```

---

## Casos de Uso

### Caso 1: Busca Simples com Cache

```python
from books.adapters import GoogleBooksAdapter
from books.iterators import UnifiedAPIIterator

def search_books(query: str, limit: int = 10):
    """Busca simples que carrega todos os resultados."""
    adapter = GoogleBooksAdapter()
    results = adapter.search_by_query(query, limit=limit)
    return UnifiedAPIIterator(results, api_name='google_books')

# Uso
iterator = search_books("python programming", limit=20)
for book in iterator:
    print(f"{book['title']} - {book['authors']}")
```

---

### Caso 2: Exploração Lazy (Economiza Requisições)

```python
from books.adapters import GoogleBooksAdapter
from books.iterators import LazyAPIIterator

def explore_books_lazy(query: str):
    """Explora resultados sem carregar tudo de uma vez."""
    adapter = GoogleBooksAdapter()
    iterator = LazyAPIIterator(adapter, query, page_size=10, max_pages=5)

    # Processa até encontrar o que precisa
    for book in iterator:
        if "Clean Code" in book['title']:
            return book
        # Carrega próxima página apenas se necessário

    return None

# Uso
book = explore_books_lazy("software engineering")
```

---

### Caso 3: Agregação de Múltiplas Fontes

```python
from books.adapters import GoogleBooksAdapter, OpenLibraryAdapter
from books.iterators import MultiSourceIterator

def search_all_sources(query: str):
    """Busca em todas as APIs disponíveis."""
    adapters = [
        GoogleBooksAdapter(),
        OpenLibraryAdapter()
    ]

    return MultiSourceIterator(
        adapters,
        query=query,
        limit_per_api=20,
        deduplicate_by_isbn=True
    )

# Uso
iterator = search_all_sources("django")
results = list(iterator)
print(f"Encontrados {len(results)} livros únicos em todas as APIs")

# Agrupa por fonte
grouped = iterator.group_by_source()
for api_name, books in grouped.items():
    print(f"{api_name}: {len(books)} livros")
```

---

### Caso 4: Importação em Lote com Builder

```python
from books.adapters import GoogleBooksAdapter, OpenLibraryAdapter
from books.iterators import BookAPICollection, IteratorBookBuilder

def import_books_to_database(query: str, max_books: int = 50):
    """Importa livros para o banco de dados automaticamente."""

    # Setup
    collection = BookAPICollection()
    collection.add_api(GoogleBooksAdapter())
    collection.add_api(OpenLibraryAdapter())

    # Cria iterador multi-fonte
    iterator = collection.create_multi_source_iterator(
        query=query,
        limit_per_api=max_books // 2
    )

    # Integra com Builder
    builder = IteratorBookBuilder(iterator)

    # Importa apenas livros novos
    books = builder.build_all(skip_existing=True)

    return books

# Uso
books = import_books_to_database("python programming", max_books=100)
print(f"Importados {len(books)} novos livros")
```

---

### Caso 5: Processamento em Lote com Controle

```python
from books.adapters import GoogleBooksAdapter
from books.iterators import BookAPICollection, IteratorBookBuilder

def import_books_in_batches(query: str, batch_size: int = 10):
    """Importa livros em lotes menores com controle fino."""

    collection = BookAPICollection()
    collection.add_api(GoogleBooksAdapter())

    iterator = collection.create_lazy_iterator(
        query=query,
        page_size=batch_size,
        max_pages=10
    )

    builder = IteratorBookBuilder(iterator)

    total_imported = 0
    while iterator.has_next():
        # Processa lote
        batch = builder.build_batch(count=batch_size, skip_existing=True)
        total_imported += len(batch)

        print(f"Lote processado: {len(batch)} livros")

        # Controle: para se atingir limite
        if total_imported >= 50:
            break

    return total_imported

# Uso
count = import_books_in_batches("machine learning", batch_size=10)
print(f"Total importado: {count} livros")
```

---

## Exemplos Práticos

### Exemplo Completo: Sistema de Recomendação

```python
from books.adapters import GoogleBooksAdapter, OpenLibraryAdapter
from books.iterators import BookAPICollection, MultiSourceIterator, IteratorBookBuilder
from books.models import Book

class BookRecommendationSystem:
    """Sistema que usa Iterator para popular banco de recomendações."""

    def __init__(self):
        self.collection = BookAPICollection()
        self.collection.add_api(GoogleBooksAdapter())
        self.collection.add_api(OpenLibraryAdapter())

    def populate_genre(self, genre: str, limit_per_api: int = 20):
        """Popula banco com livros de um gênero."""

        # Busca em todas as APIs
        iterator = self.collection.create_multi_source_iterator(
            query=genre,
            limit_per_api=limit_per_api,
            deduplicate=True
        )

        # Importa para banco
        builder = IteratorBookBuilder(iterator)
        books = builder.build_all(skip_existing=True)

        print(f"Gênero '{genre}': {len(books)} livros importados")
        return books

    def populate_multiple_genres(self, genres: list):
        """Popula múltiplos gêneros."""
        total_books = []

        for genre in genres:
            books = self.populate_genre(genre, limit_per_api=15)
            total_books.extend(books)

        return total_books

    def get_books_by_source(self, query: str):
        """Retorna livros agrupados por fonte."""
        iterator = self.collection.create_multi_source_iterator(query)
        return iterator.group_by_source()

# Uso
recommender = BookRecommendationSystem()

# Popula banco com diferentes gêneros
genres = ["Python Programming", "Web Development", "Data Science", "DevOps"]
all_books = recommender.populate_multiple_genres(genres)

print(f"Total de {len(all_books)} livros importados")
print(f"Livros únicos no banco: {Book.objects.count()}")
```

---

## Testes

Os testes cobrem todos os componentes do padrão Iterator. Para executar:

```bash
# Via Docker
docker-compose exec backend python manage.py test books.test_iterators -v 2

# Localmente (se tiver ambiente configurado)
cd backend
python manage.py test books.test_iterators -v 2
```

### Cobertura de Testes

#### 1. UnifiedAPIIterator (8 testes)
- ✅ `test_iterator_initialization` - Inicialização correta
- ✅ `test_iteration` - Iteração básica
- ✅ `test_for_loop_iteration` - Compatibilidade com for loop
- ✅ `test_reset` - Reinicialização
- ✅ `test_peek` - Peek sem avançar
- ✅ `test_skip` - Pular elementos
- ✅ `test_empty_results` - Resultados vazios
- ✅ `test_none_results` - Tratamento de None

**Arquivo**: `backend/books/test_iterators.py:19-158`

---

#### 2. LazyAPIIterator (5 testes)
- ✅ `test_lazy_loading_first_page` - Lazy load inicial
- ✅ `test_iteration_single_page` - Iteração em página única
- ✅ `test_empty_results` - Resultados vazios
- ✅ `test_api_error_handling` - Tratamento de erros
- ✅ `test_reset` - Reset do iterador lazy

**Arquivo**: `backend/books/test_iterators.py:161-230`

---

#### 3. MultiSourceIterator (5 testes)
- ✅ `test_multi_source_aggregation` - Agregação de múltiplas fontes
- ✅ `test_deduplication_by_isbn` - Deduplicação por ISBN
- ✅ `test_group_by_source` - Agrupamento por fonte
- ✅ `test_api_failure_resilience` - Resiliência a falhas
- ✅ `test_reset` - Reset do iterador

**Arquivo**: `backend/books/test_iterators.py:233-318`

---

#### 4. BookAPICollection (6 testes)
- ✅ `test_add_api` - Adição de APIs
- ✅ `test_add_api_chaining` - Method chaining
- ✅ `test_create_unified_iterator` - Criação de iterador unificado
- ✅ `test_create_lazy_iterator` - Criação de iterador lazy
- ✅ `test_create_multi_source_iterator` - Criação de iterador multi-fonte
- ✅ `test_empty_collection_error` - Validação de coleção vazia

**Arquivo**: `backend/books/test_iterators.py:321-381`

---

#### 5. IteratorBookBuilder (6 testes)
- ✅ `test_build_all` - Construção de todos os livros
- ✅ `test_build_next` - Construção incremental
- ✅ `test_build_batch` - Construção em lote
- ✅ `test_skip_existing_books` - Skip de livros existentes
- ✅ `test_build_with_invalid_data` - Tratamento de dados inválidos
- ✅ `test_complete_workflow` - Teste de integração completo

**Arquivo**: `backend/books/test_iterators.py:384-525`

---

### Total: 30+ testes cobrindo todos os componentes

---

## Integração com Outros Padrões

### Iterator + Adapter + Builder (3 Padrões GoF Integrados)

```python
from books.adapters import GoogleBooksAdapter        # ADAPTER
from books.builders import BookDirector              # BUILDER
from books.iterators import UnifiedAPIIterator       # ITERATOR
from books.iterators import IteratorBookBuilder      # INTEGRATION

# 1. ADAPTER: Normaliza dados de API externa
adapter = GoogleBooksAdapter()
normalized_data = adapter.search_by_query("clean code", limit=10)

# 2. ITERATOR: Navega pelos resultados normalizados
iterator = UnifiedAPIIterator(normalized_data, api_name='google_books')

# 3. BUILDER: Constrói objetos Book a partir dos dados
director = BookDirector()
books = []

for book_data in iterator:  # Iterator fornece dados
    book = director.construct_from_adapter(  # Builder cria objetos
        book_data,
        api_name='google_books'
    )
    books.append(book)

# Ou use o helper que integra tudo:
builder_helper = IteratorBookBuilder(iterator)
books = builder_helper.build_all(skip_existing=True)
```

### Fluxo de Integração

```
API Externa (Google Books, Open Library)
         │
         ▼
┌────────────────────┐
│  ADAPTER PATTERN   │  ◄── Normaliza interface da API
│  BookAPIInterface  │
└────────────────────┘
         │
         │ dados normalizados
         ▼
┌────────────────────┐
│ ITERATOR PATTERN   │  ◄── Navega pelos resultados
│  BookIterator      │
└────────────────────┘
         │
         │ item por item
         ▼
┌────────────────────┐
│  BUILDER PATTERN   │  ◄── Constrói objetos Book
│  BookDirector      │
└────────────────────┘
         │
         ▼
   Book (Model)
```

---

## Benefícios da Implementação

### 1. Separação de Responsabilidades
- **Iterator**: Lógica de navegação
- **Adapter**: Normalização de dados
- **Builder**: Construção de objetos

### 2. Extensibilidade
- Adicionar novos tipos de iteradores sem modificar código existente
- Adicionar novas APIs apenas criando novos Adapters
- Adicionar novas estratégias de construção no Builder

### 3. Reutilização
- Iteradores podem ser reutilizados com diferentes Adapters
- Adapters podem ser usados independentemente
- Builder Director pode construir de qualquer fonte normalizada

### 4. Testabilidade
- Componentes isolados facilitam testes unitários
- Mocks simples para testar cada parte
- 30+ testes cobrindo todos os cenários

### 5. Manutenibilidade
- Código organizado e bem documentado
- Responsabilidades claras
- Fácil de entender e modificar

---

## Próximos Passos

### Possíveis Extensões

1. **CachedIterator**: Iterator com cache de resultados
2. **FilteredIterator**: Iterator com filtros customizáveis
3. **RankedIterator**: Iterator que ordena por relevância
4. **PersistentIterator**: Iterator que salva estado em banco

### Exemplo de Extensão: FilteredIterator

```python
class FilteredIterator(BookIterator):
    """Iterator que filtra resultados baseado em predicados."""

    def __init__(self, iterator: BookIterator, predicate):
        self._iterator = iterator
        self._predicate = predicate

    def __next__(self):
        while self._iterator.has_next():
            item = next(self._iterator)
            if self._predicate(item):
                return item
        raise StopIteration

# Uso
iterator = UnifiedAPIIterator(results)
filtered = FilteredIterator(
    iterator,
    predicate=lambda book: book.get('average_rating', 0) >= 4.0
)

# Itera apenas sobre livros com rating >= 4.0
for book in filtered:
    print(book['title'])
```

---

## Referências

- **Gang of Four**: Design Patterns - Iterator Pattern
- **Documentação do Adapter**: `TESTE_ADAPTER.md`
- **Documentação do Builder**: `TESTE_BUILDER.md`
- **Código fonte**: `backend/books/iterators.py`
- **Testes**: `backend/books/test_iterators.py`

---

## Conclusão

O padrão Iterator implementado fornece uma solução robusta e extensível para navegar por resultados de múltiplas APIs de livros. A integração com os padrões Adapter e Builder cria um sistema coeso e poderoso para importação e gerenciamento de dados de livros de fontes externas.

A implementação segue fielmente o padrão GoF, mantém código limpo e testável, e fornece APIs intuitivas para os desenvolvedores.

**Total de linhas de código**: ~620 (iterators.py) + ~525 (test_iterators.py) = **~1145 linhas**

**Cobertura de testes**: 30+ testes cobrindo todos os componentes e casos de uso principais.
