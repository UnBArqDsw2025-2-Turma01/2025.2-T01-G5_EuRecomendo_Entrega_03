from abc import ABC, abstractmethod
from typing import Dict, Any
from datetime import date, timedelta
from .models import Review


class ReviewDecorator(ABC):
    def __init__(self, review: Review):
        self._review = review
    
    @abstractmethod
    def get_enhanced_data(self) -> Dict[str, Any]:
        pass
    
    def get_original_review(self) -> Review:
        return self._review


class ReviewWithReadingTime(ReviewDecorator): 
    def get_enhanced_data(self) -> Dict[str, Any]:
        data = {
            'id': self._review.id,
            'book_title': self._review.book_title,
            'rating': self._review.rating,
            'text': self._review.text,
            'start_date': self._review.start_date,
            'end_date': self._review.end_date,
            'created_at': self._review.created_at,
            'updated_at': self._review.updated_at,
        }
        
        if self._review.start_date and self._review.end_date:
            reading_days = (self._review.end_date - self._review.start_date).days
            data['reading_days'] = reading_days
            data['reading_status'] = 'completed'
        elif self._review.start_date:
            days_since_start = (date.today() - self._review.start_date).days
            data['days_since_start'] = days_since_start
            data['reading_status'] = 'in_progress'
        else:
            data['reading_status'] = 'not_started'
        
        return data


class ReviewWithSentimentAnalysis(ReviewDecorator):
    def get_enhanced_data(self) -> Dict[str, Any]:
        data = {
            'id': self._review.id,
            'book_title': self._review.book_title,
            'rating': self._review.rating,
            'text': self._review.text,
            'start_date': self._review.start_date,
            'end_date': self._review.end_date,
            'created_at': self._review.created_at,
            'updated_at': self._review.updated_at,
        }
        
        sentiment = self._analyze_sentiment(self._review.text)
        data['sentiment'] = sentiment
        data['sentiment_score'] = self._calculate_sentiment_score(sentiment)
        
        return data
    
    def _analyze_sentiment(self, text: str) -> str:
        if not text:
            return 'neutral'
        
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
    
    def _calculate_sentiment_score(self, sentiment: str) -> float:
        sentiment_scores = {
            'positive': 1.0,
            'neutral': 0.0,
            'negative': -1.0
        }
        return sentiment_scores.get(sentiment, 0.0)


class ReviewWithRecommendation(ReviewDecorator):
    def get_enhanced_data(self) -> Dict[str, Any]:
        data = {
            'id': self._review.id,
            'book_title': self._review.book_title,
            'rating': self._review.rating,
            'text': self._review.text,
            'start_date': self._review.start_date,
            'end_date': self._review.end_date,
            'created_at': self._review.created_at,
            'updated_at': self._review.updated_at,
        }
        
        data['recommendation'] = self._generate_recommendation()
        data['recommendation_strength'] = self._calculate_recommendation_strength()
        
        return data
    
    def _generate_recommendation(self) -> str:
        if self._review.rating >= 4:
            return 'highly_recommended'
        elif self._review.rating == 3:
            return 'moderately_recommended'
        else:
            return 'not_recommended'
    
    def _calculate_recommendation_strength(self) -> float:
        return self._review.rating / 5.0


class ReviewWithStatistics(ReviewDecorator):
    def get_enhanced_data(self) -> Dict[str, Any]:
        data = {
            'id': self._review.id,
            'book_title': self._review.book_title,
            'rating': self._review.rating,
            'text': self._review.text,
            'start_date': self._review.start_date,
            'end_date': self._review.end_date,
            'created_at': self._review.created_at,
            'updated_at': self._review.updated_at,
        }
        
        data['word_count'] = len(self._review.text.split()) if self._review.text else 0
        data['character_count'] = len(self._review.text) if self._review.text else 0
        data['rating_percentage'] = (self._review.rating / 5.0) * 100
        data['is_recent'] = self._is_recent_review()
        
        return data
    
    def _is_recent_review(self) -> bool:
        if not self._review.created_at:
            return False
        
        thirty_days_ago = date.today() - timedelta(days=30)
        return self._review.created_at.date() >= thirty_days_ago


class ReviewDecoratorFactory:
    @staticmethod
    def create_decorated_review(review: Review, decorators: list) -> ReviewDecorator:
        decorated_review = review
        
        for decorator_name in decorators:
            if decorator_name == 'reading_time':
                decorated_review = ReviewWithReadingTime(decorated_review)
            elif decorator_name == 'sentiment':
                decorated_review = ReviewWithSentimentAnalysis(decorated_review)
            elif decorator_name == 'recommendation':
                decorated_review = ReviewWithRecommendation(decorated_review)
            elif decorator_name == 'statistics':
                decorated_review = ReviewWithStatistics(decorated_review)
        
        return decorated_review
