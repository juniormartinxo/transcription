# Dockerfile - Backend FastAPI
FROM python:3.12-slim

# Argumentos de build
ARG BUILD_ENV=production

# Metadados
LABEL maintainer="Transcription Service"
LABEL description="FastAPI backend for audio/video transcription service"

# Criar usuário não-root com UID/GID do host para evitar problemas de permissão
ARG USER_ID=1000
ARG GROUP_ID=1000
RUN groupadd -g ${GROUP_ID} appuser && useradd -u ${USER_ID} -g appuser -m appuser

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libsndfile1 \
    curl \
    build-essential \
    libavcodec-extra \
    git \
    patchelf \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Configurar diretório de trabalho
WORKDIR /app

# Configurar variáveis de ambiente para otimização
ENV PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_DEFAULT_TIMEOUT=100 \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app

# Configurar cache do Hugging Face e PyTorch
ENV HF_HOME=/app/cache/huggingface \
    HF_HUB_CACHE=/app/cache/huggingface \
    HF_ASSETS_CACHE=/app/cache/huggingface \
    TORCH_HOME=/app/cache/torch \
    MPLCONFIGDIR=/home/appuser/.config/matplotlib \
    HOME=/home/appuser \
    XDG_CACHE_HOME=/home/appuser/.cache \
    XDG_CONFIG_HOME=/home/appuser/.config

# Criar estrutura de diretórios
RUN mkdir -p \
    /home/appuser/.cache/huggingface \
    /home/appuser/.config/matplotlib \
    /app/public/audios \
    /app/public/transcriptions \
    /app/public/videos \
    /app/logs \
    /app/cache/huggingface \
    /app/cache/torch

# Copiar e instalar dependências Python
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Aplicar correção do patchelf para ctranslate2
RUN find /usr/local/lib/python*/site-packages/ -name "*ctranslate2*.so*" -exec patchelf --clear-execstack {} \; 2>/dev/null || true

# Copiar código da aplicação
COPY src/ src/
COPY main.py .

# Ajustar permissões
RUN chown -R appuser:appuser /app /home/appuser && \
    chmod -R 755 /app /home/appuser

# Mudar para usuário não-root
USER appuser

# Exposer porta
EXPOSE 8000

# Volumes para persistência
VOLUME ["/app/public/audios", "/app/public/transcriptions", "/app/public/videos", "/app/logs", "/app/cache"]

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --retries=3 --start-period=40s \
    CMD curl -f http://localhost:8000/health || exit 1

# Comando padrão
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]