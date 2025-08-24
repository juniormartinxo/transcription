import os
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Optional, Set

from dotenv import load_dotenv
from pydantic import BaseModel, ConfigDict

from src.core.logger_config import get_logger

logger = get_logger(__name__)

load_dotenv()

class ModelSize(str, Enum):
    TINY = "tiny"
    TINY_EN = "tiny.en"
    BASE = "base"
    BASE_EN = "base.en"
    SMALL = "small"
    SMALL_EN = "small.en"
    MEDIUM = "medium"
    MEDIUM_EN = "medium.en"
    LARGE = "large"
    LARGE_V1 = "large-v1"
    LARGE_V2 = "large-v2"
    LARGE_V3 = "large-v3"
    DISTIL_LARGE_V2 = "distil-large-v2"
    DISTIL_MEDIUM_EN = "distil-medium.en"
    DISTIL_SMALL_EN = "distil-small.en"

class AppConfig(BaseModel):
    """
    Classe de configuração da aplicação
    """
    hf_token: str
    audios_dir: Path = Path("../public/audios")
    transcriptions_dir: Path = Path("../public/transcriptions")
    version_model: ModelSize = ModelSize.LARGE_V3  # Using latest large model as default
    force_cpu: bool = True
    max_file_size: int = 100 * 1024 * 1024  # 100MB
    allowed_extensions: Set[str] = {"audio/mp3", "audio/wav", "audio/ogg", "audio/m4a", "audio/flac", "audio/aac", "audio/x-wav"}
    
    model_config = ConfigDict(protected_namespaces=())
    
    @classmethod
    def from_env(cls) -> 'AppConfig':
        """
        Carrega configuração das variáveis de ambiente
        """
        hf_token = os.getenv('HUGGING_FACE_HUB_TOKEN')
        if not hf_token:
            raise ValueError(
                "Token do HuggingFace não encontrado. "
                "Configure a variável HUGGING_FACE_HUB_TOKEN no arquivo .env"
            )
        
        # Handle legacy 'turbo' model name
        model_env = os.getenv('VERSION_MODEL', 'large-v3')
        if model_env == 'turbo':
            model_env = 'large-v3'  # Map turbo to large-v3
        
        return cls(
            hf_token=hf_token,
            audios_dir=Path(os.getenv('AUDIOS_DIR', '../public/audios')),
            transcriptions_dir=Path(os.getenv('TRANSCRIPTIONS_DIR', '../public/transcriptions')),
            version_model=model_env,
            force_cpu=os.getenv('FORCE_CPU', 'false').lower() == 'true'
        )
        
    def get_audio_path(self, filename: str) -> Path:
        """Retorna o caminho completo para um arquivo de áudio"""
        return self.audios_dir / filename
    
    def get_transcription_path(self, filename: str, format: str = 'txt') -> Path:
        """Retorna o caminho completo para um arquivo de transcrição"""
        base_name = Path(filename).stem
        return self.transcriptions_dir / f"{base_name}.{format}"
    
    def is_file_allowed(self, filename: str) -> bool:
        """Verifica se o arquivo tem uma extensão permitida"""
        return Path(filename).suffix.lower().lstrip('.') in self.allowed_extensions

# Função singleton para obter as configurações
_config_instance = None

def get_settings() -> AppConfig:
    global _config_instance
    if _config_instance is None:
        _config_instance = AppConfig.from_env()
    return _config_instance