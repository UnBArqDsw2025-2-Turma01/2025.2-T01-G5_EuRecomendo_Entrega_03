from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import ReadingList
from .serializers import ReadingListSerializer
from users.models import UserProfile

class ReadingListViewSet(viewsets.ModelViewSet):
    queryset = ReadingList.objects.all()
    serializer_class = ReadingListSerializer

    @action(detail=False, methods=['get'], url_path='by-user/(?P<user_id>[^/.]+)')
    def by_user(self, request, user_id=None):
        """
        GET /api/reading-lists/by-user/{user_id}/
        Returns all reading lists for a specific user.
        """
        try:
            user = UserProfile.objects.get(pk=user_id)
        except UserProfile.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        reading_lists = ReadingList.objects.filter(owner=user)
        serializer = self.get_serializer(reading_lists, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def clone(self, request, pk=None):
        reading_list = self.get_object()
        new_owner_id = request.data.get('new_owner_id')
        try:
            new_owner = UserProfile.objects.get(pk=new_owner_id)
        except UserProfile.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        cloned_list = reading_list.clone_for_user(new_owner)
        serializer = self.get_serializer(cloned_list)
        return Response(serializer.data, status=status.HTTP_201_CREATED)