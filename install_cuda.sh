#!/bin/bash

echo "🚀 Instalando CUDA Toolkit para RTX 5070 Ti"
echo "============================================="

# Verificar se CUDA já está instalado
if command -v nvcc &> /dev/null; then
    echo "✅ CUDA já está instalado"
    nvcc --version
else
    echo "📦 CUDA não encontrado, instalando..."
    
    # Adicionar repositório NVIDIA
    wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2204/x86_64/cuda-keyring_1.1-1_all.deb
    sudo dpkg -i cuda-keyring_1.1-1_all.deb
    sudo apt-get update
    
    # Instalar CUDA toolkit
    sudo apt-get install cuda-toolkit-12-1
    
    echo "✅ CUDA Toolkit instalado"
fi

# Verificar drivers NVIDIA
if command -v nvidia-smi &> /dev/null; then
    echo "✅ Drivers NVIDIA encontrados"
    nvidia-smi
else
    echo "⚠️  Drivers NVIDIA não encontrados"
    echo "📋 Instale os drivers:"
    echo "   sudo apt install nvidia-driver-535"
fi

echo ""
echo "🔧 Agora execute:"
echo "   python3 setup_gpu.py" 