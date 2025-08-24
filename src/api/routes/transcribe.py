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
    BatchUploadResponse,
    BatchUploadTask,
)
from src.services.transcription import TranscriptionService
from src.services.video_extractor import VideoAudioExtractor
from src.services.video_frame_extractor import VideoFrameExtractor

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
            
        # Cria diretório base se não existir
        os.makedirs(service.config.audios_dir, exist_ok=True)
        
        task_id = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{os.urandom(4).hex()}"
        
        # Cria subpasta para o áudio
        audio_subfolder = Path(service.config.audios_dir) / task_id
        audio_subfolder.mkdir(parents=True, exist_ok=True)
        
        audio_path = audio_subfolder / file.filename
        
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
        
        # Cria subpasta para o áudio extraído
        audio_subfolder = Path(service.config.audios_dir) / task_id
        audio_subfolder.mkdir(parents=True, exist_ok=True)
        
        audio_filename = f"{Path(file.filename).stem}.wav"
        audio_path = audio_subfolder / audio_filename
        
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
                    include_speaker_diarization=config["diarization"],
                    base_task_id=task_id,  # Usa o task_id base para a pasta
                    transcription_suffix=config["suffix"]  # Sufixo para o nome do arquivo
                )
                
                # Adiciona o objeto TranscriptionTask completo com metadados adicionais
                task_dict = jsonable_encoder(task)
                task_dict.update({
                    "type": config["suffix"],
                    "timestamps": config["timestamps"],
                    "diarization": config["diarization"]
                })
                transcription_tasks.append(task_dict)
                
                logger.info(f"Transcrição {config['suffix']} criada: {transcription_task_id}")
            
            # Retorna mensagem de sucesso com informações do arquivo e transcrições
            return JSONResponse(
                status_code=200,
                content={
                    "message": "Áudio extraído com sucesso e transcrições iniciadas",
                    "audio": {
                        "filename": audio_filename,
                        "path": str(audio_path),
                        "size_bytes": os.path.getsize(audio_path),
                        "original_video": file.filename
                    },
                    "transcriptions": transcription_tasks,
                    "summary": {
                        "total": len(transcription_tasks),
                        "types": [config["suffix"] for config in configs]
                    }
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

@router.post("/extract-frames")
async def extract_frames_from_video(
    file: UploadFile,
    fps: float = 1.0,
    interval_seconds: float = None,
    extract_keyframes: bool = False,
    format: str = "jpg",
    quality: int = 2,
    service: TranscriptionService = Depends(get_transcription_service)
):
    """
    Extrai frames de um arquivo de vídeo e salva como imagens
    
    Args:
        file: Arquivo de vídeo
        fps: Frames por segundo a extrair (padrão: 1.0)
        interval_seconds: Intervalo em segundos entre frames (alternativa ao fps)
        extract_keyframes: Se True, extrai apenas key frames
        format: Formato das imagens (jpg ou png)
        quality: Qualidade das imagens JPEG (1-31, menor = melhor qualidade)
    """
    try:
        extractor = VideoFrameExtractor()
        
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
        
        # Validação dos parâmetros
        if format not in ["jpg", "png"]:
            raise HTTPException(
                status_code=400,
                detail="Formato deve ser 'jpg' ou 'png'"
            )
        
        if quality < 1 or quality > 31:
            raise HTTPException(
                status_code=400,
                detail="Qualidade deve estar entre 1 e 31"
            )
        
        # Cria diretórios
        sequencies_dir = Path("public/sequencies")
        sequencies_dir.mkdir(parents=True, exist_ok=True)
        
        videos_dir = Path(service.config.audios_dir).parent / "videos"
        videos_dir.mkdir(parents=True, exist_ok=True)
        
        # Gera nomes únicos
        task_id = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{os.urandom(4).hex()}"
        video_path = videos_dir / f"{task_id}_{file.filename}"
        output_dir = sequencies_dir / f"{task_id}_{Path(file.filename).stem}"
        
        try:
            # Salva o arquivo de vídeo temporariamente
            contents = await file.read()
            with open(video_path, "wb") as buffer:
                buffer.write(contents)
            
            logger.info(f"Vídeo salvo: {video_path}")
            
            # Extrai os frames
            if extract_keyframes:
                result = extractor.extract_key_frames(
                    str(video_path),
                    str(output_dir),
                    format=format,
                    quality=quality
                )
            elif interval_seconds:
                result = extractor.extract_frames_at_intervals(
                    str(video_path),
                    str(output_dir),
                    interval_seconds=interval_seconds,
                    format=format,
                    quality=quality
                )
            else:
                result = extractor.extract_frames(
                    str(video_path),
                    str(output_dir),
                    fps=fps,
                    quality=quality,
                    format=format
                )
            
            # Remove o arquivo de vídeo temporário
            try:
                os.remove(video_path)
                logger.info(f"Arquivo de vídeo temporário removido: {video_path}")
            except Exception as e:
                logger.warning(f"Não foi possível remover o arquivo temporário: {e}")
            
            if not result["success"]:
                # Limpa o diretório de saída em caso de erro
                extractor.cleanup_output_dir(str(output_dir))
                raise HTTPException(
                    status_code=500,
                    detail=result.get("error", "Falha na extração de frames")
                )
            
            # Retorna informações sobre a extração
            return JSONResponse(
                status_code=200,
                content={
                    "message": "Frames extraídos com sucesso",
                    "task_id": task_id,
                    "extraction": {
                        "frame_count": result["frame_count"],
                        "output_dir": str(output_dir),
                        "fps_extracted": result.get("fps_extracted", fps),
                        "format": format,
                        "quality": quality,
                        "extraction_type": result.get("extraction_type", "regular"),
                        "video_info": result.get("video_info")
                    },
                    "original_video": {
                        "filename": file.filename,
                        "size_bytes": file_size
                    }
                }
            )
            
        except Exception as e:
            # Limpa arquivos temporários em caso de erro
            for temp_file in [video_path]:
                try:
                    if os.path.exists(temp_file):
                        os.remove(temp_file)
                except:
                    pass
            
            # Limpa diretório de saída se foi criado
            if os.path.exists(output_dir):
                extractor.cleanup_output_dir(str(output_dir))
                    
            logger.error(f"Erro ao extrair frames: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Erro ao extrair frames do vídeo: {str(e)}"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro inesperado ao extrair frames: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{task_id}/cancel")
async def cancel_transcription(
    task_id: str,
    service: TranscriptionService = Depends(get_transcription_service)
):
    """
    Cancela uma tarefa de transcrição em andamento
    """
    try:
        cancelled_task = service.cancel_task(task_id)
        if not cancelled_task:
            raise HTTPException(
                status_code=404,
                detail="Tarefa não encontrada ou não pode ser cancelada"
            )
        
        return {
            "message": f"Tarefa {task_id} cancelada com sucesso",
            "task": cancelled_task
        }
    except Exception as e:
        logger.error(f"Erro ao cancelar tarefa: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{task_id}")
async def delete_transcription(
    task_id: str,
    delete_files: bool = True,
    service: TranscriptionService = Depends(get_transcription_service)
):
    """
    Exclui uma tarefa de transcrição e, opcionalmente, seus arquivos
    
    Query parameters:
    - delete_files: Se True (padrão), remove também os arquivos associados
    """
    try:
        success = service.delete_task(task_id, delete_files)
        if not success:
            raise HTTPException(
                status_code=404,
                detail="Tarefa não encontrada"
            )
        
        return {
            "message": f"Tarefa {task_id} excluída com sucesso",
            "deleted_files": delete_files
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao excluir tarefa: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{task_id}/files")
async def get_task_files(
    task_id: str,
    service: TranscriptionService = Depends(get_transcription_service)
):
    """
    Retorna informações sobre os arquivos associados a uma tarefa
    """
    try:
        files_info = service.get_task_files_info(task_id)
        if not files_info:
            raise HTTPException(
                status_code=404,
                detail="Tarefa não encontrada"
            )
        
        return files_info
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao obter informações dos arquivos: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/batch-audio", response_model=BatchUploadResponse)
async def batch_upload_audio(
    files: List[UploadFile],
    background_tasks: BackgroundTasks,
    service: TranscriptionService = Depends(get_transcription_service),
    include_timestamps: bool = True,
    include_speaker_diarization: bool = True,
    output_format: str = "txt",
    force_cpu: bool = None,
    version_model: str = None
):
    """
    Upload múltiplo de arquivos de áudio para transcrição em lote
    """
    try:
        if not files:
            raise HTTPException(
                status_code=400,
                detail="Nenhum arquivo foi enviado"
            )
        
        if len(files) > 10:  # Limite de arquivos por lote
            raise HTTPException(
                status_code=400,
                detail="Máximo de 10 arquivos por lote"
            )
        
        # Gera ID do lote
        batch_id = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{os.urandom(4).hex()}"
        
        batch_tasks: List[BatchUploadTask] = []
        config = service.config
        
        # Processa cada arquivo
        for file in files:
            batch_task = BatchUploadTask(
                filename=file.filename,
                file_size=file.size if hasattr(file, 'size') else 0
            )
            
            try:
                # Validação do arquivo
                if not file.filename or not file.file:
                    batch_task.error = "Arquivo inválido"
                    batch_task.status = "failed"
                    batch_tasks.append(batch_task)
                    continue
                
                # Validação do tipo de arquivo
                file_extension = Path(file.filename).suffix.lower()
                extension_to_mime = {
                    '.wav': 'audio/wav',
                    '.mp3': 'audio/mp3', 
                    '.ogg': 'audio/ogg',
                    '.m4a': 'audio/m4a',
                    '.flac': 'audio/flac',
                    '.aac': 'audio/aac'
                }
                
                expected_mime = extension_to_mime.get(file_extension)
                allowed_types = config.allowed_extensions
                
                if file.content_type not in allowed_types and expected_mime not in allowed_types:
                    batch_task.error = f"Tipo de arquivo não suportado: {file.content_type}"
                    batch_task.status = "failed"
                    batch_tasks.append(batch_task)
                    continue
                
                # Validação do tamanho do arquivo
                file.file.seek(0, 2)
                file_size = file.file.tell()
                file.file.seek(0)
                batch_task.file_size = file_size
                
                if file_size > config.max_file_size:
                    batch_task.error = f"Arquivo muito grande: {file_size} bytes"
                    batch_task.status = "failed"
                    batch_tasks.append(batch_task)
                    continue
                
                # Cria diretório e salva arquivo
                os.makedirs(service.config.audios_dir, exist_ok=True)
                task_id = f"{batch_id}_{len(batch_tasks):03d}_{datetime.now().strftime('%H%M%S')}"
                
                audio_subfolder = Path(service.config.audios_dir) / task_id
                audio_subfolder.mkdir(parents=True, exist_ok=True)
                audio_path = audio_subfolder / file.filename
                
                # Salva o arquivo
                contents = await file.read()
                with open(audio_path, "wb") as buffer:
                    buffer.write(contents)
                
                # Cria tarefa de transcrição
                task = service.create_task(task_id, file.filename)
                batch_task.task = task
                batch_task.status = "pending"
                
                # Adiciona à fila de processamento em background
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
                
                logger.info(f"Arquivo {file.filename} adicionado ao lote {batch_id} como task {task_id}")
                
            except Exception as e:
                logger.error(f"Erro ao processar arquivo {file.filename}: {str(e)}")
                batch_task.error = str(e)
                batch_task.status = "failed"
            
            batch_tasks.append(batch_task)
        
        # Conta arquivos processados
        successful_files = len([t for t in batch_tasks if t.status != "failed"])
        
        response = BatchUploadResponse(
            batch_id=batch_id,
            total_files=len(files),
            tasks=batch_tasks,
            message=f"Lote processado: {successful_files}/{len(files)} arquivos enviados com sucesso"
        )
        
        return JSONResponse(status_code=202, content=jsonable_encoder(response))
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro no upload em lote: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/batch-video", response_model=BatchUploadResponse)
async def batch_upload_video(
    files: List[UploadFile],
    background_tasks: BackgroundTasks,
    service: TranscriptionService = Depends(get_transcription_service)
):
    """
    Upload múltiplo de arquivos de vídeo para extração de áudio e transcrição em lote
    """
    try:
        if not files:
            raise HTTPException(
                status_code=400,
                detail="Nenhum arquivo foi enviado"
            )
        
        if len(files) > 5:  # Limite menor para vídeos (são maiores)
            raise HTTPException(
                status_code=400,
                detail="Máximo de 5 vídeos por lote"
            )
        
        # Gera ID do lote
        batch_id = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{os.urandom(4).hex()}"
        
        batch_tasks: List[BatchUploadTask] = []
        extractor = VideoAudioExtractor()
        
        # Processa cada arquivo
        for file in files:
            batch_task = BatchUploadTask(
                filename=file.filename,
                file_size=file.size if hasattr(file, 'size') else 0
            )
            
            try:
                # Validação do arquivo
                if not file.filename or not file.file:
                    batch_task.error = "Arquivo de vídeo inválido"
                    batch_task.status = "failed"
                    batch_tasks.append(batch_task)
                    continue
                
                # Verifica se é um arquivo de vídeo suportado
                if not extractor.is_video_file(file.filename):
                    batch_task.error = f"Formato de vídeo não suportado"
                    batch_task.status = "failed"
                    batch_tasks.append(batch_task)
                    continue
                
                # Validação do tamanho do arquivo
                file.file.seek(0, 2)
                file_size = file.file.tell()
                file.file.seek(0)
                batch_task.file_size = file_size
                
                max_size = 500 * 1024 * 1024  # 500MB para vídeos
                if file_size > max_size:
                    batch_task.error = f"Arquivo muito grande: {file_size} bytes (máximo: {max_size})"
                    batch_task.status = "failed"
                    batch_tasks.append(batch_task)
                    continue
                
                # Cria diretórios
                videos_dir = Path(service.config.audios_dir).parent / "videos"
                os.makedirs(videos_dir, exist_ok=True)
                os.makedirs(service.config.audios_dir, exist_ok=True)
                
                # Gera nomes únicos para os arquivos
                task_id = f"{batch_id}_{len(batch_tasks):03d}_{datetime.now().strftime('%H%M%S')}"
                video_path = videos_dir / f"{task_id}_{file.filename}"
                
                # Cria subpasta para o áudio extraído
                audio_subfolder = Path(service.config.audios_dir) / task_id
                audio_subfolder.mkdir(parents=True, exist_ok=True)
                
                audio_filename = f"{Path(file.filename).stem}.wav"
                audio_path = audio_subfolder / audio_filename
                
                # Salva o arquivo de vídeo temporariamente
                contents = await file.read()
                with open(video_path, "wb") as buffer:
                    buffer.write(contents)
                
                logger.info(f"Vídeo salvo: {video_path}")
                
                # Extrai o áudio
                success = extractor.extract_audio(str(video_path), str(audio_path))
                
                if not success:
                    batch_task.error = "Falha na extração do áudio do vídeo"
                    batch_task.status = "failed"
                    # Remove arquivo temporário
                    try:
                        os.remove(video_path)
                    except:
                        pass
                    batch_tasks.append(batch_task)
                    continue
                
                # Remove o arquivo de vídeo temporário
                try:
                    os.remove(video_path)
                    logger.info(f"Arquivo de vídeo temporário removido: {video_path}")
                except Exception as e:
                    logger.warning(f"Não foi possível remover o arquivo temporário: {e}")
                
                # Cria tarefa principal (vamos usar apenas a transcrição limpa para o lote)
                task = service.create_task(f"{task_id}_limpa", audio_filename)
                batch_task.task = task
                batch_task.status = "pending"
                
                # Adiciona tarefa de transcrição em background (apenas versão limpa)
                background_tasks.add_task(
                    service.process_transcription,
                    task_id=f"{task_id}_limpa",
                    audio_path=str(audio_path),
                    output_format="txt",
                    force_cpu=service.config.force_cpu,
                    version_model=service.config.version_model,
                    include_timestamps=False,
                    include_speaker_diarization=False,
                    base_task_id=task_id,
                    transcription_suffix="limpa"
                )
                
                logger.info(f"Vídeo {file.filename} processado e adicionado ao lote {batch_id}")
                
            except Exception as e:
                logger.error(f"Erro ao processar vídeo {file.filename}: {str(e)}")
                batch_task.error = str(e)
                batch_task.status = "failed"
            
            batch_tasks.append(batch_task)
        
        # Conta arquivos processados
        successful_files = len([t for t in batch_tasks if t.status != "failed"])
        
        response = BatchUploadResponse(
            batch_id=batch_id,
            total_files=len(files),
            tasks=batch_tasks,
            message=f"Lote de vídeos processado: {successful_files}/{len(files)} arquivos enviados com sucesso"
        )
        
        return JSONResponse(status_code=202, content=jsonable_encoder(response))
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro no upload em lote de vídeos: {e}")
        raise HTTPException(status_code=500, detail=str(e))