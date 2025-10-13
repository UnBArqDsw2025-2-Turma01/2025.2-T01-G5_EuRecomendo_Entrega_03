from django.db import models


class Profile(models.Model):
    user_name = models.CharField(max_length=150)
    bio = models.TextField(blank=True)

    def __str__(self):
        return self.user_name
