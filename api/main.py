# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.routes import health, transcribe
from src.config.config import (  # Alterado de Config para AppConfig
    AppConfig,
    get_settings,
)
from src.core.logger_config import get_logger, setup_global_logging
from src.services.transcription import TranscriptionService

# Configura o logger global
setup_global_logging(log_file="app.log")
logger = get_logger(__name__)

def create_app() -> FastAPI:
    app = FastAPI(
        title="API de Transcrição de Áudio",
        description="API para transcrição de áudio usando WhisperX",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc"
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    try:
        config = AppConfig.from_env()
        service = TranscriptionService(config)
        app.state.transcription_service = service
        logger.info(f"Configuração carregada: VERSION_MODEL={config.version_model}, FORCE_CPU={config.force_cpu}")
    except Exception as e:
        logger.error(f"Erro ao carregar configuração: {str(e)}")
        raise

    # Adiciona as rotas
    app.include_router(transcribe.router, prefix="/transcribe", tags=["transcription"])
    app.include_router(health.router, prefix="/health", tags=["health"])
    
    return app

app = create_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)