#!/bin/bash

# Script para inicializar o ambiente Docker da aplicação de transcrição

set -e  # Sair em caso de erro

echo "🚀 Iniciando aplicação de transcrição com Docker..."

# Verificar se arquivo .env existe
if [ ! -f ".env" ]; then
    echo "⚠️  Arquivo .env não encontrado!"
    echo "📋 Copiando .env.example para .env..."
    cp .env.example .env
    echo "✏️  Por favor, edite o arquivo .env e adicione seu HUGGING_FACE_HUB_TOKEN"
    echo "💡 Você pode obter o token em: https://huggingface.co/settings/tokens"
    exit 1
fi

# Verificar se HUGGING_FACE_HUB_TOKEN está definido
if ! grep -q "HUGGING_FACE_HUB_TOKEN=hf_" .env 2>/dev/null; then
    echo "⚠️  HUGGING_FACE_HUB_TOKEN não está configurado no arquivo .env"
    echo "💡 Edite o arquivo .env e adicione seu token do Hugging Face"
    exit 1
fi

# Criar diretórios necessários
echo "📁 Criando diretórios necessários..."
mkdir -p public/audios public/transcriptions public/videos logs

# Parar containers existentes se estiverem rodando
echo "🛑 Parando containers existentes..."
docker compose down 2>/dev/null || true

# Construir e iniciar os serviços
echo "🔨 Construindo e iniciando os containers..."
docker compose up --build -d

# Aguardar os serviços ficarem prontos
echo "⏳ Aguardando serviços ficarem prontos..."
echo "   Backend (FastAPI): http://localhost:8000"
echo "   Frontend (Next.js): http://localhost:3000"

# Função para verificar se um serviço está respondendo
check_service() {
    local url=$1
    local name=$2
    local max_attempts=30
    local attempt=1

    echo -n "🔍 Verificando $name"
    while [ $attempt -le $max_attempts ]; do
        if curl -s -f "$url" > /dev/null 2>&1; then
            echo " ✅"
            return 0
        fi
        echo -n "."
        sleep 2
        ((attempt++))
    done
    echo " ❌"
    return 1
}

# Verificar se os serviços estão respondendo
if check_service "http://localhost:8000/health" "Backend"; then
    echo "🎯 Backend está funcionando!"
else
    echo "❌ Backend não respondeu a tempo"
fi

if check_service "http://localhost:3000/api/health" "Frontend"; then
    echo "🎯 Frontend está funcionando!"
else
    echo "❌ Frontend não respondeu a tempo"
fi

echo ""
echo "🎉 Aplicação iniciada com sucesso!"
echo "📱 Frontend: http://localhost:3000"
echo "🔧 API Backend: http://localhost:8000"
echo "📖 Documentação da API: http://localhost:8000/docs"
echo ""
echo "📝 Comandos úteis:"
echo "   docker compose logs -f          # Ver logs em tempo real"
echo "   docker compose logs backend     # Ver logs do backend"
echo "   docker compose logs frontend    # Ver logs do frontend"
echo "   docker compose down            # Parar os containers"
echo "   docker compose restart         # Reiniciar os containers"