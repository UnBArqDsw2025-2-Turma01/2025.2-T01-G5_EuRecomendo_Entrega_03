from django.db import transaction
from django.contrib.auth import get_user_model
from books.models import Book
from .models import LibraryEntry


class LibraryService:
    @staticmethod
    @transaction.atomic
    def add_book_to_library(*, user=None, user_id=None, book_id, status="QUERO_LER"):
        """
        Facade: interface única para orquestrar validação e criação idempotente.
        Retorna (entry, created)
        """
        User = get_user_model()
        if user is None:
            if user_id is None:
                raise ValueError("user ou user_id deve ser informado")
            user = User.objects.get(id=user_id)
        book = Book.objects.get(id=book_id)

        entry, created = LibraryEntry.objects.add_for(user=user, book=book, status=status)
        return entry, created
