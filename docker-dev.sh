#!/bin/bash

# Script para iniciar aplicação em modo desenvolvimento com hot reload

echo "🐳 Iniciando aplicação em modo desenvolvimento (Hot Reload)"
echo "📁 Volumes de código mapeados para hot reload"
echo "⚡ Modificações no código irão recarregar automaticamente"
echo ""

# Verificar se .env existe
if [[ ! -f ".env" ]]; then
    echo "⚠️  Arquivo .env não encontrado!"
    echo "📝 Criando arquivo .env com configurações padrão..."
    
    cat > .env << 'EOF'
# Configurações da API de Transcrição
HUGGING_FACE_HUB_TOKEN=seu_token_aqui
VERSION_MODEL=turbo
FORCE_CPU=true
LOG_LEVEL=INFO

# Docker - IDs de usuário para evitar problemas de permissão
USER_ID=1000
GROUP_ID=1000
EOF
    
    echo "✅ Arquivo .env criado"
    echo "⚠️  IMPORTANTE: Configure seu token do HuggingFace no arquivo .env"
    echo "   Obtenha o token em: https://huggingface.co/settings/tokens"
    echo ""
fi

# Parar containers existentes se estiverem rodando
echo "🛑 Parando containers existentes..."
docker-compose -f docker-compose.dev.yml down

# Construir e iniciar em modo desenvolvimento
echo "🏗️  Construindo e iniciando containers de desenvolvimento..."
docker-compose -f docker-compose.dev.yml up --build

echo ""
echo "🎉 Aplicação iniciada em modo desenvolvimento!"
echo "📝 URLs:"
echo "   Backend:  http://localhost:8000"
echo "   Docs API: http://localhost:8000/docs"
echo "   Frontend: http://localhost:3000"
echo ""
echo "💡 Hot Reload ativo:"
echo "   - Modificações em api/src/ recarregam o backend automaticamente"
echo "   - Modificações em frontend/src/ recarregam o frontend automaticamente"
echo ""
echo "⏹️  Para parar: Ctrl+C ou execute: docker-compose -f docker-compose.dev.yml down"