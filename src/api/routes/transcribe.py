import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import List

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, UploadFile
from fastapi.encoders import jsonable_encoder
from fastapi.responses import FileResponse, JSONResponse

from src.config.config import get_settings
from src.core.logger_config import get_logger
from src.models.schemas import (
    TranscriptionListResponse,
    TranscriptionRequest,
    TranscriptionStatus,
    TranscriptionTask,
)
from src.services.transcription import TranscriptionService
from src.services.video_extractor import VideoAudioExtractor

logger = get_logger(__name__)

router = APIRouter()

def get_transcription_service():
    settings = get_settings()
    return TranscriptionService(settings)

@router.get("/test")
async def test_endpoint():
    """Endpoint de teste para verificar se a rota está funcionando"""
    return {"message": "Endpoint de transcrição funcionando!", "status": "ok"}

@router.post("", response_model=TranscriptionTask)
@router.post("/", response_model=TranscriptionTask) 
async def transcribe_audio(
    file: UploadFile,
    background_tasks: BackgroundTasks,
    service: TranscriptionService = Depends(get_transcription_service),
    include_timestamps: bool = True,
    include_speaker_diarization: bool = True,
    output_format: str = "txt",
    force_cpu: bool = None,
    version_model: str = None
):
    """
    Inicia uma nova tarefa de transcrição de áudio
    """
    try:
        config = service.config
        
        logger.info(f"Recebendo arquivo: {file.filename}")
        logger.info(f"Tipo recebido: {file.content_type}")
        logger.info(f"Tipos permitidos: {config.allowed_extensions}")
        
        # Validação do arquivo
        if not file.filename or not file.file:
            raise HTTPException(
                status_code=400,
                detail="Arquivo de áudio inválido"
            )
        
        # Validação mais flexível do tipo do arquivo
        allowed_types = config.allowed_extensions
        file_extension = Path(file.filename).suffix.lower()
        
        # Mapeamento de extensões para tipos MIME
        extension_to_mime = {
            '.wav': 'audio/wav',
            '.mp3': 'audio/mp3', 
            '.ogg': 'audio/ogg',
            '.m4a': 'audio/m4a',
            '.flac': 'audio/flac',
            '.aac': 'audio/aac'
        }
        
        expected_mime = extension_to_mime.get(file_extension)
        
        # Aceita se o content_type está correto OU se a extensão é válida
        if file.content_type not in allowed_types and expected_mime not in allowed_types:
            raise HTTPException(
                status_code=400,
                detail=f"Tipo de arquivo não suportado. Tipos permitidos: {', '.join(allowed_types)}. Recebido: {file.content_type}"
            )
        
        # Antes da validação, precisamos ler o tamanho do arquivo
        file_size = 0
        file.file.seek(0, 2)  # Vai para o final do arquivo
        file_size = file.file.tell()  # Pega a posição atual (tamanho)
        file.file.seek(0)  # Volta para o início do arquivo
        
        # Validação do tamanho do arquivo
        if file_size > config.max_file_size:
            raise HTTPException(
                status_code=400,
                detail=f"Tamanho do arquivo excede o limite de {config.max_file_size} bytes"
            )
    
        # Validação do arquivo
        if not file.filename or not file.file:
            raise HTTPException(
                status_code=400,
                detail="Arquivo de áudio inválido"
            )
            
        # Cria diretório se não existir
        os.makedirs(service.config.audios_dir, exist_ok=True)
        
        task_id = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{os.urandom(4).hex()}"
        audio_path = Path(service.config.audios_dir) / f"{task_id}_{file.filename}"
        
        try:
            # Garantir que o arquivo está no início
            await file.seek(0)
            
            # Ler o conteúdo do arquivo
            contents = await file.read()
            
            logger.info(f"Arquivo lido com sucesso. Tamanho: {len(contents)} bytes")
            
            # Salvar o arquivo
            with open(audio_path, "wb") as buffer:
                buffer.write(contents)
                
            logger.info(f"Arquivo salvo com sucesso: {audio_path}")
            
            # Verificar se o arquivo foi salvo corretamente
            if not os.path.exists(audio_path):
                raise Exception("Arquivo não foi salvo corretamente")
                
            file_size = os.path.getsize(audio_path)
            logger.info(f"Arquivo salvo com tamanho: {file_size} bytes")
            
        except Exception as e:
            logger.error(f"Erro detalhado ao salvar arquivo: {str(e)}")
            logger.error(f"Tipo de erro: {type(e).__name__}")
            raise HTTPException(
                status_code=500,
                detail=f"Erro ao salvar arquivo de áudio: {str(e)}"
            )
        
        task = service.create_task(task_id, file.filename)
        
        background_tasks.add_task(
            service.process_transcription,
            task_id=task_id,
            audio_path=str(audio_path),
            output_format=output_format,
            force_cpu=force_cpu if force_cpu is not None else config.force_cpu,
            version_model=version_model or config.version_model,
            include_timestamps=include_timestamps,
            include_speaker_diarization=include_speaker_diarization
        )
        
        serialized_task = jsonable_encoder(task)
        return JSONResponse(status_code=202, content=serialized_task)
        
    except Exception as e:
        logger.error(f"Erro ao processar transcrição: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{task_id}", response_model=TranscriptionTask)
