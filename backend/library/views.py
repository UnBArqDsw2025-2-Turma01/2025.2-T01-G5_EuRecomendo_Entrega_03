from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from .models import LibraryEntry
from .serializers import LibraryEntrySerializer, AddToLibrarySerializer
from .services import LibraryService


class LibraryEntryViewSet(viewsets.ModelViewSet):
    queryset = LibraryEntry.objects.all()
    serializer_class = LibraryEntrySerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def create(self, request, *args, **kwargs):
        serializer = AddToLibrarySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        status_value = serializer.validated_data.get("status", "QUERO_LER")
        book_id = serializer.validated_data["book_id"]

        user = request.user if request.user and request.user.is_authenticated else None
        user_id = getattr(request.user, "id", None)

        entry, created = LibraryService.add_book_to_library(
            user=user, user_id=user_id, book_id=book_id, status=status_value
        )
        data = LibraryEntrySerializer(entry).data
        data["created"] = created
        http_status = status.HTTP_201_CREATED if created else status.HTTP_200_OK
        return Response(data, status=http_status)
