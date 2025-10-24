from django.conf import settings
from django.db import models

class Book(models.Model):
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255, blank=True)
    synopsis = models.TextField(blank=True)

    def __str__(self):
        return f"{self.title} por {self.author}".strip()

class Review(models.Model):
    rating = models.IntegerField()
    text = models.TextField(blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="reviews")
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name="reviews")

    def __str__(self):
        return f"Avaliação de {self.user.username} para {self.book.title}"
