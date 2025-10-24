from abc import ABC, abstractmethod
from typing import List, Dict, Any
from datetime import date, timedelta
from .models import Review


class ReviewCalculationStrategy(ABC):
    """
    Interface abstrata para estratégias de cálculo de avaliação.
    Padrão Strategy para diferentes tipos de análise de avaliações.
    """
    
    @abstractmethod
    def calculate(self, reviews: List[Review]) -> Dict[str, Any]:
        pass


class BasicRatingStrategy(ReviewCalculationStrategy):
    def calculate(self, reviews: List[Review]) -> Dict[str, Any]:
        if not reviews:
            return {
                'total_reviews': 0,
                'average_rating': 0.0,
                'rating_distribution': {},
                'strategy_type': 'basic'
            }
        
        ratings = [review.rating for review in reviews]
        
        # Distribuição de avaliações
        distribution = {}
        for rating in range(1, 6):
            distribution[rating] = ratings.count(rating)
        
        return {
            'total_reviews': len(reviews),
            'average_rating': sum(ratings) / len(ratings),
            'rating_distribution': distribution,
            'highest_rating': max(ratings),
            'lowest_rating': min(ratings),
            'strategy_type': 'basic'
        }


class WeightedRatingStrategy(ReviewCalculationStrategy):
    def calculate(self, reviews: List[Review]) -> Dict[str, Any]:
        if not reviews:
            return {
                'total_reviews': 0,
                'weighted_average_rating': 0.0,
                'strategy_type': 'weighted'
            }
        
        weighted_sum = 0.0
        total_weight = 0.0
        
        for review in reviews:
            weight = self._calculate_weight(review)
            weighted_sum += review.rating * weight
            total_weight += weight
        
        weighted_average = weighted_sum / total_weight if total_weight > 0 else 0.0
        
        return {
            'total_reviews': len(reviews),
            'weighted_average_rating': weighted_average,
            'strategy_type': 'weighted'
        }
    
    def _calculate_weight(self, review: Review) -> float:
        """Calcula o peso de uma avaliação baseado em critérios"""
        weight = 1.0
        
        # Peso por avaliações recentes (avaliações mais recentes têm maior peso)
        if review.created_at:
            days_old = (date.today() - review.created_at.date()).days
            recency_factor = max(0.1, 1.0 - (days_old / 365.0))  # Decai ao longo de um ano
            weight *= recency_factor
        
        # Peso por presença de comentários em outras av
        if review.text and len(review.text.strip()) > 10:
            weight *= 1.5
        
        # Peso por período de leitura completo
        if review.start_date and review.end_date:
            weight *= 1.2
        
        return weight


class TimeBasedRatingStrategy(ReviewCalculationStrategy):
    def calculate(self, reviews: List[Review]) -> Dict[str, Any]:
        if not reviews:
            return {
                'total_reviews': 0,
                'strategy_type': 'time_based'
            }
        
        monthly_ratings = {}
        for review in reviews:
            if review.created_at:
                month_key = review.created_at.strftime('%Y-%m')
                if month_key not in monthly_ratings:
                    monthly_ratings[month_key] = []
                monthly_ratings[month_key].append(review.rating)
        
        # Calcula tendência temporal
        trend = self._calculate_trend(monthly_ratings)
        
        # Análise de sazonalidade
        seasonal_analysis = self._analyze_seasonality(reviews)
        
        return {
            'total_reviews': len(reviews),
            'monthly_ratings': monthly_ratings,
            'trend': trend,
            'seasonal_analysis': seasonal_analysis,
            'strategy_type': 'time_based'
        }
    
    def _calculate_trend(self, monthly_ratings: Dict[str, List[int]]) -> str:
        """Calcula a tendência das avaliações ao longo do tempo"""
        if len(monthly_ratings) < 2:
            return 'insufficient_data'
        
        sorted_months = sorted(monthly_ratings.keys())
        
        # média dos primeiros e últimos 3 meses
        first_half = []
        second_half = []
        
        for month in sorted_months[:3]:
            first_half.extend(monthly_ratings[month])
        
        for month in sorted_months[-3:]:
            second_half.extend(monthly_ratings[month])
        
        if not first_half or not second_half:
            return 'insufficient_data'
        
        first_avg = sum(first_half) / len(first_half)
        second_avg = sum(second_half) / len(second_half)
        
        if second_avg > first_avg + 0.5:
            return 'improving'
        elif second_avg < first_avg - 0.5:
            return 'declining'
        else:
            return 'stable'
    
    def _analyze_seasonality(self, reviews: List[Review]) -> Dict[str, Any]:
        """Analisa padrões sazonais nas avaliações"""
        monthly_averages = {}
        
        for review in reviews:
            if review.created_at:
                month = review.created_at.month
                if month not in monthly_averages:
                    monthly_averages[month] = []
                monthly_averages[month].append(review.rating)
        
        # média por mês
        for month in monthly_averages:
            monthly_averages[month] = sum(monthly_averages[month]) / len(monthly_averages[month])
        
        return {
            'monthly_averages': monthly_averages,
            'best_month': max(monthly_averages.keys(), key=lambda m: monthly_averages[m]) if monthly_averages else None,
            'worst_month': min(monthly_averages.keys(), key=lambda m: monthly_averages[m]) if monthly_averages else None
        }


