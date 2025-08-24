#!/bin/bash

echo "🎵 Setup da API de Transcrição Local"
echo "======================================"

# Verificar Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 não encontrado"
    exit 1
fi

echo "✅ Python 3 encontrado"

# Verificar FFmpeg
if ! command -v ffmpeg &> /dev/null; then
    echo "❌ FFmpeg não encontrado"
    echo "📋 Instale o FFmpeg:"
    echo "   Ubuntu/Debian: sudo apt install ffmpeg"
    echo "   macOS: brew install ffmpeg"
    exit 1
fi

echo "✅ FFmpeg encontrado"

# Criar diretórios
echo "📁 Criando diretórios..."
mkdir -p public/audios public/transcriptions logs

# Instalar dependências
echo "📦 Instalando dependências..."
pip3 install -r requirements.txt

# Criar arquivo .env se não existir
if [ ! -f .env ]; then
    echo "📝 Criando arquivo .env..."
    cat > .env << EOF
# Configurações da API de Transcrição
HUGGING_FACE_HUB_TOKEN=seu_token_aqui
VERSION_MODEL=turbo
FORCE_CPU=true
AUDIOS_DIR=./public/audios
TRANSCRIPTIONS_DIR=./public/transcriptions
LOG_LEVEL=INFO
LOG_FILE=./logs/app.log
EOF
    echo "⚠️  IMPORTANTE: Configure seu token do HuggingFace no arquivo .env"
    echo "   Obtenha o token em: https://huggingface.co/settings/tokens"
else
    echo "✅ Arquivo .env encontrado"
fi

echo ""
echo "✅ Setup concluído!"
echo "🚀 Para executar: python3 main.py"
echo "📚 Documentação: http://localhost:8000/docs" 