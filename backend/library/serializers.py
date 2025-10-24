from rest_framework import serializers
from .models import LibraryEntry


class LibraryEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = LibraryEntry
        fields = ["id_library_entry", "user", "book",
                  "status", "created_at", "updated_at"]
        read_only_fields = ["id_library_entry", "created_at", "updated_at"]


class AddToLibrarySerializer(serializers.Serializer):
    book_id = serializers.IntegerField()
    status = serializers.ChoiceField(
        choices=LibraryEntry.STATUS_CHOICES, required=False, default="QUERO_LER")
