import os
import subprocess
from pathlib import Path
from typing import Optional

from src.core.logger_config import get_logger

logger = get_logger(__name__)

class VideoAudioExtractor:
    """Serviço para extrair áudio de arquivos de vídeo usando FFmpeg"""
    
    def __init__(self):
        self.supported_video_formats = {
            '.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv', 
            '.webm', '.m4v', '.3gp', '.mpg', '.mpeg'
        }
    
    def is_video_file(self, filename: str) -> bool:
        """Verifica se o arquivo é um formato de vídeo suportado"""
        return Path(filename).suffix.lower() in self.supported_video_formats
    
    def extract_audio(self, video_path: str, output_path: str) -> bool:
        """
        Extrai áudio de um arquivo de vídeo e salva como WAV
        
        Args:
            video_path: Caminho do arquivo de vídeo
            output_path: Caminho onde salvar o arquivo WAV
            
        Returns:
            bool: True se a extração foi bem-sucedida, False caso contrário
        """
        try:
            # Verifica se o arquivo de vídeo existe
            if not os.path.exists(video_path):
                logger.error(f"Arquivo de vídeo não encontrado: {video_path}")
                return False
            
            # Cria o diretório de saída se não existir
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Comando FFmpeg para extrair áudio como WAV
            # -i: arquivo de entrada
            # -vn: não incluir vídeo
            # -acodec pcm_s16le: codec de áudio WAV
            # -ar 16000: sample rate 16kHz (ideal para transcrição)
            # -ac 1: mono (1 canal)
            # -y: sobrescrever arquivo de saída se existir
            cmd = [
                'ffmpeg',
                '-i', video_path,
                '-vn',  # Sem vídeo
                '-acodec', 'pcm_s16le',  # Codec WAV
                '-ar', '16000',  # Sample rate 16kHz
                '-ac', '1',  # Mono
                '-y',  # Sobrescrever
                output_path
            ]
            
            logger.info(f"Executando comando FFmpeg: {' '.join(cmd)}")
            
            # Executa o comando FFmpeg
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300  # Timeout de 5 minutos
            )
            
            if result.returncode == 0:
                logger.info(f"Áudio extraído com sucesso: {output_path}")
                
                # Verifica se o arquivo foi criado e tem tamanho > 0
                if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                    logger.info(f"Arquivo de áudio criado com {os.path.getsize(output_path)} bytes")
                    return True
                else:
                    logger.error("Arquivo de áudio não foi criado ou está vazio")
                    return False
            else:
                logger.error(f"Erro no FFmpeg (código {result.returncode}): {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            logger.error(f"Timeout na extração de áudio de {video_path}")
            return False
        except Exception as e:
            logger.error(f"Erro inesperado na extração de áudio: {str(e)}")
            return False
    
    def get_video_info(self, video_path: str) -> Optional[dict]:
        """
        Obtém informações sobre o arquivo de vídeo
        
        Args:
            video_path: Caminho do arquivo de vídeo
            
        Returns:
            dict: Informações do vídeo ou None se erro
        """
        try:
            cmd = [
                'ffprobe',
                '-v', 'quiet',
                '-print_format', 'json',
                '-show_format',
                '-show_streams',
                video_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                import json
                return json.loads(result.stdout)
            else:
                logger.error(f"Erro ao obter informações do vídeo: {result.stderr}")
                return None
                
        except Exception as e:
            logger.error(f"Erro ao obter informações do vídeo: {str(e)}")
            return None