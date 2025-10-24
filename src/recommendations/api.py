from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from .container import build_recommendation_service
from django.core.cache import cache

class RecommendMeView(APIView):
    def get(self, request, user_id: int):
        key = f"user:{user_id}:profile"
        was_cached = cache.get(key) is not None
        svc = build_recommendation_service()
        recs = svc.get_recommendations(user_id)
        resp = Response({"recommendations": recs})
        resp["X-UserProfile-Cache"] = "HIT" if was_cached else "MISS"
        return resp
