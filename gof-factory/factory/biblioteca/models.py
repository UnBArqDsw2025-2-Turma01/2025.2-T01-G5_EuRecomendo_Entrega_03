
from django.db import models

class Livro(models.Model):
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=200)
    # Vamos usar o 'cover' para guardar o emoji 📚
    cover = models.CharField(max_length=10, default='📚')
    genre = models.CharField(max_length=100)
    rating = models.DecimalField(max_digits=2, decimal_places=1) # Ex: 4.5

    def __str__(self):
        return self.title