# Project Context: Transcription Service

## Stack Tecnológico

### Backend
- **Framework**: FastAPI 0.110.0
- **Python**: 3.10 (baseado no Dockerfile)
- **ASGI Server**: Uvicorn 0.27.1
- **Validação**: Pydantic 2.6.1
- **Configuração**: python-dotenv 1.0.0

### IA/Machine Learning
- **Transcrição**: WhisperX 3.3.0
- **Modelo**: Faster-Whisper 1.1.0, CTranslate2 4.4.0
- **Diarização**: PyAnnote.Audio 3.3.2
- **Transformers**: Transformers, SpeechBrain 1.0.0+
- **Audio Processing**: LibROSA 0.10.0+, SoundFile 0.13.0+

### Infraestrutura
- **Containerização**: Docker + Docker Compose
- **Gerenciamento de Processos**: Scripts bash para setup
- **Cache**: HuggingFace cache local
- **Logs**: Sistema de logging customizado com ColoredFormatter

## Estrutura do Projeto

```
/
├── main.py                    # Entry point da aplicação FastAPI
├── requirements.txt           # Dependências Python
├── Dockerfile                 # Container configuration
├── docker-compose.yml         # Orquestração de serviços
├── .env                       # Variáveis de ambiente
├── src/
│   ├── api/
│   │   └── routes/
│   │       ├── health.py      # Health check endpoint
│   │       └── transcribe.py  # Endpoints de transcrição
│   ├── config/
│   │   └── config.py          # AppConfig com enum ModelSize
│   ├── core/
│   │   ├── colored_formatter.py # Formatação de logs
│   │   └── logger_config.py   # Configuração global de logging
│   ├── models/
│   │   └── schemas.py         # Pydantic models (TranscriptionTask, etc.)
│   └── services/
│       ├── audio_transcriber.py # Core transcription logic
│       └── transcription.py   # Service layer para gerenciar tasks
├── scripts/                   # Scripts de setup e execução
├── public/
│   ├── audios/               # Upload de arquivos de áudio
│   ├── transcriptions/       # Arquivos de transcrição gerados
│   └── logs/                 # Logs da aplicação
├── cache/huggingface/        # Cache local dos modelos
└── venv/                     # Virtual environment Python
```

## Padrões de Desenvolvimento

### Nomenclatura
- **Arquivos**: snake_case (transcribe.py, audio_transcriber.py)
- **Classes**: PascalCase (TranscriptionService, AppConfig)
- **Variáveis/Funções**: snake_case (get_settings, process_transcription)
- **Constantes**: UPPER_CASE (HUGGING_FACE_HUB_TOKEN)
- **Task IDs**: formato `{timestamp}_{hex_random}` (20250728_190005_0e554efe)

### Estrutura de Código
- **Dependency Injection**: FastAPI Depends() para services
- **Configuration**: Dataclass-based com Pydantic validation
- **Error Handling**: HTTPException com logging detalhado
- **Async/Await**: Background tasks para processamento pesado
- **Type Hints**: Uso extensivo de typing (Optional, List, Dict)

### Logging
- **Logger centralizado**: `get_logger(__name__)`
- **Formatação customizada**: ColoredFormatter para output colorido
- **Níveis**: INFO para operações normais, ERROR para exceções
- **Arquivo de log**: Configurável via LOG_FILE (padrão: ./public/logs/app.log)

## Configurações Específicas

### Modelos Disponíveis
```python
class ModelSize(str, Enum):
    TINY = "tiny"
    BASE = "base" 
    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"
    TURBO = "turbo"  # Padrão
```

### Formatos de Áudio Suportados
- MP3, WAV, OGG, M4A, FLAC, AAC
- Limite de tamanho: 100MB
- Content-type validation flexível

### Task Management
- **Estados**: PENDING → PROCESSING → COMPLETED/FAILED
- **Persistência**: JSON file em `public/transcriptions/tasks.json`
- **Serialização**: ISO datetime format para compatibilidade
- **Background processing**: FastAPI BackgroundTasks

## Scripts Disponíveis

### Setup Scripts
- `scripts/setup_local.sh` - Setup para desenvolvimento local
- `scripts/setup_venv.sh` - Configuração do virtual environment
- `scripts/setup_rtx5070ti.sh` - Setup específico para RTX 5070 Ti
- `scripts/install_cuda.sh` - Instalação CUDA

### Execution Scripts  
- `scripts/run_with_cpu.sh` - Execução forçando CPU
- `scripts/run_with_gpu.sh` - Execução com GPU
- `scripts/activate_venv.sh` - Ativação do ambiente virtual
- `scripts/fix_permissions.sh` - Correção de permissões

### Python Runners
- `run_local.py` - Execução local
- `run_venv.py` - Execução no virtual environment
- `setup_cpu.py` / `setup_gpu.py` - Setup Python para CPU/GPU

## Configuração Docker

### Dockerfile Features
- **Base Image**: python:3.10-slim
- **Non-root user**: appuser para segurança
- **System deps**: ffmpeg, libsndfile1, build-essential
- **Volume mounts**: audios, transcriptions, logs, cache
- **Health check**: curl para /health endpoint
- **Memory limits**: 4GB limit, 2GB reservation

### Environment Variables

#### Obrigatórias
- `HUGGING_FACE_HUB_TOKEN` - Token para HuggingFace Hub

#### Opcionais (com padrões)
- `VERSION_MODEL=turbo` - Modelo Whisper a usar
- `FORCE_CPU=false` - Força uso de CPU vs GPU
- `LOG_LEVEL=INFO` - Nível de logging
- `AUDIOS_DIR=./public/audios` - Diretório de upload
- `TRANSCRIPTIONS_DIR=./public/transcriptions` - Diretório de output
- `LOG_FILE=./public/logs/app.log` - Arquivo de log
- `HF_HOME_DIR=./cache/huggingface` - Cache dos modelos

## API Endpoints

### Core Endpoints
- `POST /transcribe/` - Upload e inicia transcrição
- `GET /transcribe/{task_id}` - Status da tarefa
- `GET /transcribe/{task_id}/download` - Download do resultado
- `GET /transcribe/` - Lista todas as tarefas
- `GET /health/` - Health check

### Response Models
- `TranscriptionTask` - Task completa com status
- `TranscriptionListResponse` - Lista paginada de tasks
- `TranscriptionRequest` - Parâmetros de entrada (comentado no código atual)

## Observações Importantes

### Estado Atual do Código
- **Parâmetros de request comentados**: TranscriptionRequest não está sendo usado
- **Validação flexível**: Aceita tanto content-type quanto extensão
- **Cache inteligente**: Reutiliza instância do transcriber
- **Fallback de diretórios**: Usa temp dir se não conseguir escrever

### Segurança
- **Non-root containers**: Usuario appuser nos containers
- **File validation**: Extensão e tamanho de arquivo
- **No new privileges**: Security opt no docker-compose
- **Expose mínimo**: Apenas porta 8000

### Performance
- **Background processing**: Transcrição não bloqueia request
- **Model caching**: Modelos carregados uma vez e reutilizados
- **Memory management**: Limits configurados no Docker
- **Volume optimization**: Cache persistente para modelos