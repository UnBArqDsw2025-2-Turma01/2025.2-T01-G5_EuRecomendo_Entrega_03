from dataclasses import asdict
from django.contrib.auth import get_user_model
from django.db import transaction
from .models import Review
from .handlers import ReviewContext, build_default_chain, Status

User = get_user_model()

class ReviewService:
    def __init__(self, chain=None):
        self.chain = chain or build_default_chain()

    @transaction.atomic
    def submit(self, user_id: int, book_title: str, rating: int, text: str):
        ctx = ReviewContext(user_id=user_id, book_title=book_title, rating=rating, text=text)
        result = self.chain.handle(ctx)

        if result.status is Status.APPROVED:
            Review.objects.create(
                user_id=user_id,
                book_title=book_title,
                rating=rating,
                text=result.final_text or text,
            )
        return result
