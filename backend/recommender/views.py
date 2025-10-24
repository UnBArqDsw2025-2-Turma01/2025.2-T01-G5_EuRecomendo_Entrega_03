from rest_framework.views import APIView
from rest_framework.response import Response


class RecommendView(APIView):
    def get(self, request):
        # placeholder response
        return Response({'recommendations': []})
