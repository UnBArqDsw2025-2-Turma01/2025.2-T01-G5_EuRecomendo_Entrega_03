from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from moderation.services import ReviewService
from moderation.models import Review

User = get_user_model()

class Command(BaseCommand):
    help = "Demonstra o Chain of Responsibility moderando reviews."

    def handle(self, *args, **kwargs):
        user, _ = User.objects.get_or_create(username="alice", defaults={"email": "alice@example.com"})
        
        Review.objects.get_or_create(user=user, book_title="Clean Code", rating=5, text="Excelente livro!")

        service = ReviewService()

        cases = [
            dict(book_title="", rating=5, text="Faltou título"),                               
            dict(book_title="DDD", rating=5, text="ok"),                                      
            dict(book_title="Refactoring", rating=4, text="Livro imbecil! não gostei"),       
            dict(book_title="Clean Code", rating=4, text="Já avaliei antes"),                 
            dict(book_title="Patterns", rating=5, text="Livro muito bom, recomendo a todos!"),
        ]

        for i, c in enumerate(cases, start=1):
            res = service.submit(user.id, **c)
            self.stdout.write(self.style.WARNING(f"Case {i}: {c['book_title']}"))
            self.stdout.write(f"Status: {res.status.name}")
            if res.errors:
                for e in res.errors:
                    self.stdout.write(f" - {e.code}: {e.message}")
            self.stdout.write("-" * 40)
