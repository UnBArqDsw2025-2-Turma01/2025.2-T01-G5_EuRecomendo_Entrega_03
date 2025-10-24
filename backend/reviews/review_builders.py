from datetime import date
from typing import Optional
from .models import Review


class ReviewBuilder:
    def __init__(self):
        self._review_data = {}
    
    def set_book_title(self, title: str) -> 'ReviewBuilder':
        self._review_data['book_title'] = title
        return self
    
    def set_rating(self, rating: int) -> 'ReviewBuilder':
        if not 1 <= rating <= 5:
            raise ValueError("Avaliação deve estar entre 1 e 5 estrelas")
        self._review_data['rating'] = rating
        return self
    
    def set_comment(self, comment: str) -> 'ReviewBuilder':
        self._review_data['text'] = comment
        return self
    
    def set_reading_period(self, start_date: date, end_date: date) -> 'ReviewBuilder':
        if start_date and end_date and start_date > end_date:
            raise ValueError("Data de início não pode ser posterior à data de fim")
        
        self._review_data['start_date'] = start_date
        self._review_data['end_date'] = end_date
        return self
    
    def set_start_date(self, start_date: date) -> 'ReviewBuilder':
        self._review_data['start_date'] = start_date
        return self
    
    def set_end_date(self, end_date: date) -> 'ReviewBuilder':
        self._review_data['end_date'] = end_date
        return self
    
    def build(self) -> Review:
        if 'book_title' not in self._review_data:
            raise ValueError("Título do livro é obrigatório")
        
        if 'rating' not in self._review_data:
            raise ValueError("Avaliação é obrigatória")
        
        return Review.objects.create(**self._review_data)
    
    def reset(self) -> 'ReviewBuilder':
        self._review_data = {}
        return self


class ReviewDirector:
    def __init__(self, builder: ReviewBuilder):
        self._builder = builder
    
    def build_quick_review(self, book_title: str, rating: int) -> Review:
        return (self._builder
                .reset()
                .set_book_title(book_title)
                .set_rating(rating)
                .build())
    
    def build_detailed_review(self, book_title: str, rating: int, 
                            comment: str, start_date: date, end_date: date) -> Review:
        return (self._builder
                .reset()
                .set_book_title(book_title)
                .set_rating(rating)
                .set_comment(comment)
                .set_reading_period(start_date, end_date)
                .build())
    
    def build_reading_in_progress(self, book_title: str, rating: int, 
                                comment: str, start_date: date) -> Review:
        return (self._builder
                .reset()
                .set_book_title(book_title)
                .set_rating(rating)
                .set_comment(comment)
                .set_start_date(start_date)
                .build())
