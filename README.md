# 🎵 API de Transcrição de Áudio

API FastAPI para transcrição de áudio usando WhisperX e diarização com PyAnnote.Audio. Suporta execução em CPU e GPU com compatibilidade especial para RTX 5070 Ti.

## 🚀 Execução Rápida

### Opção 1: Execução Local (Recomendada para desenvolvimento)
```bash
python run_local.py
```

### Opção 2: Ambiente Virtual (Recomendada para produção)
```bash
python run_venv.py
```

### Opção 3: Docker (Isolamento completo)
```bash
docker-compose up --build
```

## 📋 Pré-requisitos

### 1. Python 3.8+
```bash
python3 --version
```

### 2. FFmpeg
```bash
# Ubuntu/Debian
sudo apt update && sudo apt install ffmpeg

# macOS
brew install ffmpeg

# Windows
# Baixe de: https://ffmpeg.org/download.html
```

### 3. Token do HuggingFace
1. Acesse: https://huggingface.co/settings/tokens
2. Crie um novo token
3. Aceite os termos dos modelos:
   - https://huggingface.co/pyannote/speaker-diarization
   - https://huggingface.co/pyannote/segmentation

## ⚙️ Configuração

### Arquivo .env
```env
# Token obrigatório do HuggingFace
HUGGING_FACE_HUB_TOKEN=seu_token_aqui

# Configurações opcionais
VERSION_MODEL=turbo
FORCE_CPU=false
AUDIOS_DIR=./public/audios
TRANSCRIPTIONS_DIR=./public/transcriptions
LOG_LEVEL=INFO
LOG_FILE=./logs/app.log
```

## 🖥️ Modos de Execução

### GPU com RTX 5070 Ti
Para placas RTX 5070 Ti, use PyTorch Nightly devido à arquitetura CUDA sm_120:

```bash
# Setup automático para RTX 5070 Ti
./scripts/setup_rtx5070ti.sh

# Executar com GPU
./scripts/run_with_gpu.sh
```

### CPU (Fallback)
```bash
./scripts/run_with_cpu.sh
```

## 🌐 Endpoints da API

### Teste de Saúde
```bash
curl http://localhost:8000/health
```

### Documentação Interativa
```bash
# Abra no navegador
http://localhost:8000/docs
```

### Upload de Áudio
```bash
curl -X POST "http://localhost:8000/transcribe/" \
  -F "file=@/caminho/para/seu/audio.wav"
```

### Status da Transcrição
```bash
curl http://localhost:8000/transcribe/{task_id}
```

## 📁 Estrutura do Projeto

```
transcription/
├── public/
│   ├── audios/          # Áudios enviados
│   └── transcriptions/  # Transcrições geradas
├── logs/                # Logs da aplicação
├── scripts/             # Scripts de setup e execução
├── src/                 # Código fonte
│   ├── api/            # Rotas da API
│   ├── config/         # Configurações
│   ├── core/           # Logger e utilitários
│   ├── models/         # Schemas Pydantic
│   └── services/       # Serviços de transcrição
├── venv/               # Ambiente virtual (criado automaticamente)
├── main.py             # Ponto de entrada
├── run_local.py        # Script de execução local
├── run_venv.py         # Script de execução com venv
└── requirements.txt    # Dependências
```

## 🛠️ Scripts Disponíveis

### Scripts de Setup

#### `scripts/setup_local.sh`
- ✅ Verifica Python 3 e FFmpeg
- ✅ Cria diretórios necessários
- ✅ Instala dependências globalmente
- ✅ Cria arquivo .env com configurações padrão
- 💡 **Uso**: Setup rápido para desenvolvimento local

#### `scripts/setup_venv.sh`
- ✅ Verifica Python 3 e FFmpeg
- ✅ Cria ambiente virtual automaticamente
- ✅ Instala dependências no ambiente isolado
- ✅ Cria diretórios e arquivo .env
- 💡 **Uso**: Setup com isolamento de dependências

#### `scripts/setup_rtx5070ti.sh`
- ✅ Remove PyTorch estável
- ✅ Instala PyTorch Nightly com CUDA 12.8
- ✅ Testa compatibilidade com RTX 5070 Ti
- ✅ Executa teste de GPU
- 💡 **Uso**: Configuração específica para RTX 5070 Ti

### Scripts de Execução

#### `scripts/run_with_gpu.sh`
- ✅ Ativa ambiente virtual
- ✅ Configura LD_LIBRARY_PATH para CUDNN
- ✅ Verifica status da GPU
- ✅ Executa API com aceleração GPU
- 💡 **Uso**: Execução otimizada para GPU (especialmente RTX 5070 Ti)

#### `scripts/run_with_cpu.sh`
- ✅ Ativa ambiente virtual
- ✅ Força execução em CPU
- ✅ Verifica status do PyTorch
- ✅ Executa API sem GPU
- 💡 **Uso**: Execução compatível com qualquer sistema

### Scripts Utilitários

#### `scripts/activate_venv.sh`
- ✅ Ativa ambiente virtual
- ✅ Mostra informações do Python/pip
- ✅ Lista comandos disponíveis
- 💡 **Uso**: Ativação manual do ambiente virtual

#### `scripts/fix_permissions.sh`
- ✅ Corrige permissões dos diretórios public/ e logs/
- ✅ Cria diretórios se não existirem
- ✅ Limpa cache do HuggingFace
- ✅ Corrige permissões do tasks.json
- 💡 **Uso**: Resolver problemas de permissão

