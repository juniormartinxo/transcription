#!/bin/bash

echo "🛑 Parando containers de desenvolvimento..."
docker-compose -f docker-compose.dev.yml down

echo "🧹 Limpando containers não utilizados..."
docker container prune -f

echo "✅ Containers de desenvolvimento parados"