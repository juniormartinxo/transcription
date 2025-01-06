# run.py
from transcription import AudioTranscriber
import os
import logging
from typing import Optional
from dataclasses import dataclass

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class Config:
    """Classe para configuração da aplicação"""
    hf_token: str
    version_model: str
    force_cpu: bool
    audios_dir: str
    transcriptions_dir: str
    
    @classmethod
    def from_env(cls) -> 'Config':
        """
        Carrega configuração das variáveis de ambiente com valores padrão
        
        Returns:
            Config: Configuração carregada
            
        Raises:
            ValueError: Se HF_TOKEN não estiver definido
        """
        hf_token = os.getenv('HUGGING_FACE_HUB_TOKEN')
        if not hf_token:
            raise ValueError(
                "Token do HuggingFace não encontrado. "
                "Configure a variável de ambiente HUGGING_FACE_HUB_TOKEN"
            )
            
        return cls(
            hf_token=hf_token,
            version_model=os.getenv('VERSION_MODEL', 'base'),
            force_cpu=os.getenv('FORCE_CPU', 'true').lower() == 'true',
            audios_dir=os.getenv('AUDIOS_DIR', 'audios'),
            transcriptions_dir=os.getenv('TRANSCRIPTIONS_DIR', 'transcriptions')
        )

def ensure_directories(config: Config) -> None:
    """Garante que os diretórios necessários existem"""
    os.makedirs(config.audios_dir, exist_ok=True)
    os.makedirs(config.transcriptions_dir, exist_ok=True)

def get_audio_file(audio_dir: str) -> str:
    """
    Encontra o primeiro arquivo de áudio no diretório
    
    Args:
        audio_dir: Diretório onde procurar
        
    Returns:
        str: Caminho do arquivo de áudio
        
    Raises:
        FileNotFoundError: Se nenhum arquivo de áudio for encontrado
    """
    audio_extensions = {'.wav', '.mp3', '.m4a', '.flac'}
    
    for file in os.listdir(audio_dir):
        if any(file.lower().endswith(ext) for ext in audio_extensions):
            return os.path.join(audio_dir, file)
            
    raise FileNotFoundError(
        f"Nenhum arquivo de áudio encontrado em: {audio_dir}\n"
        f"Formatos suportados: {', '.join(audio_extensions)}"
    )

def main():
    try:
        # Carregar configuração
        config = Config.from_env()
        logger.info(f"Configuração carregada: {config}")
        
        # Verificar diretórios
        ensure_directories(config)
        
        # Encontrar arquivo de áudio
        audio_path = get_audio_file(config.audios_dir)
        logger.info(f"Arquivo de áudio encontrado: {audio_path}")
        
        # Inicializar transcritor
        transcriber = AudioTranscriber(
            version_model=config.version_model,
            hf_token=config.hf_token,
            force_cpu=config.force_cpu
        )

        # Realizar transcrição
        output_file = transcriber.transcribe(
            audio_path=audio_path,
            output_dir=config.transcriptions_dir
        )
        
        logger.info("Transcrição concluída com sucesso!")
        logger.info(f"Arquivo de saída: {output_file}")
        
    except FileNotFoundError as fe:
        logger.error(f"Erro de arquivo: {str(fe)}")
    except ValueError as ve:
        logger.error(f"Erro de configuração: {str(ve)}")
    except Exception as e:
        logger.error(f"Erro inesperado: {str(e)}")
        logger.error("Stack trace completo:", exc_info=True)

if __name__ == "__main__":
    main()