async def get_transcription_status(
    task_id: str,
    service: TranscriptionService = Depends(get_transcription_service)
):
    """
    Retorna o status de uma transcrição específica
    """
    try:
        task_info = service.get_task_status(task_id)
        if task_info is None:
            raise HTTPException(
                status_code=404,
                detail="Tarefa não encontrada"
            )
        return task_info
    except Exception as e:
        logger.error(f"Erro ao buscar status da tarefa: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{task_id}/download")
async def download_transcription(
    task_id: str,
    service: TranscriptionService = Depends(get_transcription_service)
):
    """
    Faz download do arquivo de transcrição
    """
    try:
        task_info = service.get_task_status(task_id)
        if not task_info:
            raise HTTPException(
                status_code=404,
                detail="Tarefa não encontrada"
            )
            
        if task_info.status != TranscriptionStatus.COMPLETED:
            raise HTTPException(
                status_code=400,
                detail="Transcrição ainda não está completa"
            )
            
        if not task_info.output_file or not os.path.exists(task_info.output_file):
            raise HTTPException(
                status_code=404,
                detail="Arquivo de transcrição não encontrado"
            )
            
        return FileResponse(
            path=task_info.output_file,
            filename=os.path.basename(task_info.output_file),
            media_type="text/plain"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao fazer download da transcrição: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/", response_model=TranscriptionListResponse)
async def list_transcriptions(
    service: TranscriptionService = Depends(get_transcription_service)
):
    """
    Lista todas as transcrições
    """
    try:
        tasks = service.list_tasks()
        return TranscriptionListResponse(
            tasks=tasks,
            total=len(tasks)
        )
    except Exception as e:
        logger.error(f"Erro ao listar transcrições: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/extract-audio")
async def extract_audio_from_video(
    file: UploadFile,
    background_tasks: BackgroundTasks,
    service: TranscriptionService = Depends(get_transcription_service)
):
    """
    Extrai áudio de um arquivo de vídeo e retorna como WAV
    """
    try:
        extractor = VideoAudioExtractor()
        
        # Validação do arquivo
        if not file.filename or not file.file:
            raise HTTPException(
                status_code=400,
                detail="Arquivo de vídeo inválido"
            )
        
        # Verifica se é um arquivo de vídeo suportado
        if not extractor.is_video_file(file.filename):
            raise HTTPException(
                status_code=400,
                detail=f"Formato de vídeo não suportado. Formatos suportados: {', '.join(extractor.supported_video_formats)}"
            )
        
        # Validação do tamanho do arquivo
        file.file.seek(0, 2)
        file_size = file.file.tell()
        file.file.seek(0)
        
        max_size = 500 * 1024 * 1024  # 500MB para vídeos
        if file_size > max_size:
            raise HTTPException(
                status_code=400,
                detail=f"Tamanho do arquivo excede o limite de {max_size} bytes"
            )
        
        # Cria diretórios se não existirem
        videos_dir = Path(service.config.audios_dir).parent / "videos"
        os.makedirs(videos_dir, exist_ok=True)
        os.makedirs(service.config.audios_dir, exist_ok=True)
        
        # Gera nomes únicos para os arquivos
        task_id = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{os.urandom(4).hex()}"
        video_path = videos_dir / f"{task_id}_{file.filename}"
        audio_filename = f"{task_id}_{Path(file.filename).stem}.wav"
        audio_path = Path(service.config.audios_dir) / audio_filename
        
        try:
            # Salva o arquivo de vídeo temporariamente
            contents = await file.read()
            with open(video_path, "wb") as buffer:
                buffer.write(contents)
            
            logger.info(f"Vídeo salvo: {video_path}")
            
            # Extrai o áudio
            success = extractor.extract_audio(str(video_path), str(audio_path))
            
            if not success:
                raise HTTPException(
                    status_code=500,
                    detail="Falha na extração do áudio do vídeo"
                )
            
            # Remove o arquivo de vídeo temporário
            try:
                os.remove(video_path)
                logger.info(f"Arquivo de vídeo temporário removido: {video_path}")
            except Exception as e:
                logger.warning(f"Não foi possível remover o arquivo temporário: {e}")
            
            # Gera 4 transcrições automaticamente com diferentes configurações
            transcription_tasks = []
            
            # Configurações das 4 transcrições
            configs = [
                {"timestamps": False, "diarization": False, "suffix": "limpa"},
                {"timestamps": True, "diarization": False, "suffix": "timestamps"},
                {"timestamps": False, "diarization": True, "suffix": "diarization"},
                {"timestamps": True, "diarization": True, "suffix": "completa"}
            ]
            
            for config in configs:
                transcription_task_id = f"{task_id}_{config['suffix']}"
                task = service.create_task(transcription_task_id, audio_filename)
                
                # Adiciona tarefa de transcrição em background
                background_tasks.add_task(
                    service.process_transcription,
                    task_id=transcription_task_id,
                    audio_path=str(audio_path),
                    output_format="txt",
                    force_cpu=service.config.force_cpu,
                    version_model=service.config.version_model,
                    include_timestamps=config["timestamps"],
                    include_speaker_diarization=config["diarization"]
                )
                
                transcription_tasks.append({
                    "task_id": transcription_task_id,
                    "type": config["suffix"],
                    "timestamps": config["timestamps"],
                    "diarization": config["diarization"],
                    "status": "pending"
                })
                
                logger.info(f"Transcrição {config['suffix']} criada: {transcription_task_id}")
            
            # Retorna mensagem de sucesso com informações do arquivo e transcrições
            return JSONResponse(
                status_code=200,
                content={
                    "message": "Áudio extraído com sucesso e transcrições iniciadas",
                    "audio_filename": audio_filename,
                    "audio_path": str(audio_path),
                    "file_size_bytes": os.path.getsize(audio_path),
                    "original_video": file.filename,
                    "transcription_tasks": transcription_tasks,
                    "total_transcriptions": len(transcription_tasks)
                }
            )
            
        except Exception as e:
            # Limpa arquivos temporários em caso de erro
            for temp_file in [video_path, audio_path]:
                try:
                    if os.path.exists(temp_file):
                        os.remove(temp_file)
                except:
                    pass
                    
            logger.error(f"Erro ao extrair áudio: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Erro ao extrair áudio do vídeo: {str(e)}"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro inesperado ao extrair áudio: {e}")
        raise HTTPException(status_code=500, detail=str(e))