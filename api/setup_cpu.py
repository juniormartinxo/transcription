#!/usr/bin/env python3
"""
Script para configurar ambiente para CPU e corrigir problemas
"""
import os
import sys
from pathlib import Path

def setup_cpu_environment():
    """Configura o ambiente para usar CPU"""
    print("🔧 Configurando ambiente para CPU...")
    
    # Configurar variáveis de ambiente para CPU
    os.environ['FORCE_CPU'] = 'true'
    os.environ['CUDA_VISIBLE_DEVICES'] = ''
    
    # Configurar diretórios locais
    os.environ['AUDIOS_DIR'] = './public/audios'
    os.environ['TRANSCRIPTIONS_DIR'] = './public/transcriptions'
    os.environ['LOG_FILE'] = './logs/app.log'
    
    print("✅ Ambiente configurado para CPU")

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
        
        # Verificar se FORCE_CPU está configurado
        if 'FORCE_CPU=true' not in content:
            print("⚠️  Adicionando FORCE_CPU=true ao .env")
            with open(env_file, 'a') as f:
                f.write("\nFORCE_CPU=true\n")
        else:
            print("✅ FORCE_CPU já configurado")
    else:
        print("📝 Criando arquivo .env...")
        env_content = """# Configurações da API de Transcrição
HUGGING_FACE_HUB_TOKEN=seu_token_aqui
VERSION_MODEL=turbo
FORCE_CPU=true
AUDIOS_DIR=./public/audios
TRANSCRIPTIONS_DIR=./public/transcriptions
LOG_LEVEL=INFO
LOG_FILE=./logs/app.log
"""
        with open(env_file, 'w') as f:
            f.write(env_content)
        print("✅ Arquivo .env criado")

def run_application():
    """Executa a aplicação"""
    print("🚀 Iniciando aplicação com CPU...")
    
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
    print("🔧 Setup da API de Transcrição para CPU")
    print("=" * 40)
    
    # Configurações
    setup_cpu_environment()
    create_directories()
    check_env_file()
    
    print("\n" + "=" * 40)
    print("✅ Setup concluído!")
    print("⚠️  Lembre-se de configurar o HUGGING_FACE_HUB_TOKEN no arquivo .env")
    print("💡 Usando CPU para evitar problemas de CUDA")
    print("=" * 40)
    
    # Executar aplicação
    run_application()

if __name__ == "__main__":
    main() 