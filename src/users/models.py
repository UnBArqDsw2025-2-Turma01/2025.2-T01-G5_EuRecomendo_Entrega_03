from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    """
    Usuário customizado. Flags is_staff/is_superuser já existem em AbstractUser.
    Mantemos simples para focar no Abstract Factory.
    """
    pass
