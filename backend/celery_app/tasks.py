# Placeholder for celery tasks
from celery import shared_task


@shared_task
def ping():
    return 'pong'


@shared_task
def recompute_recommendations(user_id: int):
    # Placeholder side-effect for Observer
    # In a real scenario, reprocess user recommendations here.
    return {"user_id": user_id, "status": "recomputed"}
