#!/usr/bin/env python3
"""
Script de teste para demonstrar o funcionamento do ReviewBuilder e ReviewDirector.
Este script pode ser executado dentro do container Docker para testar as funcionalidades.
"""

import os
import sys
import django
from datetime import date, datetime

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eurecomendo.settings')
django.setup()

from reviews.review_builders import ReviewBuilder, ReviewDirector
from reviews.models import Review

def test_review_builder():
    """Testa o ReviewBuilder individualmente"""
    print("=== TESTANDO REVIEW BUILDER ===")
    
    # Criar instância do builder
    builder = ReviewBuilder()
    
    # Teste 1: Review básica
    print("\n1. Criando review básica...")
    try:
        review1 = (builder
                  .reset()
                  .set_book_title("Clean Code")
                  .set_rating(5)
                  .build())
        print(f"✅ Review criada: {review1}")
    except Exception as e:
        print(f"❌ Erro: {e}")
    
    # Teste 2: Review com comentário
    print("\n2. Criando review com comentário...")
    try:
        review2 = (builder
                  .reset()
                  .set_book_title("The Pragmatic Programmer")
                  .set_rating(4)
                  .set_comment("Excelente livro para desenvolvedores!")
                  .build())
        print(f"✅ Review criada: {review2}")
    except Exception as e:
        print(f"❌ Erro: {e}")
    
    # Teste 3: Review com período de leitura
    print("\n3. Criando review com período de leitura...")
    try:
        start_date = date(2024, 1, 1)
        end_date = date(2024, 1, 15)
        review3 = (builder
                  .reset()
                  .set_book_title("Design Patterns")
                  .set_rating(5)
                  .set_comment("Padrões essenciais para qualquer desenvolvedor")
                  .set_reading_period(start_date, end_date)
                  .build())
        print(f"✅ Review criada: {review3}")
    except Exception as e:
        print(f"❌ Erro: {e}")
    
    # Teste 4: Review em progresso (só data de início)
    print("\n4. Criando review em progresso...")
    try:
        review4 = (builder
                  .reset()
                  .set_book_title("Refactoring")
                  .set_rating(3)
                  .set_comment("Ainda lendo...")
                  .set_start_date(date(2024, 2, 1))
                  .build())
        print(f"✅ Review criada: {review4}")
    except Exception as e:
        print(f"❌ Erro: {e}")
    
    # Teste 5: Validação de erro - rating inválido
    print("\n5. Testando validação de rating inválido...")
    try:
        review5 = (builder
                  .reset()
                  .set_book_title("Test Book")
                  .set_rating(6)  # Rating inválido
                  .build())
        print(f"❌ Deveria ter falhado: {review5}")
    except ValueError as e:
        print(f"✅ Validação funcionou: {e}")
    
    # Teste 6: Validação de erro - dados obrigatórios
    print("\n6. Testando validação de dados obrigatórios...")
    try:
        review6 = (builder
                  .reset()
                  .set_book_title("Test Book")
                  # Sem rating - deve falhar
                  .build())
        print(f"❌ Deveria ter falhado: {review6}")
    except ValueError as e:
        print(f"✅ Validação funcionou: {e}")

def test_review_director():
    """Testa o ReviewDirector"""
    print("\n\n=== TESTANDO REVIEW DIRECTOR ===")
    
    builder = ReviewBuilder()
    director = ReviewDirector(builder)
    
    # Teste 1: Review rápida
    print("\n1. Criando review rápida...")
    try:
        review1 = director.build_quick_review("Python Cookbook", 4)
        print(f"✅ Review rápida criada: {review1}")
    except Exception as e:
        print(f"❌ Erro: {e}")
    
    # Teste 2: Review detalhada
    print("\n2. Criando review detalhada...")
    try:
        review2 = director.build_detailed_review(
            book_title="Effective Python",
            rating=5,
            comment="Livro fundamental para programadores Python",
            start_date=date(2024, 1, 10),
            end_date=date(2024, 1, 25)
        )
        print(f"✅ Review detalhada criada: {review2}")
    except Exception as e:
        print(f"❌ Erro: {e}")
    
    # Teste 3: Review em progresso
    print("\n3. Criando review em progresso...")
    try:
        review3 = director.build_reading_in_progress(
            book_title="Fluent Python",
            rating=4,
            comment="Lendo aos poucos...",
            start_date=date(2024, 2, 1)
        )
        print(f"✅ Review em progresso criada: {review3}")
    except Exception as e:
        print(f"❌ Erro: {e}")

def list_all_reviews():
    """Lista todas as reviews criadas"""
    print("\n\n=== TODAS AS REVIEWS CRIADAS ===")
    reviews = Review.objects.all().order_by('-created_at')
    
    if not reviews:
        print("Nenhuma review encontrada.")
        return
    
    for i, review in enumerate(reviews, 1):
        print(f"\n{i}. {review}")
        print(f"   Rating: {review.rating}/5")
        if review.text:
            print(f"   Comentário: {review.text}")
        if review.start_date:
            print(f"   Data início: {review.start_date}")
        if review.end_date:
            print(f"   Data fim: {review.end_date}")
        print(f"   Criada em: {review.created_at}")

def cleanup_reviews():
    """Remove todas as reviews de teste"""
    print("\n\n=== LIMPANDO REVIEWS DE TESTE ===")
    count = Review.objects.count()
    Review.objects.all().delete()
    print(f"✅ {count} reviews removidas.")

if __name__ == "__main__":
    print("🚀 INICIANDO TESTES DO REVIEW BUILDER")
    print("=" * 50)
    
    try:
        # Executar testes
        test_review_builder()
        test_review_director()
        list_all_reviews()
        
        # Perguntar se quer limpar
        print("\n" + "=" * 50)
        response = input("Deseja limpar as reviews de teste? (s/n): ").lower()
        if response in ['s', 'sim', 'y', 'yes']:
            cleanup_reviews()
        
        print("\n✅ Testes concluídos com sucesso!")
        
    except Exception as e:
        print(f"\n❌ Erro durante os testes: {e}")
        sys.exit(1)

