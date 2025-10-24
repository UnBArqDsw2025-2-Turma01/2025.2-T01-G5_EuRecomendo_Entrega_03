from django.contrib.auth import get_user_model
from .abstractFactory import UserFactory

User = get_user_model()

class StandardUserFactory(UserFactory):
    def create_user(self, data: dict) -> User:
        user = User(username=data["username"], email=data["email"], is_staff=False, is_superuser=False)
        user.set_password(data["password"])
        user.save()
        return user
