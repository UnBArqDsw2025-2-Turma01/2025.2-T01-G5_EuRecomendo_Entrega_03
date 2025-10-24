from django.core.management.base import BaseCommand
from django.db import transaction
from books.models import Book
from reviews.models import Review
from recommender.engine import engine


class Command(BaseCommand):
    help = "Seed demo data for recommendations (books + reviews). Idempotent."

    def handle(self, *args, **options):
        SEED_TAG = "[SEED]"
        dataset = [
            ("Clean Code", "Robert C. Martin", [5, 5, 4, 5]),
            ("The Pragmatic Programmer", "Andrew Hunt", [5, 4, 5, 4, 5]),
            ("Design Patterns", "GoF", [5, 5, 5, 4]),
            ("Refactoring", "Martin Fowler", [4, 4, 5, 4]),
            ("Domain-Driven Design", "Eric Evans", [5, 4, 4]),
        ]

        with transaction.atomic():
            Review.objects.filter(text__contains=SEED_TAG).delete()

            for title, author, ratings in dataset:
                Book.objects.get_or_create(title=title, author=author)
                for i, r in enumerate(ratings, start=1):
                    Review.objects.create(
                        book_title=title,
                        rating=r,
                        text=f"{SEED_TAG} review {i} for {title}",
                    )

        engine.reset()
        engine.initialize()

        self.stdout.write(self.style.SUCCESS("Seed created and recommendation cache warmed."))