#!/usr/bin/env python3
"""
Script para diagnosticar problemas de GPU
"""
import subprocess
import sys

def check_nvidia_drivers():
    """Verifica drivers NVIDIA"""
    print("🔍 Verificando drivers NVIDIA...")
    
    try:
        result = subprocess.run(['nvidia-smi'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Drivers NVIDIA funcionando")
            print(result.stdout)
            return True
        else:
            print("❌ Drivers NVIDIA não funcionando")
            print(result.stderr)
            return False
    except FileNotFoundError:
        print("❌ nvidia-smi não encontrado")
        return False

def check_cuda_toolkit():
    """Verifica CUDA toolkit"""
    print("\n🔍 Verificando CUDA toolkit...")
    
    try:
        result = subprocess.run(['nvcc', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ CUDA toolkit instalado")
            print(result.stdout)
            return True
        else:
            print("❌ CUDA toolkit não funcionando")
            return False
    except FileNotFoundError:
        print("❌ nvcc não encontrado")
        return False

def check_pytorch_gpu():
    """Verifica PyTorch com GPU"""
    print("\n🔍 Verificando PyTorch com GPU...")
    
    try:
        import torch
        
        print(f"PyTorch version: {torch.__version__}")
        print(f"CUDA available: {torch.cuda.is_available()}")
        
        if torch.cuda.is_available():
            print(f"CUDA version: {torch.version.cuda}")
            print(f"GPU device: {torch.cuda.get_device_name()}")
            print(f"GPU count: {torch.cuda.device_count()}")
            
            # Teste básico
            device = torch.device("cuda")
            x = torch.randn(3, 3).to(device)
            y = torch.randn(3, 3).to(device)
            z = torch.mm(x, y)
            print("✅ Teste de GPU bem-sucedido!")
            return True
        else:
            print("❌ CUDA não disponível no PyTorch")
            return False
            
    except ImportError:
        print("❌ PyTorch não instalado")
        return False
    except Exception as e:
        print(f"❌ Erro no teste de GPU: {e}")
        return False

def check_gpu_compatibility():
    """Verifica compatibilidade da GPU"""
    print("\n🔍 Verificando compatibilidade da GPU...")
    
    try:
        import torch
        
        if torch.cuda.is_available():
            device_name = torch.cuda.get_device_name()
            print(f"GPU: {device_name}")
            
            # Verificar se é RTX 5070 Ti
            if "5070" in device_name or "5070 Ti" in device_name:
                print("⚠️  RTX 5070 Ti detectada")
                print("💡 Esta GPU é muito nova e pode precisar de versões específicas")
                print("📋 Recomendações:")
                print("   1. Use PyTorch com CUDA 12.1+")
                print("   2. Atualize drivers NVIDIA")
                print("   3. Considere usar CPU se houver problemas")
            else:
                print("✅ GPU compatível detectada")
                
            return True
        else:
            print("❌ Nenhuma GPU detectada")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao verificar GPU: {e}")
        return False

def suggest_solutions():
    """Sugere soluções para problemas"""
    print("\n💡 Sugestões de solução:")
    print("=" * 40)
    
    print("1. Se drivers não funcionam:")
    print("   sudo apt update")
    print("   sudo apt install nvidia-driver-535")
    print("   sudo reboot")
    
    print("\n2. Se CUDA não está instalado:")
    print("   ./install_cuda.sh")
    
    print("\n3. Se PyTorch não funciona com GPU:")
    print("   python3 setup_gpu.py")
    
    print("\n4. Como último recurso (CPU):")
    print("   python3 setup_cpu.py")
    
    print("\n5. Verificar status:")
    print("   nvidia-smi")
    print("   python3 check_gpu.py")

def main():
    """Função principal"""
    print("🔍 Diagnóstico de GPU")
    print("=" * 30)
    
    drivers_ok = check_nvidia_drivers()
    cuda_ok = check_cuda_toolkit()
    pytorch_ok = check_pytorch_gpu()
    compatibility_ok = check_gpu_compatibility()
    
    print("\n" + "=" * 30)
    print("📊 Resumo:")
    print(f"   Drivers NVIDIA: {'✅' if drivers_ok else '❌'}")
    print(f"   CUDA Toolkit: {'✅' if cuda_ok else '❌'}")
    print(f"   PyTorch GPU: {'✅' if pytorch_ok else '❌'}")
    print(f"   Compatibilidade: {'✅' if compatibility_ok else '❌'}")
    
    if all([drivers_ok, cuda_ok, pytorch_ok, compatibility_ok]):
        print("\n🎉 GPU está funcionando perfeitamente!")
        print("🚀 Execute: python3 setup_gpu.py")
    else:
        print("\n⚠️  Problemas detectados")
        suggest_solutions()

if __name__ == "__main__":
    main() 