#!/bin/bash

# Script para testar a API de Reviews
# Execute este script após subir os containers e obter o token JWT

echo "🚀 TESTANDO API DE REVIEWS"
echo "=========================="

# Verificar se o TOKEN foi definido
if [ -z "$TOKEN" ]; then
    echo "❌ Erro: Variável TOKEN não definida"
    echo "Execute primeiro: TOKEN=\"<seu_token_aqui>\""
    exit 1
fi

BASE_URL="http://localhost:8000/api/reviews"
AUTH_HEADER="Authorization: Bearer $TOKEN"

echo "📝 Teste 1: Criando review básica..."
curl -X POST $BASE_URL/ \
  -H "Content-Type: application/json" \
  -H "$AUTH_HEADER" \
  -d '{
    "book_title": "Clean Code",
    "rating": 5,
    "text": "Excelente livro sobre programação limpa!"
  }' | jq '.'

echo -e "\n📝 Teste 2: Criando review com período de leitura..."
curl -X POST $BASE_URL/ \
  -H "Content-Type: application/json" \
  -H "$AUTH_HEADER" \
  -d '{
    "book_title": "The Pragmatic Programmer",
    "rating": 4,
    "text": "Livro fundamental para desenvolvedores",
    "start_date": "2024-01-01",
    "end_date": "2024-01-15"
  }' | jq '.'

echo -e "\n📝 Teste 3: Criando review em progresso..."
curl -X POST $BASE_URL/ \
  -H "Content-Type: application/json" \
  -H "$AUTH_HEADER" \
  -d '{
    "book_title": "Design Patterns",
    "rating": 3,
    "text": "Ainda lendo...",
    "start_date": "2024-02-01"
  }' | jq '.'

echo -e "\n📝 Teste 4: Listando todas as reviews..."
curl -X GET $BASE_URL/ \
  -H "$AUTH_HEADER" | jq '.'

echo -e "\n📝 Teste 5: Testando validação - rating inválido (deve falhar)..."
curl -X POST $BASE_URL/ \
  -H "Content-Type: application/json" \
  -H "$AUTH_HEADER" \
  -d '{
    "book_title": "Test Book",
    "rating": 6
  }' | jq '.'

echo -e "\n📝 Teste 6: Testando validação - dados obrigatórios faltando (deve falhar)..."
curl -X POST $BASE_URL/ \
  -H "Content-Type: application/json" \
  -H "$AUTH_HEADER" \
  -d '{
    "book_title": "Test Book"
  }' | jq '.'

echo -e "\n✅ Testes da API concluídos!"
echo "Acesse http://localhost:8000/admin para ver as reviews no Django Admin"

