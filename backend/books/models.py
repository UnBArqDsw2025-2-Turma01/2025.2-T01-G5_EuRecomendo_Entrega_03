from django.db import models
from django.contrib.postgres.fields import ArrayField

class Book(models.Model):
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    isbn = models.CharField(max_length=20, blank=True)
    description = models.TextField(blank=True)
    categories = ArrayField(
        models.CharField(max_length=100),
        blank=True,
        default=list
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def to_component(self):
        """Converte model Django para BookLeaf (padrão Composite)."""
        from .composite import BookLeaf
        return BookLeaf(
            book_id=self.id,
            title=self.title,
            author=self.author,
            description=self.description,
            isbn=self.isbn,
            categories=self.categories if hasattr(self, 'categories') else []
        )
    
    def __str__(self):
        return self.title


class Collection(models.Model):
    
    COLLECTION_TYPES = [
        ('list', 'Lista de Leitura'),
        ('category', 'Categoria'),
        ('tag', 'Tag'),
        ('recommendation', 'Recomendação')
    ]
    
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    collection_type = models.CharField(
        max_length=20,
        choices=COLLECTION_TYPES,
        default='list'
    )
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='subcollections'
    )
    books = models.ManyToManyField(Book, related_name='collections', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def to_component(self):
        from .composite import BookCollection
        
        collection = BookCollection(
            collection_id=self.id,
            name=self.name,
            description=self.description,
            collection_type=self.collection_type
        )
        
        # Adiciona livros
        for book in self.books.all():
            collection.add(book.to_component())
        
        # Adiciona subcoleções recursivamente
        for subcoll in self.subcollections.all():
            collection.add(subcoll.to_component())
        
        return collection
    
    def get_all_books_recursive(self):
        """Retorna todos os livros incluindo subcoleções."""
        books = list(self.books.all())
        for subcoll in self.subcollections.all():
            books.extend(subcoll.get_all_books_recursive())
        return books
    
    def __str__(self):
        return f"{self.get_collection_type_display()}: {self.name}"
    
    class Meta:
        ordering = ['name']