# Backend (Django)

This folder contains the Django backend scaffold for the EuRecomendo project.

Quick start (using Docker):

1. Build and start services:

   docker compose up --build

2. Create and apply migrations (in another terminal):

   docker compose exec web python manage.py migrate

3. Create a superuser:

   docker compose exec web python manage.py createsuperuser

API endpoints (examples):

- /api/users/
- /api/profiles/
- /api/books/
- /api/reviews/
- /api/recommender/recommend/
