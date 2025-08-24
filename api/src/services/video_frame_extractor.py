import os
import subprocess
from pathlib import Path
from typing import Optional, Dict, List
import shutil

from src.core.logger_config import get_logger

logger = get_logger(__name__)

class VideoFrameExtractor:
    """Serviço para extrair frames de arquivos de vídeo usando FFmpeg"""
    
    def __init__(self):
        self.supported_video_formats = {
            '.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv', 
            '.webm', '.m4v', '.3gp', '.mpg', '.mpeg'
        }
    
    def is_video_file(self, filename: str) -> bool:
        """Verifica se o arquivo é um formato de vídeo suportado"""
        return Path(filename).suffix.lower() in self.supported_video_formats
    
    def extract_frames(
        self, 
        video_path: str, 
        output_dir: str, 
        fps: float = 1.0,
        quality: int = 2,
        format: str = "jpg"
    ) -> Dict[str, any]:
        """
        Extrai frames de um arquivo de vídeo e salva como imagens
        
        Args:
            video_path: Caminho do arquivo de vídeo
            output_dir: Diretório onde salvar as imagens
            fps: Frames por segundo a extrair (default: 1.0 = 1 frame por segundo)
            quality: Qualidade das imagens JPEG (1-31, menor = melhor qualidade)
            format: Formato das imagens (jpg ou png)
            
        Returns:
            Dict com informações sobre a extração
        """
        try:
            # Verifica se o arquivo de vídeo existe
            if not os.path.exists(video_path):
                logger.error(f"Arquivo de vídeo não encontrado: {video_path}")
                return {"success": False, "error": "Arquivo de vídeo não encontrado"}
            
            # Cria o diretório de saída se não existir
            os.makedirs(output_dir, exist_ok=True)
            
            # Define o padrão de nome dos frames
            output_pattern = os.path.join(output_dir, f"frame_%06d.{format}")
            
            # Comando FFmpeg para extrair frames
            # -i: arquivo de entrada
            # -vf fps: filtro de video para definir FPS
            # -q:v: qualidade do vídeo (para JPEG)
            cmd = [
                'ffmpeg',
                '-i', video_path,
                '-vf', f'fps={fps}',
            ]
            
            # Adiciona parâmetros específicos do formato
            if format == "jpg":
                cmd.extend(['-q:v', str(quality)])
            elif format == "png":
                cmd.extend(['-compression_level', '0'])  # Sem compressão para PNG
            
            cmd.append(output_pattern)
            
            logger.info(f"Executando comando FFmpeg: {' '.join(cmd)}")
            
            # Executa o comando FFmpeg
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=600  # Timeout de 10 minutos
            )
            
            if result.returncode == 0:
                # Conta quantos frames foram extraídos
                frame_files = list(Path(output_dir).glob(f"frame_*.{format}"))
                frame_count = len(frame_files)
                
                logger.info(f"Frames extraídos com sucesso: {frame_count} frames em {output_dir}")
                
                # Obtém informações do vídeo
                video_info = self.get_video_info(video_path)
                
                return {
                    "success": True,
                    "frame_count": frame_count,
                    "output_dir": output_dir,
                    "fps_extracted": fps,
                    "format": format,
                    "video_info": video_info,
                    "frames": [str(f) for f in sorted(frame_files)]
                }
            else:
                logger.error(f"Erro no FFmpeg (código {result.returncode}): {result.stderr}")
                return {
                    "success": False,
                    "error": f"Erro no FFmpeg: {result.stderr}"
                }
                
        except subprocess.TimeoutExpired:
            logger.error(f"Timeout na extração de frames de {video_path}")
            return {
                "success": False,
                "error": "Timeout na extração de frames"
            }
        except Exception as e:
            logger.error(f"Erro inesperado na extração de frames: {str(e)}")
            return {
                "success": False,
                "error": f"Erro inesperado: {str(e)}"
            }
    
    def extract_frames_at_intervals(
        self,
        video_path: str,
        output_dir: str,
        interval_seconds: float = 1.0,
        format: str = "jpg",
        quality: int = 2
    ) -> Dict[str, any]:
        """
        Extrai frames em intervalos específicos
        
        Args:
            video_path: Caminho do arquivo de vídeo
            output_dir: Diretório onde salvar as imagens
            interval_seconds: Intervalo em segundos entre frames
            format: Formato das imagens
            quality: Qualidade das imagens
            
        Returns:
            Dict com informações sobre a extração
        """
        # Calcula FPS baseado no intervalo
        fps = 1.0 / interval_seconds
        return self.extract_frames(video_path, output_dir, fps, quality, format)
    
    def extract_key_frames(
        self,
        video_path: str,
        output_dir: str,
        format: str = "jpg",
        quality: int = 2
    ) -> Dict[str, any]:
        """
        Extrai apenas key frames (frames importantes) do vídeo
        
        Args:
            video_path: Caminho do arquivo de vídeo
            output_dir: Diretório onde salvar as imagens
            format: Formato das imagens
            quality: Qualidade das imagens
            
        Returns:
            Dict com informações sobre a extração
        """
        try:
            # Verifica se o arquivo de vídeo existe
            if not os.path.exists(video_path):
                logger.error(f"Arquivo de vídeo não encontrado: {video_path}")
                return {"success": False, "error": "Arquivo de vídeo não encontrado"}
            
            # Cria o diretório de saída se não existir
            os.makedirs(output_dir, exist_ok=True)
            
            # Define o padrão de nome dos frames
            output_pattern = os.path.join(output_dir, f"keyframe_%06d.{format}")
            
            # Comando FFmpeg para extrair apenas key frames
            cmd = [
                'ffmpeg',
                '-i', video_path,
                '-vf', 'select=eq(pict_type\\,I)',  # Seleciona apenas I-frames (key frames)
                '-vsync', 'vfr',  # Variable frame rate
            ]
            
            # Adiciona parâmetros específicos do formato
            if format == "jpg":
                cmd.extend(['-q:v', str(quality)])
            elif format == "png":
                cmd.extend(['-compression_level', '0'])
            
            cmd.append(output_pattern)
            
            logger.info(f"Executando comando FFmpeg para key frames: {' '.join(cmd)}")
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=600
            )
            
            if result.returncode == 0:
                frame_files = list(Path(output_dir).glob(f"keyframe_*.{format}"))
                frame_count = len(frame_files)
                
                logger.info(f"Key frames extraídos: {frame_count} frames")
                
                video_info = self.get_video_info(video_path)
                
                return {
                    "success": True,
                    "frame_count": frame_count,
                    "output_dir": output_dir,
                    "extraction_type": "keyframes",
                    "format": format,
                    "video_info": video_info,
                    "frames": [str(f) for f in sorted(frame_files)]
                }
            else:
                logger.error(f"Erro ao extrair key frames: {result.stderr}")
                return {
                    "success": False,
                    "error": f"Erro no FFmpeg: {result.stderr}"
                }
                
        except Exception as e:
            logger.error(f"Erro ao extrair key frames: {str(e)}")
            return {
                "success": False,
                "error": f"Erro inesperado: {str(e)}"
            }
    
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
                data = json.loads(result.stdout)
                
                # Extrai informações relevantes
                video_stream = next((s for s in data.get('streams', []) if s['codec_type'] == 'video'), None)
                
                if video_stream:
                    return {
                        'duration': float(data['format'].get('duration', 0)),
                        'width': video_stream.get('width'),
                        'height': video_stream.get('height'),
                        'fps': eval(video_stream.get('r_frame_rate', '0/1')),
                        'codec': video_stream.get('codec_name'),
                        'total_frames': int(video_stream.get('nb_frames', 0)),
                        'format': data['format'].get('format_name'),
                        'size': int(data['format'].get('size', 0))
                    }
                return None
                
        except Exception as e:
            logger.error(f"Erro ao obter informações do vídeo: {str(e)}")
            return None
    
    def cleanup_output_dir(self, output_dir: str) -> bool:
        """
        Remove um diretório de saída e todo seu conteúdo
        
        Args:
            output_dir: Diretório a ser removido
            
        Returns:
            bool: True se removido com sucesso
        """
        try:
            if os.path.exists(output_dir):
                shutil.rmtree(output_dir)
                logger.info(f"Diretório removido: {output_dir}")
                return True
            return False
        except Exception as e:
            logger.error(f"Erro ao remover diretório: {str(e)}")
            return False