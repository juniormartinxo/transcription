# 🎵 Aplicação de Transcrição Full-Stack

Aplicação completa para transcrição de áudio e vídeo com FastAPI + Next.js. Backend usa WhisperX para transcrição e PyAnnote.Audio para diarização, com suporte completo para GPU e CPU, incluindo compatibilidade especial para RTX 5070 Ti. Frontend moderno em React para gerenciamento de arquivos e transcrições.

## 🏗️ Arquitetura

```
.
├── api/                    # Backend FastAPI
│   ├── main.py            # Entrada da API
│   ├── src/               # Código fonte do backend
│   ├── requirements.txt   # Dependências Python
│   ├── venv/              # Ambiente virtual
│   └── scripts/           # Scripts de setup
├── frontend/              # Frontend Next.js
│   ├── src/               # Componentes React
│   ├── package.json       # Dependências Node.js
│   └── public/            # Assets estáticos
├── public/                # Dados compartilhados
│   ├── audios/            # Arquivos de áudio
│   ├── transcriptions/    # Transcrições geradas
│   └── videos/            # Arquivos de vídeo
├── logs/                  # Logs da aplicação
└── docker-compose.yml     # Orquestração de containers
```

## 🚀 Execução Rápida

### Opção 1: Full Stack (Recomendada)
```bash
# Executa backend + frontend simultaneamente
./run_dev.sh
```

### Opção 2: Python Script
```bash
# Alternativa em Python
python run_full_stack.py
```

### Opção 3: Docker (Isolamento completo)
```bash
# Execução containerizada
docker-compose up --build
```

### Opção 4: Execução Separada
```bash
# Backend apenas
cd api && python run_venv.py

# Frontend apenas (em outro terminal)
cd frontend && npm run dev
```

## 📋 Pré-requisitos

### 1. Python 3.8+
```bash
python3 --version
```

### 2. Node.js 18+
```bash
node --version
npm --version
```

### 3. FFmpeg
```bash
# Ubuntu/Debian
sudo apt update && sudo apt install ffmpeg

# macOS
brew install ffmpeg

# Windows
# Baixe de: https://ffmpeg.org/download.html
```

### 4. Token do HuggingFace
1. Acesse: https://huggingface.co/settings/tokens
2. Crie um novo token
3. Aceite os termos dos modelos:
   - https://huggingface.co/pyannote/speaker-diarization
   - https://huggingface.co/pyannote/segmentation

## ⚙️ Configuração

### Arquivo .env (raiz do projeto)
```env
# Token obrigatório do HuggingFace
HUGGING_FACE_HUB_TOKEN=seu_token_aqui

# Configurações opcionais do backend
VERSION_MODEL=turbo
FORCE_CPU=false
AUDIOS_DIR=./public/audios
TRANSCRIPTIONS_DIR=./public/transcriptions
LOG_LEVEL=INFO
LOG_FILE=./logs/app.log

# Configurações do frontend
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## 🌐 URLs da Aplicação

Após iniciar a aplicação:

### Frontend (Interface Principal)
- **Dashboard**: http://localhost:3000
- **Upload de Arquivos**: Interface gráfica completa
- **Gerenciamento de Transcrições**: Visualização em tempo real
- **Health Check**: http://localhost:3000/api/health

### Backend (API)
- **Health Check**: http://localhost:8000/health
- **Documentação Interativa**: http://localhost:8000/docs
- **API Endpoints**: http://localhost:8000/transcribe/

## 🔧 Funcionalidades

### Backend (FastAPI)
- ✅ **Transcrição de Áudio**: WhisperX com modelos turbo/large
- ✅ **Diarização**: Identificação de speakers com PyAnnote
- ✅ **Processamento de Vídeo**: Extração automática de áudio
- ✅ **Upload em Lote**: Múltiplos arquivos simultaneamente
- ✅ **4 Tipos de Saída**: Limpa, Timestamps, Diarização, Completa
- ✅ **GPU/CPU**: Suporte completo incluindo RTX 5070 Ti
- ✅ **Background Tasks**: Processamento não-bloqueante

### Frontend (Next.js)
- ✅ **Interface Moderna**: React 19 + TypeScript + TailwindCSS
- ✅ **Upload Drag & Drop**: Suporte para áudio e vídeo
- ✅ **Progresso em Tempo Real**: Acompanhamento de transcrições
- ✅ **Dashboard Completo**: Listagem e gerenciamento de tarefas
- ✅ **Download Direto**: Baixar transcrições prontas
- ✅ **Responsive**: Otimizado para desktop e mobile

## 🖥️ Modos de Execução GPU

### RTX 5070 Ti (Configuração Especial)
```bash
# Setup específico para RTX 5070 Ti
cd api && ./scripts/setup_rtx5070ti.sh

