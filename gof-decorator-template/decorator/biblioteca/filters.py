from abc import ABC, abstractmethod

class FiltroBase(ABC):
    @abstractmethod
    def aplicar(self, queryset):
        pass

class FiltroConcreto(FiltroBase):
    def aplicar(self, queryset):
        return queryset

class FiltroDecorator(FiltroBase):
    def __init__(self, filtro):
        self._filtro = filtro

class FiltroAutor(FiltroDecorator):
    def __init__(self, filtro, autor):
        super().__init__(filtro)
        self.autor = autor

    def aplicar(self, queryset):
        queryset = self._filtro.aplicar(queryset)
        return queryset.filter(author__icontains=self.autor)

class FiltroCategoria(FiltroDecorator):
    def __init__(self, filtro, categoria):
        super().__init__(filtro)
        self.categoria = categoria

    def aplicar(self, queryset):
        queryset = self._filtro.aplicar(queryset)
        return queryset.filter(genre__icontains=self.categoria)

