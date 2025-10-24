import json
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import get_user_model
from books.models import Book
from .services import get_factory

User = get_user_model()

@csrf_exempt
def signup_view(request):
    if request.method != "POST":
        return HttpResponseBadRequest("Use POST")
    try:
        payload = json.loads(request.body.decode())
        factory = get_factory(payload.get("kind", "standard"))
        user = factory.create_user(payload)
        return JsonResponse({"id": user.id, "username": user.username, "is_staff": user.is_staff})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)

@csrf_exempt
def demo_register_book_view(request):
    if request.method != "POST":
        return HttpResponseBadRequest("Use POST")
    try:
        payload = json.loads(request.body.decode())
        factory = get_factory(payload.get("kind", "standard"))
        book = factory.register_book(title=payload["title"], author=payload.get("author", ""))
        return JsonResponse({"book_id": book.id, "title": book.title})
    except NotImplementedError as e:
        return JsonResponse({"error": str(e)}, status=403)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)
