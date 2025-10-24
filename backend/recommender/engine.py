from __future__ import annotations
import logging
import threading
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)

class SingletonMeta(type):
    _instances: Dict[type, Any] = {}
    _lock: threading.Lock = threading.Lock()

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            with cls._lock:
                if cls not in cls._instances:
                    instance = super().__call__(*args, **kwargs)
                    cls._instances[cls] = instance
        return cls._instances[cls]


class RecommendationEngine(metaclass=SingletonMeta):
    """
    Singleton thread-safe em memória para dev.
    Mantém um cache simples de recomendações "top-rated" baseado em Review.
    """
    def __init__(self) -> None:
        self._state_lock = threading.RLock()
        self._initialized = False
        self._cache_version = 0
        self._top_cache: List[Dict[str, Any]] = []

    def initialize(self) -> None:
        if not self._initialized:
            with self._state_lock:
                if not self._initialized:
                    try:
                        self.warm_up()
                        self._initialized = True
                        logger.info("RecommendationEngine initialized")
                    except Exception as exc:
                        logger.exception("Failed to initialize engine: %s", exc)

    def warm_up(self) -> None:
        from django.db.models import Avg, Count
        from reviews.models import Review  # type: ignore
        top = (
            Review.objects.values("book_title")
            .annotate(avg_rating=Avg("rating"), votes=Count("id"))
            .order_by("-avg_rating", "-votes")[:50]
        )
        with self._state_lock:
            self._top_cache = [
                {
                    "book_title": row["book_title"],
                    "avg_rating": (float(row["avg_rating"]) if row["avg_rating"] is not None else None),
                    "votes": int(row["votes"]),
                }
                for row in top
            ]
            self._cache_version += 1

    def get_recommendations(self, user_id: Optional[int] = None, limit: int = 10) -> List[Dict[str, Any]]:
        self.initialize()
        with self._state_lock:
            if not self._top_cache:
                try:
                    self.warm_up()
                except Exception as exc:
                    logger.exception("On-demand warm_up failed: %s", exc)

            data = list(self._top_cache[:limit])
            if not data:
                try:
                    from books.models import Book  # type: ignore
                    data = [{"book_title": b.title, "avg_rating": None, "votes": 0} for b in Book.objects.all()[:limit]]
                except Exception:
                    data = []
        return data

    def reset(self) -> None:
        with self._state_lock:
            self._initialized = False
            self._top_cache.clear()
            self._cache_version += 1


# Instancia única por processo
engine = RecommendationEngine()