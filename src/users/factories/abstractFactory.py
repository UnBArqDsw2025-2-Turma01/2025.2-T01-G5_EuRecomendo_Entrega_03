from abc import ABC, abstractmethod
from django.contrib.auth import get_user_model
from books.models import Book, Review

User = get_user_model()

class UserFactory(ABC):
    @abstractmethod
    def create_user(self, data: dict) -> User: ...
    def create_review(self, *, user: User, book: Book, rating: int, text: str = "") -> Review:
        return Review.objects.create(user=user, book=book, rating=rating, text=text)
    def register_book(self, *, title: str, author: str = "", synopsis: str = "") -> Book:
        raise NotImplementedError("Este tipo de usuário não registra livros.")
