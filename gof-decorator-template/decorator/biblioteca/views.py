# views.py
from django.shortcuts import render
from .models import Livro
from .search_template import BuscaAvancadaLivros


def index(request):
    """Página inicial (feed padrão)."""
    todos_os_livros = Livro.objects.all()
    contexto = {"livros": todos_os_livros}
    return render(request, "biblioteca/feed.html", contexto)


def lista_livros(request):
    """Página com filtros e busca avançada."""
    busca = BuscaAvancadaLivros()
    livros = busca.buscar(request)
    contexto = {"livros": livros}
    return render(request, "biblioteca/feed.html", contexto)
