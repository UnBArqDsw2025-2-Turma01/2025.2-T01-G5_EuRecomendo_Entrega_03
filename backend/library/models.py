from django.db import models
from django.conf import settings


class LibraryEntryManager(models.Manager):
    def add_for(self, user, book, status="QUERO_LER"):
        # Idempotent creation using get_or_create (Factory Method encapsulated in Manager)
        entry, created = self.get_or_create(user=user, book=book, defaults={"status": status})
        # If already exists and status changed, update it
        if not created and status and entry.status != status:
            entry.status = status
            entry.save(update_fields=["status"])
        return entry, created


class LibraryEntry(models.Model):
    STATUS_CHOICES = (
        ("QUERO_LER", "Quero ler"),
        ("LENDO", "Lendo"),
        ("LIDO", "Lido"),
        ("ABANDONADO", "Abandonado"),
    )
    id_library_entry = models.AutoField(primary_key=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    book = models.ForeignKey('books.Book', on_delete=models.CASCADE)
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="QUERO_LER")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = LibraryEntryManager()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "book"], name="unique_user_book")
        ]
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user} – {self.book} ({self.status})"
