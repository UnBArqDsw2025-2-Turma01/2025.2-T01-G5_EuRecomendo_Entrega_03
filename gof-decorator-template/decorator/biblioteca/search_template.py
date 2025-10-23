from abc import ABC, abstractmethod
from .models import Livro
from .filters import (
    FiltroConcreto,
    FiltroAutor,
    FiltroCategoria,
)

class LivroSearchTemplate(ABC):
    def buscar(self, request):
        filtro = self.preparar_filtros(request)
        queryset = self.aplicar_filtros(filtro)
        queryset = self.ordenar_resultados(request, queryset)
        return self.exibir_resultados(queryset)

    @abstractmethod
    def preparar_filtros(self, request):
        pass

    def aplicar_filtros(self, filtro):
        return filtro.aplicar(Livro.objects.all())

    def ordenar_resultados(self, request, queryset):
        ordenar_por = request.GET.get("ordenar_por")
        if ordenar_por == "titulo":
            return queryset.order_by("title")
        return queryset

    def exibir_resultados(self, queryset):
        return queryset


class BuscaAvancadaLivros(LivroSearchTemplate):
    def preparar_filtros(self, request):
        filtro = FiltroConcreto()
        autor = request.GET.get("autor")
        if autor:
            filtro = FiltroAutor(filtro, autor)
        categoria = request.GET.get("categoria")
        if categoria:
            filtro = FiltroCategoria(filtro, categoria)
        return filtro
