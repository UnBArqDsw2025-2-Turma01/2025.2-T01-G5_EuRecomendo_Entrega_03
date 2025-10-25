# books/serializers.py
from rest_framework import serializers

from .models import ReadingList

class ReadingListSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReadingList
        fields = ['id', 'name', 'owner', 'books']