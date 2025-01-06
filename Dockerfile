# Dockerfile
FROM python:3.10-slim

# Criar usuário não-root
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Criar diretórios e configurar permissões mais permissivas para o cache
RUN mkdir -p /home/appuser/.cache/huggingface \
    /home/appuser/.config/matplotlib \
    /app/audios \
    /app/transcriptions \
    /app/logs && \
    chown -R appuser:appuser /home/appuser && \
    chmod -R 777 /home/appuser/.cache && \
    find /home/appuser/.cache -type d -exec chmod 777 {} + && \
    chown -R appuser:appuser /app && \
    chmod -R 755 /app

# ADICIONAR AQUI - Novas variáveis de ambiente
ENV HF_HOME=/home/appuser/.cache/huggingface \
    HF_HOME_DIR=/home/appuser/.cache/huggingface \
    HF_DATASETS_CACHE=/home/appuser/.cache/huggingface/datasets \
    TORCH_HOME=/home/appuser/.cache/torch \
    MPLCONFIGDIR=/home/appuser/.config/matplotlib \
    HOME=/home/appuser

# Instalar dependências do sistema necessárias
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libsndfile1 \
    curl \
    build-essential \
    libavcodec-extra \
    && rm -rf /var/lib/apt/lists/*

# Configurar diretório de trabalho
WORKDIR /app

# Otimizar pip e configurações Python
ENV PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_DEFAULT_TIMEOUT=100 \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_FIND_LINKS=https://download.pytorch.org/whl/cpu

# Copiar arquivos de requisitos primeiro
COPY requirements.txt .
    
# Antes do pip install
ENV PIP_DEFAULT_TIMEOUT=100 \
    PIP_FIND_LINKS=https://download.pytorch.org/whl/cpu
    
# Instalar dependências como root, mas com flags apropriadas
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copiar estrutura do projeto
COPY src/ src/
COPY main.py .

# Remover ou comentar este trecho
# RUN mkdir -p /app/audios /app/transcriptions /app/logs && \
#     chmod 777 /app/audios /app/transcriptions /app/logs

# Definir volumes para persistência
VOLUME ["/app/audios", "/app/transcriptions", "/app/logs"]

# Mudar ownership dos arquivos
RUN chown -R appuser:appuser /app

# Mudar para usuário não-root
USER appuser

# Healthcheck
#HEALTHCHECK --interval=90s --timeout=10s --retries=3 \
#    CMD curl -f http://localhost:8000/health || exit 1
HEALTHCHECK CMD curl -f http://localhost:8000/health || exit 1

# Comando para executar a aplicação
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]