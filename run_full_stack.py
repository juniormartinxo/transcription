#!/usr/bin/env python3
"""
Script para iniciar API e Frontend simultaneamente
Executa o backend (FastAPI) e frontend (Next.js) em processos paralelos
Usa ambiente virtual para o backend se disponível
"""

import os
import subprocess
import sys
import time
import signal
from typing import List, Optional
from pathlib import Path

def check_node_installed() -> bool:
    """Verifica se Node.js está instalado"""
    try:
        subprocess.run(['node', '--version'], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def get_venv_python():
    """Retorna o caminho do Python do ambiente virtual se existir"""
    venv_path = Path("venv")
    if venv_path.exists():
        if sys.platform == "win32":
            python_path = "venv/Scripts/python.exe"
        else:
            python_path = "venv/bin/python"
        
        if Path(python_path).exists():
            return python_path
    
    return sys.executable

def setup_backend_environment() -> bool:
    """Configura ambiente do backend usando run_venv.py se necessário"""
    venv_path = Path("venv")
    requirements_path = Path("requirements.txt")
    
    if not venv_path.exists() and requirements_path.exists():
        print("🐍 Configurando ambiente virtual do backend...")
        try:
            # Executa apenas a parte de setup do run_venv.py
            from run_venv import check_venv, install_dependencies, create_directories, check_env_file
            
            check_venv()
            create_directories()
            install_dependencies()
            check_env_file()
            
            print("✅ Ambiente backend configurado")
            return True
        except Exception as e:
            print(f"❌ Erro ao configurar backend: {e}")
            print("💡 Tente executar primeiro: python run_venv.py")
            return False
    
    return True

def install_frontend_dependencies() -> bool:
    """Instala dependências do frontend se necessário"""
    frontend_dir = os.path.join(os.getcwd(), 'frontend')
    node_modules = os.path.join(frontend_dir, 'node_modules')
    
    if not os.path.exists(node_modules):
        print("📦 Instalando dependências do frontend...")
        try:
            subprocess.run(['npm', 'install'], cwd=frontend_dir, check=True)
            print("✅ Dependências do frontend instaladas")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Erro ao instalar dependências: {e}")
            return False
    return True

def start_backend() -> subprocess.Popen:
    """Inicia o servidor FastAPI usando ambiente virtual se disponível"""
    print("🚀 Iniciando backend (FastAPI)...")
    
    python_cmd = get_venv_python()
    print(f"📍 Usando Python: {python_cmd}")
    
    # Configurar variáveis de ambiente
    env = os.environ.copy()
    env.setdefault("AUDIOS_DIR", "./public/audios")
    env.setdefault("TRANSCRIPTIONS_DIR", "./public/transcriptions")
    env.setdefault("LOG_FILE", "./logs/app.log")
    
    return subprocess.Popen(
        [python_cmd, 'main.py'],
        cwd=os.getcwd(),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True,
        bufsize=1,
        env=env
    )

def start_frontend() -> subprocess.Popen:
    """Inicia o servidor Next.js"""
    print("🎨 Iniciando frontend (Next.js)...")
    frontend_dir = os.path.join(os.getcwd(), 'frontend')
    return subprocess.Popen(
        ['npm', 'run', 'dev'],
        cwd=frontend_dir,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True,
        bufsize=1
    )

def monitor_processes(processes: List[subprocess.Popen], names: List[str]):
    """Monitora os processos e exibe logs"""
    try:
        while True:
            for i, (process, name) in enumerate(zip(processes, names)):
                if process.poll() is not None:
                    print(f"❌ {name} parou inesperadamente (código: {process.returncode})")
                    return
                
                # Lê output não-bloqueante
                try:
                    line = process.stdout.readline()
                    if line:
                        print(f"[{name}] {line.strip()}")
                except:
                    pass
            
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\n⏹️  Parando aplicações...")
        for process, name in zip(processes, names):
            print(f"🛑 Parando {name}...")
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()
        print("✅ Aplicações paradas")

def main():
    """Função principal"""
    print("🔥 Iniciando Full Stack - API + Frontend")
    print("=" * 50)
    
    # Verificações iniciais
    if not check_node_installed():
        print("❌ Node.js não encontrado. Instale o Node.js primeiro.")
        sys.exit(1)
    
    # Configurar ambiente backend
    if not setup_backend_environment():
        sys.exit(1)
    
    # Instalar dependências frontend
    if not install_frontend_dependencies():
        sys.exit(1)
    
    # Inicia os processos
    processes = []
    names = []
    
    try:
        # Backend
        backend_process = start_backend()
        processes.append(backend_process)
        names.append("Backend")
        
        # Aguarda um pouco para o backend inicializar
        time.sleep(3)
        
        # Frontend
        frontend_process = start_frontend()
        processes.append(frontend_process)
        names.append("Frontend")
        
        print("\n🎉 Aplicações iniciadas!")
        print("📝 URLs:")
        print("   Backend:  http://localhost:8000")
        print("   Docs API: http://localhost:8000/docs")
        print("   Frontend: http://localhost:3000")
        print("\n💡 Pressione Ctrl+C para parar ambas as aplicações")
        print("⚠️  Se houver erro de token HuggingFace, configure o .env")
        print("=" * 50)
        
        # Monitora processos
        monitor_processes(processes, names)
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        for process in processes:
            try:
                process.terminate()
                process.wait(timeout=5)
            except:
                try:
                    process.kill()
                except:
                    pass
        sys.exit(1)

if __name__ == "__main__":
    main()