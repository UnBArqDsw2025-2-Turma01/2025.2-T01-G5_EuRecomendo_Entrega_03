from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Optional, List, Protocol
from django.contrib.auth import get_user_model
from .models import Review

User = get_user_model()


class Status(Enum):
    APPROVED = auto()
    REJECTED = auto()

@dataclass
class RuleViolation:
    code: str
    message: str

@dataclass
class ModerationResult:
    status: Status
    errors: List[RuleViolation] = field(default_factory=list)
    final_text: Optional[str] = None

@dataclass
class ReviewContext:
    user_id: int
    book_title: str
    rating: Optional[int]
    text: Optional[str]
    # campo mutável para sanitização:
    sanitized_text: Optional[str] = None
    # coleta de erros (aggregate mode):
    errors: List[RuleViolation] = field(default_factory=list)


class Handler(Protocol):
    def set_next(self, nxt: "Handler") -> "Handler": ...
    def handle(self, ctx: ReviewContext) -> ModerationResult: ...

class AbstractHandler(Handler):
    _next: Optional[Handler] = None

    def set_next(self, nxt: Handler) -> Handler:
        self._next = nxt
        return nxt

    def handle(self, ctx: ReviewContext) -> ModerationResult:
        self.do_handle(ctx)
        if any(True for _ in ctx.errors):  
            pass
        if self._next:
            return self._next.handle(ctx)
        if ctx.errors:
            return ModerationResult(status=Status.REJECTED, errors=ctx.errors, final_text=ctx.sanitized_text or ctx.text)
        return ModerationResult(status=Status.APPROVED, errors=[], final_text=ctx.sanitized_text or ctx.text)

    def do_handle(self, ctx: ReviewContext) -> None:
        return


class RequiredFieldsHandler(AbstractHandler):
    def do_handle(self, ctx: ReviewContext) -> None:
        if not ctx.book_title:
            ctx.errors.append(RuleViolation("MISSING_BOOK", "O título do livro é obrigatório."))
        if ctx.rating is None:
            ctx.errors.append(RuleViolation("MISSING_RATING", "A nota (rating) é obrigatória."))
        if ctx.text is None or not str(ctx.text).strip():
            ctx.errors.append(RuleViolation("MISSING_TEXT", "O texto da review é obrigatório."))

class LengthHandler(AbstractHandler):
    def __init__(self, min_chars: int = 5, max_chars: int = 1000):
        self.min = min_chars
        self.max = max_chars

    def do_handle(self, ctx: ReviewContext) -> None:
        if ctx.text is None:
            return
        t = ctx.text.strip()
        if len(t) < self.min:
            ctx.errors.append(RuleViolation("TEXT_TOO_SHORT", f"O texto deve ter ao menos {self.min} caracteres."))
        if len(t) > self.max:
            ctx.errors.append(RuleViolation("TEXT_TOO_LONG", f"O texto deve ter no máximo {self.max} caracteres."))

class ProfanityHandler(AbstractHandler):
    def __init__(self, deny_list: Optional[List[str]] = None):
        self.deny_list = [w.lower() for w in (deny_list or ["idiota", "imbecil", "palavrao"])]

    def do_handle(self, ctx: ReviewContext) -> None:
        if not ctx.text:
            return
        lowered = ctx.text.lower()
        if any(bad in lowered for bad in self.deny_list):
            ctx.errors.append(RuleViolation("PROFANITY", "Seu texto contém linguagem imprópria."))

class DuplicateHandler(AbstractHandler):
    """Considera duplicado se o mesmo usuário já avaliou o mesmo livro."""
    def do_handle(self, ctx: ReviewContext) -> None:
        if ctx.user_id and ctx.book_title:
            exists = Review.objects.filter(user_id=ctx.user_id, book_title=ctx.book_title).exists()
            if exists:
                ctx.errors.append(RuleViolation("DUPLICATE", "Você já realizou uma review para este livro."))


def build_default_chain() -> Handler:
    head = RequiredFieldsHandler()
    head.set_next(LengthHandler()) \
        .set_next(ProfanityHandler()) \
        .set_next(DuplicateHandler())
    return head