# Execução otimizada
cd api && ./scripts/run_with_gpu.sh
```

### GPU Padrão
```bash
# Execução com GPU
cd api && ./scripts/run_with_gpu.sh
```

### CPU (Fallback)
```bash
# Forçar execução em CPU
cd api && ./scripts/run_with_cpu.sh
```

## 📡 Endpoints da API

### Transcrição
- `POST /transcribe/` - Upload de áudio individual
- `POST /transcribe/batch-audio` - Upload de áudios em lote
- `POST /transcribe/extract-audio` - Upload de vídeo (extrai áudio automaticamente)
- `POST /transcribe/batch-video` - Upload de vídeos em lote

### Gerenciamento
- `GET /transcribe/` - Listar todas as tarefas
- `GET /transcribe/{task_id}` - Status de tarefa específica
- `GET /transcribe/{task_id}/download` - Download da transcrição
- `DELETE /transcribe/{task_id}` - Deletar tarefa

### Sistema
- `GET /health` - Status da API

## 🛠️ Scripts Disponíveis

### Scripts de Desenvolvimento
- `./run_dev.sh` - **RECOMENDADO**: Inicia backend + frontend
- `python run_full_stack.py` - Alternativa Python para full stack

### Scripts Backend (dentro de `api/`)
- `python run_local.py` - Setup e execução local
- `python run_venv.py` - Setup com ambiente virtual
- `./scripts/setup_rtx5070ti.sh` - Configuração RTX 5070 Ti
- `./scripts/run_with_gpu.sh` - Execução com GPU
- `./scripts/run_with_cpu.sh` - Execução em CPU
- `./scripts/fix_permissions.sh` - Corrigir permissões

### Scripts Frontend (dentro de `frontend/`)
- `npm run dev` - Servidor de desenvolvimento (Turbopack)
- `npm run build` - Build de produção
- `npm run start` - Servidor de produção
- `npm run lint` - Verificação ESLint

## 🎯 Fluxos de Trabalho

### Para Desenvolvedores (Primeira vez)
```bash
# 1. Clone o repositório
git clone <url-do-repositorio>
cd transcription

# 2. Configure o token HuggingFace no .env
echo "HUGGING_FACE_HUB_TOKEN=seu_token_aqui" > .env

# 3. Execute o setup completo
./run_dev.sh

# 4. Acesse a aplicação
# Frontend: http://localhost:3000
# API: http://localhost:8000/docs
```

### Para Produção
```bash
# 1. Use Docker para produção
cp .env.example .env
# Edite .env com suas configurações

# 2. Execute com Docker Compose
docker compose -f docker-compose.prod.yml up -d --build

# 3. Monitore os serviços
docker compose logs -f
```

### Upload de Arquivos

#### Via Interface Web (Recomendado)
1. Acesse http://localhost:3000
2. Arraste arquivos ou use o botão de upload
3. Acompanhe o progresso em tempo real
4. Baixe as transcrições quando prontas

#### Via API (cURL)
```bash
# Upload de áudio individual
curl -X POST "http://localhost:8000/transcribe/" \
  -F "file=@audio.wav"

# Upload de vídeo (extrai áudio automaticamente)
curl -X POST "http://localhost:8000/transcribe/extract-audio" \
  -F "file=@video.mp4"

# Verificar status
curl "http://localhost:8000/transcribe/{task_id}"
```

## 🐳 Docker

### Desenvolvimento
```bash
# Execução com hot-reload
docker compose up --build

# Ver logs específicos
docker compose logs frontend
docker compose logs backend
```

### Produção
```bash
# Build otimizado
docker compose -f docker-compose.prod.yml up -d --build

# Monitoramento
docker compose -f docker-compose.prod.yml logs -f
```

### Comandos Úteis
```bash
# Parar containers
docker compose down

# Limpar volumes (cuidado!)
docker compose down -v

# Shell no container backend
docker compose exec backend bash

# Shell no container frontend
docker compose exec frontend sh
```

## 🔧 Troubleshooting

### Script `run_dev.sh` falha
```bash
# Verificar se tem Python correto no ambiente virtual
cd api && ls -la venv/bin/python

# Executar manualmente para debug
cd api && venv/bin/python main.py
```

### Frontend não conecta com backend
```bash
# Verificar se backend está rodando
curl http://localhost:8000/health

# Verificar configuração CORS no frontend
grep NEXT_PUBLIC_API_URL frontend/.env*
```

### "Token do HuggingFace não encontrado"
```bash
# Verificar arquivo .env na raiz
cat .env | grep HUGGING_FACE_HUB_TOKEN

# Verificar se API está lendo a variável
curl http://localhost:8000/health
```

### Problemas de GPU RTX 5070 Ti
```bash
# Verificar se PyTorch Nightly está instalado
cd api && venv/bin/python -c "import torch; print(torch.__version__)"

