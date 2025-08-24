#!/bin/bash

echo "🐍 Ativando ambiente virtual..."

# Verificar se o ambiente virtual existe
if [ ! -d "venv" ]; then
    echo "❌ Ambiente virtual não encontrado"
    echo "📦 Execute primeiro: ./setup_venv.sh"
    exit 1
fi

# Ativar ambiente virtual
source venv/bin/activate

echo "✅ Ambiente virtual ativado"
echo "🐍 Python: $(which python)"
echo "📦 Pip: $(which pip)"

# Mostrar opções
echo ""
echo "🚀 Opções disponíveis:"
echo "   1. python main.py                    # Executar aplicação"
echo "   2. python -m uvicorn main:app --reload  # Executar com reload"
echo "   3. pip install -r requirements.txt   # Instalar dependências"
echo "   4. deactivate                        # Desativar ambiente virtual"
echo ""
echo "💡 Dica: Use 'python run_venv.py' para execução automática" 