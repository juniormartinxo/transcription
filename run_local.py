#!/usr/bin/env python3
"""
Script para rodar a aplicação localmente sem Docker
"""
import os
import sys
import subprocess
from pathlib import Path

def check_python_version():
    """Verifica se a versão do Python é compatível"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ é necessário")
        sys.exit(1)
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detectado")

def create_directories():
    """Cria os diretórios necessários"""
    directories = [
        "public/audios",
        "public/transcriptions", 
        "logs"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✅ Diretório criado: {directory}")

def install_dependencies():
    """Instala as dependências Python"""
    print("📦 Instalando dependências...")
    
    try:
        subprocess.run([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
        ], check=True)
        print("✅ Dependências instaladas com sucesso")
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro ao instalar dependências: {e}")
        sys.exit(1)

def check_ffmpeg():
    """Verifica se o FFmpeg está instalado"""
    try:
        subprocess.run(["ffmpeg", "-version"], 
                      capture_output=True, check=True)
        print("✅ FFmpeg encontrado")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ FFmpeg não encontrado")
        print("📋 Instale o FFmpeg:")
        print("   Ubuntu/Debian: sudo apt install ffmpeg")
        print("   macOS: brew install ffmpeg")
        print("   Windows: https://ffmpeg.org/download.html")
        sys.exit(1)

def check_env_file():
    """Verifica se o arquivo .env existe"""
    env_file = Path(".env")
    if not env_file.exists():
        print("⚠️  Arquivo .env não encontrado")
        print("📝 Criando arquivo .env com configurações padrão...")
        
        env_content = """# Configurações da API de Transcrição
HUGGING_FACE_HUB_TOKEN=seu_token_aqui
VERSION_MODEL=turbo
FORCE_CPU=true
AUDIOS_DIR=./public/audios
TRANSCRIPTIONS_DIR=./public/transcriptions
LOG_LEVEL=INFO
"""
        
        with open(".env", "w") as f:
            f.write(env_content)
        
        print("✅ Arquivo .env criado")
        print("⚠️  IMPORTANTE: Configure seu token do HuggingFace no arquivo .env")
        print("   Obtenha o token em: https://huggingface.co/settings/tokens")
    else:
        print("✅ Arquivo .env encontrado")

def run_application():
    """Executa a aplicação"""
    print("🚀 Iniciando aplicação...")
    
    # Configurar variáveis de ambiente para desenvolvimento local
    os.environ.setdefault("AUDIOS_DIR", "./public/audios")
    os.environ.setdefault("TRANSCRIPTIONS_DIR", "./public/transcriptions")
    os.environ.setdefault("LOG_FILE", "./logs/app.log")
    
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
    print("🎵 Setup da API de Transcrição Local")
    print("=" * 40)
    
    # Verificações e setup
    check_python_version()
    create_directories()
    install_dependencies()
    check_ffmpeg()
    check_env_file()
    
    print("\n" + "=" * 40)
    print("✅ Setup concluído!")
    print("⚠️  Lembre-se de configurar o HUGGING_FACE_HUB_TOKEN no arquivo .env")
    print("=" * 40)
    
    # Executar aplicação
    run_application()

if __name__ == "__main__":
    main() 