# Executar setup específico
cd api && ./scripts/setup_rtx5070ti.sh
```

### Erros de Permissão
```bash
# Corrigir permissões dos diretórios
cd api && ./scripts/fix_permissions.sh

# Verificar ownership dos arquivos
ls -la public/
```

## 📊 Performance

### Com GPU (RTX 5070 Ti)
- **Transcrição**: ~30-60s para áudio de 3 minutos
- **Diarização**: Significativamente acelerada
- **Memória**: ~8-12GB VRAM
- **Paralelismo**: Múltiplas transcrições simultâneas

### Com CPU
- **Transcrição**: ~2-3 minutos para áudio de 3 minutos
- **Diarização**: Mais lenta mas funcional
- **Memória**: ~4-8GB RAM
- **Paralelismo**: Limitado pela CPU

## 📈 Monitoramento

### Logs da Aplicação
```bash
# Logs do backend
tail -f logs/app.log

# Logs do Docker
docker compose logs -f backend
docker compose logs -f frontend

# Logs durante desenvolvimento
tail -f backend.log    # Script run_dev.sh
tail -f frontend.log   # Script run_dev.sh
```

### Health Checks
```bash
# Status completo da aplicação
curl http://localhost:3000/api/health  # Frontend
curl http://localhost:8000/health      # Backend

# Status detalhado via frontend
# Acesse: http://localhost:3000 (mostra status em tempo real)
```

### Verificar GPU
```bash
# Status da GPU
nvidia-smi

# Testar PyTorch + CUDA
cd api && venv/bin/python -c "import torch; print(f'CUDA: {torch.cuda.is_available()}')"
```

## 🔄 Comparação de Métodos

| Método | Facilidade | Performance | Isolamento | Debug | Recomendado Para |
|--------|------------|-------------|------------|-------|------------------|
| `./run_dev.sh` | ✅ Muito fácil | ✅ Ótima | ⚠️ Médio | ✅ Fácil | **Desenvolvimento** |
| `python run_full_stack.py` | ✅ Fácil | ✅ Ótima | ⚠️ Médio | ✅ Fácil | Desenvolvimento |
| Docker Compose | ✅ Fácil | ⚠️ Boa | ✅ Completo | ⚠️ Médio | **Produção** |
| Execução Separada | ❌ Trabalhoso | ✅ Máxima | ❌ Baixo | ✅ Máximo | Debug avançado |

## 📱 Formatos Suportados

### Áudio
- WAV, MP3, FLAC, OGG, M4A, AAC

### Vídeo  
- MP4, AVI, MOV, MKV, WEBM, FLV
- **Nota**: Extrai áudio automaticamente em 16kHz mono

### Transcrições Geradas
- **Limpa**: Apenas texto, sem timestamps ou speakers
- **Timestamps**: Texto com marcações de tempo
- **Diarização**: Texto com identificação de speakers
- **Completa**: Timestamps + diarização + formatação

## 🎉 Exemplo Completo

```bash
# 1. Setup inicial
git clone <repo>
cd transcription

# 2. Configurar token
echo "HUGGING_FACE_HUB_TOKEN=hf_seu_token_aqui" > .env

# 3. Executar aplicação
./run_dev.sh

# 4. Usar a interface web
# Abrir: http://localhost:3000
# - Upload arquivos via drag & drop
# - Acompanhar progresso em tempo real  
# - Baixar transcrições quando prontas

# 5. Ou usar API diretamente
curl -X POST "http://localhost:8000/transcribe/" \
  -F "file=@exemplo.wav"

# 6. Verificar resultado
curl "http://localhost:8000/transcribe/{task_id}"
```

## 🚨 Notas Importantes

1. **Primeira execução**: Modelos são baixados automaticamente (~2-4GB)
2. **GPU Memory**: RTX 5070 Ti requer pelo menos 8GB VRAM livres
3. **Internet**: Necessária apenas na primeira execução
4. **HuggingFace**: Token obrigatório para diarização
5. **Arquivos grandes**: Vídeos até 500MB, áudios até 100MB
6. **Background**: Transcrições rodam em background, não bloqueiam a API

## 📞 Suporte

### Para Problemas
1. **Verifique logs**: `tail -f logs/app.log`
2. **Teste health checks**: URLs mostradas acima
3. **Verifique dependências**: FFmpeg, Python, Node.js, token HF
4. **Use scripts de correção**: `cd api && ./scripts/fix_permissions.sh`
5. **Teste com arquivos pequenos** primeiro

### Para RTX 5070 Ti
- Use **obrigatoriamente** PyTorch Nightly
- Execute scripts específicos de GPU
- Monitore VRAM com `nvidia-smi`

A aplicação está pronta para transcrever seus arquivos com interface web moderna e API robusta! 🚀