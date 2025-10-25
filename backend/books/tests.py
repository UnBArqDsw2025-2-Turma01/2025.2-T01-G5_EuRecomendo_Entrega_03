# backend/books/tests.py
from django.test import TestCase
from .models import Book, Collection
from .composite import BookLeaf, BookCollection


class CompositePatternTestCase(TestCase):
    """Testes para o padrão Composite."""
    
    def setUp(self):
        """Criar livros de teste."""
        self.book1 = Book.objects.create(
            title="Clean Code",
            author="Robert C. Martin",
            isbn="9780132350884",
            description="A Handbook of Agile Software Craftsmanship"
        )
        self.book2 = Book.objects.create(
            title="Design Patterns",
            author="Gang of Four",
            isbn="9780201633610",
            description="Elements of Reusable OO Software"
        )
        self.book3 = Book.objects.create(
            title="Refactoring",
            author="Martin Fowler",
            isbn="9780134757599",
            description="Improving the Design of Existing Code"
        )
    
    def test_book_leaf_component(self):
        """Testa componente Leaf (livro individual)."""
        leaf = self.book1.to_component()
        
        self.assertEqual(leaf.get_title(), "Clean Code")
        self.assertEqual(leaf.get_books_count(), 1)
        self.assertIn("Clean Code", leaf.display())
        self.assertEqual(leaf.get_description(), "A Handbook of Agile Software Craftsmanship")
    
    def test_collection_composite_component(self):
        """Testa componente Composite (coleção)."""
        collection = Collection.objects.create(
            name="Melhores Livros de Programação",
            collection_type="list",
            description="Livros essenciais para desenvolvedores"
        )
        collection.books.add(self.book1, self.book2)
        
        component = collection.to_component()
        self.assertEqual(component.get_books_count(), 2)
        self.assertIn("Melhores Livros", component.display())
        self.assertEqual(component.get_title(), "Melhores Livros de Programação")
    
    def test_nested_collections(self):
        """Testa coleções aninhadas (hierarquia)."""
        # Categoria principal
        software_category = Collection.objects.create(
            name="Engenharia de Software",
            collection_type="category",
            description="Livros sobre engenharia de software"
        )
        
        # Subcategorias
        patterns_category = Collection.objects.create(
            name="Padrões de Projeto",
            collection_type="category",
            parent=software_category,
            description="Livros sobre design patterns"
        )
        clean_code_category = Collection.objects.create(
            name="Clean Code",
            collection_type="category",
            parent=software_category,
            description="Livros sobre código limpo"
        )
        
        # Adicionar livros
        patterns_category.books.add(self.book2)
        clean_code_category.books.add(self.book1, self.book3)
        
        # Testar hierarquia
        root = software_category.to_component()
        self.assertEqual(root.get_books_count(), 3)
        
        # Verificar estrutura
        display_output = root.display()
        self.assertIn("Engenharia de Software", display_output)
        self.assertIn("Padrões de Projeto", display_output)
        self.assertIn("Clean Code", display_output)
        self.assertIn("Design Patterns", display_output)
    
    def test_add_remove_operations(self):
        """Testa operações de adicionar e remover."""
        collection = BookCollection(1, "Minha Lista")
        book1 = self.book1.to_component()
        book2 = self.book2.to_component()
        
        # Adicionar
        collection.add(book1)
        collection.add(book2)
        self.assertEqual(collection.get_books_count(), 2)
        
        # Remover
        collection.remove(book1)
        self.assertEqual(collection.get_books_count(), 1)
        
        # Verificar que não adiciona duplicados
        collection.add(book2)
        self.assertEqual(collection.get_books_count(), 1)
    
    def test_recursive_search(self):
        """Testa busca recursiva por título."""
        root = BookCollection(1, "Biblioteca")
        subcollection = BookCollection(2, "Programação")
        
        root.add(subcollection)
        subcollection.add(self.book1.to_component())
        subcollection.add(self.book2.to_component())
        
        results = root.find_by_title("Clean")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].get_title(), "Clean Code")
        
        # Buscar por termo que não existe
        results_empty = root.find_by_title("JavaScript")
        self.assertEqual(len(results_empty), 0)
    
    def test_uniform_treatment(self):
        """Testa tratamento uniforme de livros e coleções."""
        components = [
            self.book1.to_component(),
            BookCollection(1, "Coleção Teste")
        ]
        
        # Ambos devem ter mesma interface
        for component in components:
            self.assertTrue(hasattr(component, 'get_title'))
            self.assertTrue(hasattr(component, 'get_books_count'))
            self.assertTrue(hasattr(component, 'display'))
            self.assertTrue(hasattr(component, 'to_dict'))
    
    def test_to_dict_serialization(self):
        """Testa serialização para dicionário."""
        # Testar livro individual
        leaf = self.book1.to_component()
        leaf_dict = leaf.to_dict()
        
        self.assertEqual(leaf_dict['type'], 'book')
        self.assertEqual(leaf_dict['title'], 'Clean Code')
        self.assertEqual(leaf_dict['books_count'], 1)
        
        # Testar coleção
        collection = Collection.objects.create(
            name="Minha Coleção",
            collection_type="list"
        )
        collection.books.add(self.book1)
        
        component = collection.to_component()
        component_dict = component.to_dict()
        
        self.assertEqual(component_dict['type'], 'collection')
        self.assertEqual(component_dict['name'], 'Minha Coleção')
        self.assertEqual(component_dict['books_count'], 1)
        self.assertIsInstance(component_dict['children'], list)
    
    def test_get_child_operations(self):
        """Testa operações de obter filho por índice."""
        collection = BookCollection(1, "Teste")
        book1 = self.book1.to_component()
        book2 = self.book2.to_component()
        
        collection.add(book1)
        collection.add(book2)
        
        # Obter por índice válido
        child = collection.get_child(0)
        self.assertIsNotNone(child)
        self.assertEqual(child.get_title(), "Clean Code")
        
        # Obter por índice inválido
        invalid_child = collection.get_child(10)
        self.assertIsNone(invalid_child)
    
    def test_leaf_cannot_add_children(self):
        """Testa que Leaf não pode ter filhos."""
        leaf = self.book1.to_component()
        another_leaf = self.book2.to_component()
        
        # Deve lançar NotImplementedError
        with self.assertRaises(NotImplementedError):
            leaf.add(another_leaf)
        
        with self.assertRaises(NotImplementedError):
            leaf.remove(another_leaf)
        
        with self.assertRaises(NotImplementedError):
            leaf.get_child(0)
    
    def test_empty_collection(self):
        """Testa coleção vazia."""
        empty_collection = BookCollection(1, "Vazia")
        
        self.assertEqual(empty_collection.get_books_count(), 0)
        self.assertEqual(len(empty_collection.get_children()), 0)
        
        display = empty_collection.display()
        self.assertIn("Vazia", display)
        self.assertIn("(0 livros)", display)
    
    def test_deep_nesting(self):
        """Testa aninhamento profundo de coleções."""
        level1 = BookCollection(1, "Nível 1")
        level2 = BookCollection(2, "Nível 2")
        level3 = BookCollection(3, "Nível 3")
        
        level1.add(level2)
        level2.add(level3)
        level3.add(self.book1.to_component())
        level3.add(self.book2.to_component())
        
        # Contar livros recursivamente
        self.assertEqual(level1.get_books_count(), 2)
        self.assertEqual(level2.get_books_count(), 2)
        self.assertEqual(level3.get_books_count(), 2)
        
        # Buscar em estrutura profunda
        results = level1.find_by_title("Clean")
        self.assertEqual(len(results), 1)
    