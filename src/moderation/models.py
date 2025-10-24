from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reviews")
    book_title = models.CharField(max_length=255)
    rating = models.IntegerField()  # 1..5 (validado via chain)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [models.Index(fields=["user", "book_title"])]

    def __str__(self):
        return f"Review({self.user_id}, {self.book_title}, {self.rating})"
