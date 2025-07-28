#!/bin/bash

echo "🔧 Corrigindo permissões e cache..."

# Corrigir permissões dos diretórios
echo "📁 Corrigindo permissões dos diretórios..."
chmod -R 755 public/
chmod -R 755 logs/

# Criar diretórios se não existirem
mkdir -p public/audios public/transcriptions logs

# Corrigir permissões específicas
chmod 777 public/audios
chmod 777 public/transcriptions
chmod 777 logs

# Limpar cache do HuggingFace se existir
if [ -d "~/.cache/huggingface" ]; then
    echo "🗑️  Limpando cache do HuggingFace..."
    rm -rf ~/.cache/huggingface
fi

# Limpar cache local se existir
if [ -d ".cache" ]; then
    echo "🗑️  Limpando cache local..."
    rm -rf .cache
fi

# Verificar se o arquivo tasks.json existe e corrigir permissões
if [ -f "public/transcriptions/tasks.json" ]; then
    echo "📄 Corrigindo permissões do tasks.json..."
    chmod 666 public/transcriptions/tasks.json
fi

echo "✅ Permissões corrigidas!"
echo ""
echo "🚀 Agora execute:"
echo "   python3 run_venv.py"
echo ""
echo "💡 Dica: Configure FORCE_CPU=true no arquivo .env" 