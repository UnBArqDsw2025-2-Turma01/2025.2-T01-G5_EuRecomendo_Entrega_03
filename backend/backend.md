# Backend (Django)

Esta pasta contém o esqueleto (scaffold) do backend Django para o projeto EuRecomendo.

Início rápido (usando Docker):

1. Construir e iniciar os serviços:

```bash
docker compose up --build
```

2. Criar e aplicar as migrações (em outro terminal):

```bash
docker compose exec web python manage.py migrate
```

3. Criar um superusuário:

```bash
docker compose exec web python manage.py createsuperuser
```

Exemplos de endpoints da API:

- /api/users/
- /api/profiles/
- /api/books/
- /api/reviews/
- /api/recommender/recommend/
- /api/library/