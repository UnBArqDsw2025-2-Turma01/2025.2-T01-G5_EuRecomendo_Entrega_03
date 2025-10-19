from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import LibraryEntry
try:
    from celery_app.tasks import recompute_recommendations
except Exception:  # Celery optional in dev
    recompute_recommendations = None  # type: ignore


@receiver(post_save, sender=LibraryEntry)
def library_entry_post_save(sender, instance: LibraryEntry, created, **kwargs):
    if recompute_recommendations is not None:
        try:
            recompute_recommendations.delay(user_id=instance.user_id)
        except Exception:
            # Fallback no-op; em dev sem broker, ignore
            pass
