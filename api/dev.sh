#!/bin/bash

# Script de desenvolvimento com hot reload
echo "🔥 Iniciando API em modo desenvolvimento (Hot Reload)"
echo "📁 Monitorando diretórios: src/, main.py"
echo "⚡ Modificações nos arquivos irão recarregar automaticamente"
echo ""

# Verifica se está no diretório correto
if [[ ! -f "main.py" ]]; then
    echo "❌ Execute este script do diretório api/"
    exit 1
fi

# Verifica se uvicorn está instalado
if ! python -c "import uvicorn" 2>/dev/null; then
    echo "📦 Instalando uvicorn..."
    pip install uvicorn[standard]
fi

# Inicia com hot reload
uvicorn main:app \
    --host 0.0.0.0 \
    --port 8000 \
    --reload \
    --reload-dir src/ \
    --reload-dir ./ \
    --reload-exclude "*.pyc" \
    --reload-exclude "__pycache__" \
    --reload-exclude "*.log" \
    --reload-exclude "venv/" \
    --reload-exclude ".env" \
    --log-level info