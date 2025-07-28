#!/bin/bash

# Script de instalação específico para RTX 5070 Ti
echo "🚀 Setup da API de Transcrição para RTX 5070 Ti"
echo "================================================="
echo "Este script instala o PyTorch Nightly com suporte à RTX 5070 Ti"
echo ""

# Verificar se está no ambiente virtual
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo "❌ Erro: Execute este script dentro do ambiente virtual"
    echo "💡 Use: source venv/bin/activate"
    exit 1
fi

# Desinstalar PyTorch anterior
echo "🗑️  Removendo versão anterior do PyTorch..."
pip uninstall torch torchvision torchaudio -y

# Instalar PyTorch Nightly com CUDA 12.8
echo "📦 Instalando PyTorch Nightly com CUDA 12.8..."
pip install --pre torch torchvision torchaudio --index-url https://download.pytorch.org/whl/nightly/cu128

# Verificar instalação
echo ""
echo "🔍 Verificando instalação..."
python -c "
import torch
print(f'✅ PyTorch version: {torch.__version__}')
print(f'✅ CUDA available: {torch.cuda.is_available()}')
print(f'✅ CUDA version: {torch.version.cuda}')
print(f'✅ GPU count: {torch.cuda.device_count()}')
if torch.cuda.is_available():
    print(f'✅ GPU name: {torch.cuda.get_device_name(0)}')
    # Teste simples de GPU
    x = torch.randn(1000, 1000).cuda()
    y = torch.randn(1000, 1000).cuda()
    z = torch.matmul(x, y)
    print('✅ Teste de GPU bem-sucedido!')
else:
    print('❌ GPU não disponível')
"

echo ""
echo "🎉 Instalação completa!"
echo "💡 Agora você pode usar ./run_with_gpu.sh para executar com aceleração GPU"