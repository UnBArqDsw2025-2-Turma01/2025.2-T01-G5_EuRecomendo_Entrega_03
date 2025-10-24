import logging
from django.core.cache import cache
from users.domain.repositories import UserRepository, ProfileDict

logger = logging.getLogger("eu.proxy")  # nome próprio do logger

class CachedProfileProxy(UserRepository):
    def __init__(self, real: UserRepository, ttl_seconds: int = 900):
        self._real = real
        self._ttl = ttl_seconds

    def _key(self, user_id: int) -> str:
        return f"user:{user_id}:profile"

    def get_profile(self, user_id: int) -> ProfileDict | None:
        key = self._key(user_id)
        hit = cache.get(key)
        if hit is not None:
            logger.info("HIT key=%s", key)
            return hit
        logger.info("MISS key=%s", key)
        result = self._real.get_profile(user_id)
        if result is not None:
            cache.set(key, result, timeout=self._ttl)
        return result
