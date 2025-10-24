from users.infra.profile_service import ProfileService
from users.infra.proxies import CachedProfileProxy
from .service import RecommendationService

def build_recommendation_service() -> RecommendationService:
    real = ProfileService()
    cached = CachedProfileProxy(real, ttl_seconds=900)
    return RecommendationService(user_repo=cached)
