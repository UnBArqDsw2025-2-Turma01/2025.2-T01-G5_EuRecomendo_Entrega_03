from abc import ABC, abstractmethod
from typing import List, Dict, Optional

class BookComponent(ABC):
    """Interface comum para livros individuais e coleções."""
    
    @abstractmethod
    def get_title(self) -> str:
        """Retorna o título do componente."""
        pass
    
    @abstractmethod
    def get_description(self) -> str:
        """Retorna a descrição do componente."""
        pass
    
    @abstractmethod
    def get_books_count(self) -> int:
        """Retorna quantidade de livros (1 para livro individual, n para coleção)."""
        pass
    
    @abstractmethod
    def display(self, indent: int = 0) -> str:
        """Exibe estrutura hierárquica."""
        pass
    
    @abstractmethod
    def to_dict(self) -> Dict:
        """Serializa componente para dicionário."""
        pass
    
    def add(self, component: 'BookComponent') -> None:
        """Adiciona componente filho (só para Composite)."""
        raise NotImplementedError("Operação não suportada para este componente")
    
    def remove(self, component: 'BookComponent') -> None:
        """Remove componente filho (só para Composite)."""
        raise NotImplementedError("Operação não suportada para este componente")
    
    def get_child(self, index: int) -> Optional['BookComponent']:
        """Obtém componente filho por índice (só para Composite)."""
        raise NotImplementedError("Operação não suportada para este componente")
    
class BookLeaf(BookComponent):
    """Representa um livro individual (folha da árvore)."""
    
    def __init__(self, book_id: int, title: str, author: str, 
                 description: str = "", isbn: str = "", 
                 categories: List[str] = None):
        self.book_id = book_id
        self.title = title
        self.author = author
        self.description = description
        self.isbn = isbn
        self.categories = categories or []
    
    def get_title(self) -> str:
        return self.title
    
    def get_description(self) -> str:
        return self.description or f"Livro: {self.title} por {self.author}"
    
    def get_books_count(self) -> int:
        return 1
    
    def display(self, indent: int = 0) -> str:
        """Exibe livro individual."""
        prefix = "  " * indent
        return f"{prefix}📕 {self.title} - {self.author}"
    
    def to_dict(self) -> Dict:
        """Serializa livro para JSON."""
        return {
            'type': 'book',
            'id': self.book_id,
            'title': self.title,
            'author': self.author,
            'description': self.description,
            'isbn': self.isbn,
            'categories': self.categories,
            'books_count': 1
        }
        
class BookCollection(BookComponent):
    """Representa uma coleção de livros ou outras coleções (composite)."""
    
    def __init__(self, collection_id: int, name: str, 
                 description: str = "", collection_type: str = "list"):
        self.collection_id = collection_id
        self.name = name
        self.description = description
        self.collection_type = collection_type  # 'list', 'category', 'tag'
        self._children: List[BookComponent] = []
    
    def add(self, component: BookComponent) -> None:
        """Adiciona livro ou subcoleção."""
        if component not in self._children:
            self._children.append(component)
    
    def remove(self, component: BookComponent) -> None:
        """Remove livro ou subcoleção."""
        if component in self._children:
            self._children.remove(component)
    
    def get_child(self, index: int) -> Optional[BookComponent]:
        """Obtém componente filho por índice."""
        if 0 <= index < len(self._children):
            return self._children[index]
        return None
    
    def get_children(self) -> List[BookComponent]:
        """Retorna todos os filhos."""
        return self._children.copy()
    
    def get_title(self) -> str:
        return self.name
    
    def get_description(self) -> str:
        return self.description or f"Coleção: {self.name}"
    
    def get_books_count(self) -> int:
        """Conta recursivamente todos os livros."""
        total = 0
        for child in self._children:
            total += child.get_books_count()
        return total
    
    def display(self, indent: int = 0) -> str:
        """Exibe estrutura hierárquica recursivamente."""
        prefix = "  " * indent
        icon = "📁" if self.collection_type == "category" else "📚"
        result = f"{prefix}{icon} {self.name} ({self.get_books_count()} livros)\n"
        
        for child in self._children:
            result += child.display(indent + 1) + "\n"
        
        return result.rstrip()
    
    def to_dict(self) -> Dict:
        """Serializa coleção e filhos para JSON recursivamente."""
        return {
            'type': 'collection',
            'id': self.collection_id,
            'name': self.name,
            'description': self.description,
            'collection_type': self.collection_type,
            'books_count': self.get_books_count(),
            'children': [child.to_dict() for child in self._children]
        }
    
    def find_by_title(self, title: str) -> List[BookComponent]:
        """Busca recursiva por título."""
        results = []
        for child in self._children:
            if title.lower() in child.get_title().lower():
                results.append(child)
            if isinstance(child, BookCollection):
                results.extend(child.find_by_title(title))
        return results