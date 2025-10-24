from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.request import Request
from .engine import engine

class RecommendView(APIView):
    def get(self, request: Request):
        try:
            limit = int(request.query_params.get("limit", "10"))
        except ValueError:
            limit = 10
        user_id = request.user.id if getattr(request, "user", None) and request.user.is_authenticated else None
        recs = engine.get_recommendations(user_id=user_id, limit=limit)
        return Response({"recommendations": recs})