#### `scripts/install_cuda.sh`
- ✅ Verifica instalação do CUDA
- ✅ Instala CUDA Toolkit se necessário
- ✅ Verifica drivers NVIDIA
- 💡 **Uso**: Instalação do CUDA para sistemas Ubuntu

## 🎯 Fluxos de Trabalho

### Para Desenvolvedores (Primeira vez)
```bash
# 1. Clone o repositório
git clone <url-do-repositorio>
cd transcription

# 2. Execute setup automático
python run_local.py

# 3. Configure o token no arquivo .env
# 4. A API estará disponível em http://localhost:8000
```

### Para Produção
```bash
# 1. Use ambiente virtual
python run_venv.py

# 2. Configure FORCE_CPU=false no .env (se tiver GPU)
# 3. Monitore logs/app.log
```

### Para RTX 5070 Ti
```bash
# 1. Setup com ambiente virtual
python run_venv.py

# 2. Configure PyTorch Nightly
source venv/bin/activate
./scripts/setup_rtx5070ti.sh

# 3. Execute com GPU
./scripts/run_with_gpu.sh
```

## 🔧 Problemas Conhecidos e Soluções

### RTX 5070 Ti - "no kernel image is available"
**Problema**: PyTorch estável não suporta arquitetura CUDA sm_120
**Solução**: Use PyTorch Nightly (automatizado nos scripts)

### "FFmpeg não encontrado"
```bash
# Ubuntu/Debian
sudo apt install ffmpeg

# macOS
brew install ffmpeg
```

### "Token do HuggingFace não encontrado"
```bash
# Verifique se o arquivo .env existe e tem o token
cat .env

# Configure manualmente se necessário
echo "HUGGING_FACE_HUB_TOKEN=seu_token_aqui" >> .env
```

### "Módulo não encontrado"
```bash
# Ambiente local
pip install -r requirements.txt --force-reinstall

# Ambiente virtual
source venv/bin/activate
pip install -r requirements.txt --force-reinstall
```

### Problemas de Permissão
```bash
# Execute o script de correção
./scripts/fix_permissions.sh
```

## 📊 Performance Esperada

### Com GPU (RTX 5070 Ti)
- **Transcrição**: ~30-60s para áudio de 3 minutos
- **Diarização**: Significativamente acelerada
- **Memória**: ~8-12GB VRAM

### Com CPU
- **Transcrição**: ~2-3 minutos para áudio de 3 minutos
- **Diarização**: Mais lenta mas funcional
- **Memória**: ~4-8GB RAM

## 📈 Monitoramento

### Logs da Aplicação
```bash
# Ver logs em tempo real
tail -f logs/app.log

# Ou usar a localização alternativa
tail -f public/logs/app.log
```

### Status da API
```bash
# Verificar se está funcionando
curl http://localhost:8000/health

# Ver documentação
curl http://localhost:8000/docs
```

### Verificar GPU
```bash
# Status da GPU
nvidia-smi

# Testar PyTorch com CUDA
python -c "import torch; print(f'CUDA: {torch.cuda.is_available()}')"
```

## 🔄 Comparação de Métodos

| Aspecto | Docker | Ambiente Virtual | Local |
|---------|--------|------------------|-------|
| **Isolamento** | ✅ Completo | ✅ Dependências | ❌ Sistema |
| **Setup** | ✅ Automático | ✅ Semi-automático | ⚠️ Manual |
| **Performance** | ⚠️ Overhead | ✅ Otimizada | ✅ Máxima |
| **Debug** | ❌ Complexo | ✅ Fácil | ✅ Direto |
| **Portabilidade** | ✅ Alta | ✅ Média | ⚠️ Baixa |
| **GPU Support** | ✅ Configurado | ✅ Flexível | ✅ Direto |

## 🚨 Notas Importantes

1. **Primeira execução**: Pode demorar para baixar os modelos do HuggingFace
2. **Memória**: WhisperX precisa de pelo menos 2GB RAM (4GB recomendado)
3. **Internet**: Necessária apenas na primeira execução para baixar modelos
4. **RTX 5070 Ti**: Requer PyTorch Nightly devido à arquitetura CUDA sm_120
5. **HuggingFace Token**: Obrigatório para modelos de diarização PyAnnote

## 📞 Suporte

Se encontrar problemas:

1. **Verifique os logs** em `logs/app.log`
2. **Confirme dependências**: FFmpeg, Python 3.8+, token HuggingFace
3. **Use scripts de correção**: `./scripts/fix_permissions.sh`
4. **Teste com arquivos pequenos** primeiro
5. **Para RTX 5070 Ti**: Use os scripts específicos de GPU

## 🎉 Exemplo Completo de Uso

```bash
# 1. Setup inicial
python run_venv.py

# 2. Configure o token (edite o arquivo .env)
# HUGGING_FACE_HUB_TOKEN=seu_token_aqui

# 3. Teste a API
curl http://localhost:8000/health

# 4. Faça upload de um áudio
curl -X POST "http://localhost:8000/transcribe/" \
  -F "file=@exemplo.wav"

# 5. Verifique o status da transcrição
curl http://localhost:8000/transcribe/{task_id_retornado}

# 6. Acesse a documentação interativa
# http://localhost:8000/docs
```

A API está pronta para transcrever seus arquivos de áudio com alta qualidade! 🚀