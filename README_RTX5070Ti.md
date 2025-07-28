# API de Transcrição - Suporte RTX 5070 Ti

## 🚀 Configuração Especial para RTX 5070 Ti

Este guia detalha como configurar a API de transcrição para funcionar com a **NVIDIA GeForce RTX 5070 Ti**, que requer PyTorch Nightly devido à sua arquitetura CUDA sm_120 mais recente.

## ⚠️ Problema Resolvido

**Problema Original:**
- RTX 5070 Ti usa arquitetura CUDA sm_120 (muito nova)
- PyTorch estável (2.7.1) só suporta até sm_90
- Erro: `CUDA error: no kernel image is available for execution on the device`

**Solução Implementada:**
- PyTorch Nightly 2.9.0 com CUDA 12.8
- Correções de compatibilidade para diarização
- Configurações otimizadas para GPU

## 🛠️ Instalação

### 1. Criar ambiente virtual
```bash
python3 -m venv venv
source venv/bin/activate
```

### 2. Instalar dependências básicas
```bash
pip install -r requirements.txt
```

### 3. Instalar PyTorch Nightly (ESSENCIAL para RTX 5070 Ti)
```bash
# Método automático
./setup_rtx5070ti.sh

# Ou manual
pip uninstall torch torchvision torchaudio -y
pip install --pre torch torchvision torchaudio --index-url https://download.pytorch.org/whl/nightly/cu128
```

### 4. Configurar token HuggingFace
Edite o arquivo `.env`:
```bash
HUGGING_FACE_HUB_TOKEN=seu_token_aqui
FORCE_CPU=false  # Importante: false para usar GPU
```

## 🚀 Execução

### Para RTX 5070 Ti (Recomendado)
```bash
./run_with_gpu.sh
```

### Para CPU (Backup)
```bash
./run_with_cpu.sh
```

## ✅ Verificação da Instalação

O script `run_with_gpu.sh` exibirá:
```
🚀 Starting Transcription API with RTX 5070 Ti GPU Support
==========================================
✅ Using PyTorch Nightly with CUDA 12.8 for RTX 5070 Ti compatibility

PyTorch version: 2.9.0.dev20250726+cu128
CUDA available: True
CUDA version: 12.8
GPU devices: 1
GPU name: NVIDIA GeForce RTX 5070 Ti
```

## 📋 Especificações Técnicas

### PyTorch Nightly
- **Versão**: 2.9.0.dev20250726+cu128
- **CUDA**: 12.8
- **Suporte**: Arquitetura sm_120 (RTX 5070 Ti)

### Configurações Otimizadas
- **Compute Type**: float16 (GPU) / int8 (CPU)
- **Batch Size**: 16 (GPU) / 4 (CPU)
- **TF32**: Habilitado para melhor performance
- **Device**: CUDA com fallback automático para CPU

## 🔧 Correções Implementadas

### 1. Device Compatibility
```python
self.torch_device = torch.device(self.device)
self.diarize_model = self.diarize_model.to(self.torch_device)
```

### 2. TF32 Configuration
```python
if self.has_cuda:
    torch.backends.cuda.matmul.allow_tf32 = True
    torch.backends.cudnn.allow_tf32 = True
```

### 3. Warning Suppression
```python
warnings.filterwarnings("ignore", message=".*torch.cuda.amp.custom_fwd.*")
warnings.filterwarnings("ignore", message=".*Model was trained with.*")
```

### 4. CUDNN Path
```bash
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$(python -c "import nvidia.cudnn; print(nvidia.cudnn.__path__[0])")/lib
```

## 🚨 Troubleshooting

### Erro: "no kernel image is available"
- **Causa**: PyTorch estável não suporta RTX 5070 Ti
- **Solução**: Use PyTorch Nightly (implementado)

### Erro: "libcudnn_ops_infer.so.8: cannot open shared object file"
- **Causa**: CUDNN não encontrado
- **Solução**: Configurado no `run_with_gpu.sh`

### Erro: "device must be an instance of torch.device"
- **Causa**: Passagem incorreta do device
- **Solução**: Corrigido com `torch.device()`

## 📊 Performance Esperada

### Com RTX 5070 Ti (GPU)
- **Transcrição**: ~30-60s para áudio de 3 minutos
- **Diarização**: Acelerada significativamente
- **Memória**: ~8-12GB VRAM

### CPU Fallback
- **Transcrição**: ~2-3 minutos para áudio de 3 minutos
- **Diarização**: Mais lenta mas funcional
- **Memória**: ~4-8GB RAM

## 🔄 Atualizações Futuras

Quando o PyTorch estável (2.8+) incluir suporte para RTX 5070 Ti:
1. Poderá voltar para PyTorch estável
2. Remover necessidade do Nightly
3. Simplificar instalação

## 📝 Logs de Status

### ✅ Funcionando Corretamente
```
- src.services.audio_transcriber - ℹ️ INFO - Dispositivo final: cuda
- src.services.audio_transcriber - ℹ️ INFO - Tipo de computação: float16
- src.services.audio_transcriber - ℹ️ INFO - Modelo Whisper carregado com sucesso
- src.services.audio_transcriber - ℹ️ INFO - Modelo de diarização carregado com sucesso
```

### ❌ Problemas Conhecidos (Não Críticos)
- Warnings de deprecated TorchAudio backends
- Warnings de versão do modelo (não afetam funcionalidade)

## 🎯 API Endpoints

- **Servidor**: http://localhost:8000
- **Documentação**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health
- **Transcrição**: POST /transcribe

A API está otimizada e pronta para produção com sua RTX 5070 Ti! 🚀