from django.apps import AppConfig


class RecommenderConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'recommender'

    def ready(self):
        try:
            from .engine import engine
            engine.initialize()
        except Exception:
            pass