class SentimentBasedRatingStrategy(ReviewCalculationStrategy):
    def calculate(self, reviews: List[Review]) -> Dict[str, Any]:
        if not reviews:
            return {
                'total_reviews': 0,
                'strategy_type': 'sentiment_based'
            }
        
        sentiment_analysis = []
        rating_sentiment_correlation = []
        
        for review in reviews:
            if review.text:
                sentiment = self._analyze_sentiment(review.text)
                sentiment_analysis.append(sentiment)
                rating_sentiment_correlation.append({
                    'rating': review.rating,
                    'sentiment': sentiment,
                    'text_length': len(review.text)
                })
        
        # Calcula correlação entre rating e sentimento
        correlation = self._calculate_correlation(rating_sentiment_correlation)
        
        return {
            'total_reviews': len(reviews),
            'reviews_with_text': len(sentiment_analysis),
            'sentiment_distribution': self._get_sentiment_distribution(sentiment_analysis),
            'rating_sentiment_correlation': correlation,
            'strategy_type': 'sentiment_based'
        }
    
    def _analyze_sentiment(self, text: str) -> str:
        """Análise simples de sentimento"""
        positive_words = ['excelente', 'ótimo', 'maravilhoso', 'fantástico', 'incrível', 
                         'adorei', 'recomendo', 'perfeito', 'amazing', 'wonderful']
        negative_words = ['ruim', 'péssimo', 'horrível', 'chato', 'entediante', 
                         'desperdício', 'terrível', 'awful', 'boring', 'disappointing']
        
        text_lower = text.lower()
        
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        if positive_count > negative_count:
            return 'positive'
        elif negative_count > positive_count:
            return 'negative'
        else:
            return 'neutral'
    
    def _get_sentiment_distribution(self, sentiments: List[str]) -> Dict[str, int]:
        """Calcula distribuição de sentimentos"""
        distribution = {'positive': 0, 'neutral': 0, 'negative': 0}
        for sentiment in sentiments:
            distribution[sentiment] += 1
        return distribution
    
    def _calculate_correlation(self, data: List[Dict]) -> Dict[str, Any]:
        """Calcula correlação entre rating e sentimento"""
        if not data:
            return {'correlation': 0.0, 'description': 'no_data'}
        
        # Mapeia sentimentos para valores numéricos
        sentiment_values = {'negative': -1, 'neutral': 0, 'positive': 1}
        
        ratings = [item['rating'] for item in data]
        sentiments = [sentiment_values[item['sentiment']] for item in data]
        
        # Correlação simples
        n = len(ratings)
        if n < 2:
            return {'correlation': 0.0, 'description': 'insufficient_data'}
        
        mean_rating = sum(ratings) / n
        mean_sentiment = sum(sentiments) / n
        
        numerator = sum((r - mean_rating) * (s - mean_sentiment) for r, s in zip(ratings, sentiments))
        denominator = (sum((r - mean_rating) ** 2 for r in ratings) * sum((s - mean_sentiment) ** 2 for s in sentiments)) ** 0.5
        
        correlation = numerator / denominator if denominator != 0 else 0.0
        
        return {
            'correlation': correlation,
            'description': self._interpret_correlation(correlation)
        }
    
    def _interpret_correlation(self, correlation: float) -> str:
        """Interpreta o valor da correlação"""
        if correlation > 0.7:
            return 'strong_positive'
        elif correlation > 0.3:
            return 'moderate_positive'
        elif correlation > -0.3:
            return 'weak'
        elif correlation > -0.7:
            return 'moderate_negative'
        else:
            return 'strong_negative'


class ReviewAnalysisContext:
    def __init__(self, strategy: ReviewCalculationStrategy):
        self._strategy = strategy
    
    def set_strategy(self, strategy: ReviewCalculationStrategy):
        """Altera a estratégia de cálculo"""
        self._strategy = strategy
    
    def analyze_reviews(self, reviews: List[Review]) -> Dict[str, Any]:
        """Executa a análise usando a estratégia atual"""
        return self._strategy.calculate(reviews)
    
    def get_strategy_type(self) -> str:
        """Retorna o tipo da estratégia atual"""
        return self._strategy.__class__.__name__


class ReviewAnalysisFactory:
    @staticmethod
    def create_basic_analysis() -> ReviewAnalysisContext:
        """Cria contexto com estratégia básica"""
        return ReviewAnalysisContext(BasicRatingStrategy())
    
    @staticmethod
    def create_weighted_analysis() -> ReviewAnalysisContext:
        """Cria contexto com estratégia ponderada"""
        return ReviewAnalysisContext(WeightedRatingStrategy())
    
    @staticmethod
    def create_time_based_analysis() -> ReviewAnalysisContext:
        """Cria contexto com estratégia baseada em tempo"""
        return ReviewAnalysisContext(TimeBasedRatingStrategy())
    
    @staticmethod
    def create_sentiment_analysis() -> ReviewAnalysisContext:
        """Cria contexto com estratégia baseada em sentimento"""
        return ReviewAnalysisContext(SentimentBasedRatingStrategy())
