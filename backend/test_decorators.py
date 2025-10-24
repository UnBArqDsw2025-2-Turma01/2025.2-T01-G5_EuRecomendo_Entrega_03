#!/usr/bin/env python3
"""
Teste que demonstra claramente o padrão Decorator implementado em review_decorators.py
COM DADOS REAIS E RESULTADOS PRÁTICOS
"""

import os
import sys
import django
from datetime import date, timedelta

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eurecomendo.settings')
django.setup()

from reviews.models import Review
from reviews.review_decorators import (
    ReviewWithReadingTime,
    ReviewWithSentimentAnalysis,
    ReviewWithRecommendation,
    ReviewWithStatistics,
    ReviewDecoratorFactory
)

def test_decorator_pattern_with_real_data():
    """
    Testa e demonstra o padrão Decorator com dados reais do banco
    """
    print("🎯 TESTE DO PADRÃO DECORATOR - DADOS REAIS E RESULTADOS PRÁTICOS")
    print("=" * 80)
    
    # Obter reviews do banco de dados
    reviews = list(Review.objects.all())
    print(f"📊 DADOS DE ENTRADA: {len(reviews)} reviews encontradas no banco de dados")
    
    if not reviews:
        print("❌ Nenhuma review encontrada no banco de dados!")
        return False
    
    # Mostrar dados brutos
    print("\n📋 DADOS BRUTOS DAS REVIEWS:")
    print("-" * 50)
    for i, review in enumerate(reviews[:5], 1):  # Mostrar apenas as primeiras 5
        print(f"   {i}. {review.book_title} - Rating: {review.rating} - Texto: {len(review.text)} chars")
    
    if len(reviews) > 5:
        print(f"   ... e mais {len(reviews) - 5} reviews")
    
    # 1. TESTE: Decorador de Tempo de Leitura
    print("\n🕒 TESTE 1: DECORATOR DE TEMPO DE LEITURA")
    print("-" * 50)
    
    review_with_reading_time = ReviewWithReadingTime(reviews[0])
    reading_data = review_with_reading_time.get_enhanced_data()
    
    print(f"📖 Livro: {reading_data['book_title']}")
    print(f"⭐ Rating: {reading_data['rating']}")
    print(f"📅 Status: {reading_data['reading_status']}")
    
    if 'reading_days' in reading_data:
        print(f"⏱️  Dias de leitura: {reading_data['reading_days']}")
    elif 'days_since_start' in reading_data:
        print(f"⏱️  Dias desde o início: {reading_data['days_since_start']}")
    
    # 2. TESTE: Decorador de Análise de Sentimento
    print("\n😊 TESTE 2: DECORATOR DE ANÁLISE DE SENTIMENTO")
    print("-" * 50)
    
    review_with_sentiment = ReviewWithSentimentAnalysis(reviews[0])
    sentiment_data = review_with_sentiment.get_enhanced_data()
    
    print(f"📖 Livro: {sentiment_data['book_title']}")
    print(f"⭐ Rating: {sentiment_data['rating']}")
    print(f"😊 Sentimento: {sentiment_data['sentiment']}")
    print(f"📊 Score de Sentimento: {sentiment_data['sentiment_score']}")
    print(f"📝 Texto: {sentiment_data['text'][:100]}...")
    
    # 3. TESTE: Decorador de Recomendação
    print("\n👍 TESTE 3: DECORATOR DE RECOMENDAÇÃO")
    print("-" * 50)
    
    review_with_recommendation = ReviewWithRecommendation(reviews[0])
    recommendation_data = review_with_recommendation.get_enhanced_data()
    
    print(f"📖 Livro: {recommendation_data['book_title']}")
    print(f"⭐ Rating: {recommendation_data['rating']}")
    print(f"👍 Recomendação: {recommendation_data['recommendation']}")
    print(f"💪 Força da Recomendação: {recommendation_data['recommendation_strength']:.2f}")
    
    # 4. TESTE: Decorador de Estatísticas
    print("\n📊 TESTE 4: DECORATOR DE ESTATÍSTICAS")
    print("-" * 50)
    
    review_with_statistics = ReviewWithStatistics(reviews[0])
    statistics_data = review_with_statistics.get_enhanced_data()
    
    print(f"📖 Livro: {statistics_data['book_title']}")
    print(f"⭐ Rating: {statistics_data['rating']}")
    print(f"📝 Palavras: {statistics_data['word_count']}")
    print(f"🔤 Caracteres: {statistics_data['character_count']}")
    print(f"📊 Percentual do Rating: {statistics_data['rating_percentage']:.1f}%")
    print(f"🆕 Review Recente: {statistics_data['is_recent']}")
    
    # 5. TESTE: Factory com Decorador Único
    print("\n🏭 TESTE 5: FACTORY COM DECORATOR ÚNICO")
    print("-" * 50)
    
    decorated_review = ReviewDecoratorFactory.create_decorated_review(
        reviews[0], ['statistics']
    )
    factory_data = decorated_review.get_enhanced_data()
    
    print(f"📖 Livro: {factory_data['book_title']}")
    print(f"📊 Estatísticas aplicadas: {factory_data['word_count']} palavras, {factory_data['character_count']} caracteres")
    
    # 6. TESTE: Comparação entre Decoradores
    print("\n🔄 TESTE 6: COMPARAÇÃO ENTRE DECORATORS")
    print("-" * 50)
    
    print("📋 DADOS ORIGINAIS vs DECORATORS:")
    print("-" * 30)
    
    original_review = reviews[0]
    print(f"Original: {original_review.book_title} - Rating: {original_review.rating}")
    
    # Aplicar diferentes decoradores
    decorators = [
        ('Tempo de Leitura', ReviewWithReadingTime),
        ('Análise de Sentimento', ReviewWithSentimentAnalysis),
        ('Recomendação', ReviewWithRecommendation),
        ('Estatísticas', ReviewWithStatistics)
    ]
    
    for name, decorator_class in decorators:
        decorated = decorator_class(original_review)
        data = decorated.get_enhanced_data()
        
        print(f"\n{name}:")
        print(f"  - Dados básicos: {data['book_title']} (Rating: {data['rating']})")
        
        # Mostrar campos específicos de cada decorador
        if 'reading_status' in data:
            print(f"  - Status: {data['reading_status']}")
        if 'sentiment' in data:
            print(f"  - Sentimento: {data['sentiment']}")
        if 'recommendation' in data:
            print(f"  - Recomendação: {data['recommendation']}")
        if 'word_count' in data:
            print(f"  - Estatísticas: {data['word_count']} palavras")
    
    # 7. TESTE: Múltiplas Reviews com Diferentes Decoradores
    print("\n📚 TESTE 7: MÚLTIPLAS REVIEWS COM DIFERENTES DECORADORES")
    print("-" * 50)
    
    for i, review in enumerate(reviews[:3], 1):
        print(f"\n📖 REVIEW {i}: {review.book_title}")
        print("-" * 30)
        
        # Aplicar decorador de sentimento
        sentiment_decorator = ReviewWithSentimentAnalysis(review)
        sentiment_data = sentiment_decorator.get_enhanced_data()
        
        # Aplicar decorador de estatísticas
        stats_decorator = ReviewWithStatistics(review)
        stats_data = stats_decorator.get_enhanced_data()
        
        print(f"  Rating: {review.rating}")
        print(f"  Sentimento: {sentiment_data['sentiment']} (score: {sentiment_data['sentiment_score']})")
        print(f"  Palavras: {stats_data['word_count']}")
        print(f"  Texto: {review.text[:50]}...")
    
    print("\n✅ TODOS OS TESTES DO PADRÃO DECORATOR CONCLUÍDOS COM SUCESSO!")
    print("=" * 80)
    return True

if __name__ == "__main__":
    success = test_decorator_pattern_with_real_data()
    if success:
        print("🎉 Demonstração do padrão Decorator executada com sucesso!")
    else:
        print("❌ Falha na demonstração do padrão Decorator!")
