from django.contrib.auth import get_user_model
from books.models import Book
from .abstractFactory import UserFactory

User = get_user_model()

class StaffUserFactory(UserFactory):
    def create_user(self, data: dict) -> User:
        user = User(username=data["username"], email=data["email"], is_staff=True, is_superuser=True)
        user.set_password(data["password"])
        user.save()
        return user
    def register_book(self, *, title: str, author: str = "", synopsis: str = "") -> Book:
        return Book.objects.create(title=title, author=author, synopsis=synopsis)
