#!/usr/bin/env python3
"""
Script para configurar ambiente para GPU (RTX 5070 Ti)
"""
import os
import sys
import subprocess
from pathlib import Path

def check_gpu():
    """Verifica se a GPU está disponível"""
    try:
        import torch
        if torch.cuda.is_available():
            print(f"✅ GPU detectada: {torch.cuda.get_device_name()}")
            print(f"✅ CUDA version: {torch.version.cuda}")
            print(f"✅ PyTorch version: {torch.__version__}")
            return True
        else:
            print("❌ GPU não detectada")
            return False
    except ImportError:
        print("❌ PyTorch não instalado")
        return False

def install_pytorch_gpu():
    """Instala PyTorch com suporte a GPU"""
    print("📦 Instalando PyTorch com suporte a GPU...")
    
    try:
        # Desinstalar versão atual do PyTorch
        subprocess.run([sys.executable, "-m", "pip", "uninstall", "torch", "torchaudio", "-y"], check=True)
        
        # Instalar PyTorch com CUDA 12.1 (compatível com RTX 5070 Ti)
        subprocess.run([
            sys.executable, "-m", "pip", "install", 
            "torch", "torchaudio", "--index-url", "https://download.pytorch.org/whl/cu121"
        ], check=True)
        
        print("✅ PyTorch com GPU instalado")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro ao instalar PyTorch: {e}")
        return False

def setup_gpu_environment():
    """Configura o ambiente para usar GPU"""
    print("🔧 Configurando ambiente para GPU...")
    
    # Configurar variáveis de ambiente para GPU
    os.environ['FORCE_CPU'] = 'false'
    os.environ['CUDA_VISIBLE_DEVICES'] = '0'
    
    # Configurar diretórios locais
    os.environ['AUDIOS_DIR'] = './public/audios'
    os.environ['TRANSCRIPTIONS_DIR'] = './public/transcriptions'
    os.environ['LOG_FILE'] = './logs/app.log'
    
    print("✅ Ambiente configurado para GPU")

def create_directories():
    """Cria diretórios necessários"""
    directories = [
        "public/audios",
        "public/transcriptions", 
        "logs"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✅ Diretório criado: {directory}")

def check_env_file():
    """Verifica e atualiza arquivo .env"""
    env_file = Path(".env")
    
    if env_file.exists():
        # Ler conteúdo atual
        with open(env_file, 'r') as f:
            content = f.read()
        
        # Atualizar FORCE_CPU para false
        if 'FORCE_CPU=true' in content:
            content = content.replace('FORCE_CPU=true', 'FORCE_CPU=false')
            with open(env_file, 'w') as f:
                f.write(content)
            print("✅ FORCE_CPU configurado para false")
        else:
            print("✅ FORCE_CPU já configurado para GPU")
    else:
        print("📝 Criando arquivo .env...")
        env_content = """# Configurações da API de Transcrição
HUGGING_FACE_HUB_TOKEN=seu_token_aqui
VERSION_MODEL=turbo
FORCE_CPU=false
AUDIOS_DIR=./public/audios
TRANSCRIPTIONS_DIR=./public/transcriptions
LOG_LEVEL=INFO
LOG_FILE=./logs/app.log
"""
        with open(env_file, 'w') as f:
            f.write(env_content)
        print("✅ Arquivo .env criado")

def test_gpu():
    """Testa se a GPU está funcionando"""
    print("🧪 Testando GPU...")
    
    try:
        import torch
        
        # Teste básico de GPU
        if torch.cuda.is_available():
            device = torch.device("cuda")
            x = torch.randn(3, 3).to(device)
            y = torch.randn(3, 3).to(device)
            z = torch.mm(x, y)
            print("✅ Teste de GPU bem-sucedido!")
            return True
        else:
            print("❌ GPU não disponível para teste")
            return False
    except Exception as e:
        print(f"❌ Erro no teste de GPU: {e}")
        return False

def run_application():
    """Executa a aplicação"""
    print("🚀 Iniciando aplicação com GPU...")
    
    try:
        # Importar e executar a aplicação
        from main import app
        import uvicorn
        
        print("🌐 Servidor iniciado em: http://localhost:8000")
        print("📚 Documentação: http://localhost:8000/docs")
        print("🔍 Health check: http://localhost:8000/health")
        print("⏹️  Para parar: Ctrl+C")
        
        uvicorn.run(
            app, 
            host="0.0.0.0", 
            port=8000, 
            reload=True,
            log_level="info"
        )
        
    except ImportError as e:
        print(f"❌ Erro ao importar aplicação: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n👋 Aplicação encerrada")
    except Exception as e:
        print(f"❌ Erro ao executar aplicação: {e}")
        sys.exit(1)

def main():
    """Função principal"""
    print("🚀 Setup da API de Transcrição para GPU")
    print("=" * 40)
    
    # Verificar GPU atual
    if not check_gpu():
        print("📦 Instalando PyTorch com suporte a GPU...")
        if not install_pytorch_gpu():
            print("❌ Falha ao instalar PyTorch com GPU")
            print("💡 Tente executar: python3 setup_cpu.py")
            sys.exit(1)
    
    # Testar GPU
    if not test_gpu():
        print("⚠️  GPU não está funcionando corretamente")
        print("💡 Tente executar: python3 setup_cpu.py")
        sys.exit(1)
    
    # Configurações
    setup_gpu_environment()
    create_directories()
    check_env_file()
    
    print("\n" + "=" * 40)
    print("✅ Setup concluído!")
    print("⚠️  Lembre-se de configurar o HUGGING_FACE_HUB_TOKEN no arquivo .env")
    print("🚀 Usando GPU para melhor performance")
    print("=" * 40)
    
    # Executar aplicação
    run_application()

if __name__ == "__main__":
    main() 