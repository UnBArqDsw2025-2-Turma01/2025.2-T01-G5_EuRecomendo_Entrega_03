from django.shortcuts import render
from .models import Livro  

def index(request):
    todos_os_livros = Livro.objects.all()
    contexto = {
        'livros': todos_os_livros
    }
    return render(request, 'biblioteca/feed.html', contexto)
