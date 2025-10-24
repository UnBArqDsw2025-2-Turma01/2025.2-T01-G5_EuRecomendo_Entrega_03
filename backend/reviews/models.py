from django.db import models


class Review(models.Model):
    book_title = models.CharField(max_length=255)
    rating = models.IntegerField()
    text = models.TextField(blank=True)

    def __str__(self):
        return f"{self.book_title} ({self.rating})"
