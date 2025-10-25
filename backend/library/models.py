from django.db import models
from users.models import UserProfile
from books.models import  Book
import copy

class ReadingList(models.Model):
    owner = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='reading_lists')
    name = models.CharField(max_length=255)
    books = models.ManyToManyField('books.Book', related_name='in_reading_lists')  # must be active

    def clone_for_user(self, new_owner):
        """
        Create a copy of this reading list for a new user.
        """
        # 1. Create new ReadingList instance
        cloned_list = ReadingList.objects.create(
            owner=new_owner,
            name=f"{self.name} (cloned)"
        )

        # 2. Copy all books
        cloned_list.books.set(self.books.all())

        return cloned_list

    def __str__(self):
        return self.name