#!/usr/bin/env python3
"""
Script para rodar a aplicação com ambiente virtual
"""
import os
import sys
import subprocess
import venv
from pathlib import Path

def check_venv():
    """Verifica se o ambiente virtual existe"""
    venv_path = Path("venv")
    if not venv_path.exists():
        print("🐍 Ambiente virtual não encontrado")
        print("📦 Criando ambiente virtual...")
        venv.create("venv", with_pip=True)
        print("✅ Ambiente virtual criado")
    else:
        print("✅ Ambiente virtual encontrado")

def get_venv_python():
    """Retorna o caminho do Python do ambiente virtual"""
    if sys.platform == "win32":
        return "venv/Scripts/python.exe"
    else:
        return "venv/bin/python"

def get_venv_pip():
    """Retorna o caminho do pip do ambiente virtual"""
    if sys.platform == "win32":
        return "venv/Scripts/pip.exe"
    else:
        return "venv/bin/pip"

def install_dependencies():
    """Instala as dependências no ambiente virtual"""
    print("📦 Instalando dependências no ambiente virtual...")
    
    pip_path = get_venv_pip()
    
    try:
        # Atualizar pip
        subprocess.run([pip_path, "install", "--upgrade", "pip"], check=True)
        
        # Instalar dependências
        subprocess.run([pip_path, "install", "-r", "requirements.txt"], check=True)
        print("✅ Dependências instaladas com sucesso")
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro ao instalar dependências: {e}")
        sys.exit(1)

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
LOG_FILE=./logs/app.log
"""
        
        with open(".env", "w") as f:
            f.write(env_content)
        
        print("✅ Arquivo .env criado")
        print("⚠️  IMPORTANTE: Configure seu token do HuggingFace no arquivo .env")
        print("   Obtenha o token em: https://huggingface.co/settings/tokens")
    else:
        print("✅ Arquivo .env encontrado")

def run_application():
    """Executa a aplicação usando o Python do ambiente virtual"""
    print("🚀 Iniciando aplicação...")
    
    python_path = get_venv_python()
    
    # Configurar variáveis de ambiente para desenvolvimento local
    os.environ.setdefault("AUDIOS_DIR", "./public/audios")
    os.environ.setdefault("TRANSCRIPTIONS_DIR", "./public/transcriptions")
    os.environ.setdefault("LOG_FILE", "./logs/app.log")
    
    try:
        print("🌐 Servidor iniciado em: http://localhost:8000")
        print("📚 Documentação: http://localhost:8000/docs")
        print("🔍 Health check: http://localhost:8000/health")
        print("⏹️  Para parar: Ctrl+C")
        
        # Executar a aplicação usando o Python do venv com uvicorn e hot reload
        subprocess.run([
            python_path, "-m", "uvicorn", "main:app",
            "--host", "0.0.0.0",
            "--port", "8000",
            "--reload",
            "--reload-dir", "src/",
            "--reload-dir", "./",
            "--reload-exclude", "*.pyc",
            "--reload-exclude", "__pycache__",
            "--reload-exclude", "*.log",
            "--reload-exclude", "venv/",
            "--reload-exclude", ".env"
        ])
        
    except KeyboardInterrupt:
        print("\n👋 Aplicação encerrada")
    except Exception as e:
        print(f"❌ Erro ao executar aplicação: {e}")
        sys.exit(1)

def main():
    """Função principal"""
    print("🐍 Setup da API de Transcrição com Ambiente Virtual")
    print("=" * 50)
    
    # Verificações e setup
    check_venv()
    create_directories()
    install_dependencies()
    check_ffmpeg()
    check_env_file()
    
    print("\n" + "=" * 50)
    print("✅ Setup concluído!")
    print("⚠️  Lembre-se de configurar o HUGGING_FACE_HUB_TOKEN no arquivo .env")
    print("=" * 50)
    
    # Executar aplicação
    run_application()

if __name__ == "__main__":
    main() 