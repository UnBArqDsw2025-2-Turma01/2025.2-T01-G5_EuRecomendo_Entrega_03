from django.db import models


class Book(models.Model):
    # Campos básicos
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255, help_text="Autor(es) do livro")
    genre = models.CharField(max_length=100, blank=True, help_text="Gênero principal do livro")

    # Metadados do livro
    isbn = models.CharField(max_length=13, blank=True, null=True, unique=True,
                           help_text="ISBN-10 ou ISBN-13")
    publisher = models.CharField(max_length=255, blank=True, help_text="Editora")
    publication_year = models.IntegerField(blank=True, null=True,
                                          help_text="Ano de publicação")
    description = models.TextField(blank=True, help_text="Sinopse do livro")
    cover_url = models.URLField(max_length=500, blank=True, null=True,
                               help_text="URL da imagem da capa")
    page_count = models.IntegerField(blank=True, null=True,
                                    help_text="Número de páginas")
    language = models.CharField(max_length=10, default='pt-BR',
                               help_text="Código do idioma (ISO 639-1)")

    # Campos JSON para dados flexíveis
    categories = models.JSONField(default=list, blank=True,
                                 help_text="Lista de categorias/gêneros adicionais")
    average_rating = models.DecimalField(max_digits=3, decimal_places=2,
                                        blank=True, null=True,
                                        help_text="Avaliação média (0.00 a 5.00)")

    # Metadados de controle
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    source = models.CharField(max_length=50, default='manual',
                             help_text="Origem dos dados: manual, google_books, open_library")

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Livro'
        verbose_name_plural = 'Livros'

    def __str__(self):
        return f"{self.title} - {self.author}"
