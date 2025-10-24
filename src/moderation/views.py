import json
from django.http import JsonResponse, HttpResponseNotAllowed
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import get_user_model
from .services import ReviewService

User = get_user_model()

@csrf_exempt
def submit_review(request):
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])
    data = json.loads(request.body.decode("utf-8"))

    # simplificação: se não veio user, usa/gera um padrão
    user, _ = User.objects.get_or_create(username=data.get("username", "demo"), defaults={"email": "demo@example.com"})
    service = ReviewService()
    result = service.submit(
        user_id=user.id,
        book_title=data.get("book_title"),
        rating=data.get("rating"),
        text=data.get("text"),
    )

    return JsonResponse({
        "status": result.status.name,
        "errors": [{"code": e.code, "message": e.message} for e in result.errors],
    }, status=200 if result.status.name == "APPROVED" else 422)
