import json
import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from src.config.config import AppConfig, get_settings
from src.core.logger_config import get_logger
from src.models.schemas import OutputFormat, TranscriptionStatus, TranscriptionTask
from src.services.audio_transcriber import AudioTranscriber

logger = get_logger(__name__)

class TranscriptionService:
    def __init__(self, config: AppConfig):
        self.config = config
        self.transcriber = None
        
        # Usar diretório temporário se não conseguir escrever no diretório configurado
        try:
            self.tasks_file = Path(self.config.transcriptions_dir) / "tasks.json"
            # Testar se consegue escrever
            self.tasks_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.tasks_file, 'a') as f:
                pass
        except (PermissionError, OSError):
            # Usar diretório temporário
            import tempfile
            temp_dir = Path(tempfile.gettempdir()) / "transcription_tasks"
            temp_dir.mkdir(exist_ok=True)
            self.tasks_file = temp_dir / "tasks.json"
            logger.warning(f"Usando diretório temporário para tasks: {self.tasks_file}")
        
        self._tasks: Dict[str, TranscriptionTask] = {}
        self._load_tasks()
        self._ensure_directories()


    def _deserialize_task(self, task_data: dict) -> TranscriptionTask:
        """Converte datas string ISO para datetime"""
        if 'created_at' in task_data and task_data['created_at']:
            task_data['created_at'] = datetime.fromisoformat(task_data['created_at'])
        if 'completed_at' in task_data and task_data['completed_at']:
            task_data['completed_at'] = datetime.fromisoformat(task_data['completed_at'])
        return TranscriptionTask(**task_data)

    def _serialize_datetime(self, obj):
        """Serializa objetos datetime para JSON"""
        if isinstance(obj, datetime):
            return obj.isoformat()
        raise TypeError(f"Object of type {type(obj)} is not JSON serializable")

    def _load_tasks(self):
        """Carrega tarefas do arquivo JSON"""
        try:
            if self.tasks_file.exists():
                with open(self.tasks_file, 'r', encoding='utf-8') as f:
                    tasks_data = json.load(f)
                    self._tasks = {
                        task_id: self._deserialize_task(task_data)
                        for task_id, task_data in tasks_data.items()
                    }
                logger.info(f"Carregadas {len(self._tasks)} tarefas do arquivo")
        except Exception as e:
            logger.error(f"Erro ao carregar tarefas: {e}")
            self._tasks = {}

    def _save_tasks(self):
        """Salva tarefas no arquivo JSON"""
        try:
            # Garantir que o diretório existe
            self.tasks_file.parent.mkdir(parents=True, exist_ok=True)
            
            tasks_data = {
                task_id: task.dict(exclude_none=True)
                for task_id, task in self._tasks.items()
            }
            with open(self.tasks_file, 'w', encoding='utf-8') as f:
                json.dump(
                    tasks_data,
                    f,
                    ensure_ascii=False,
                    indent=2,
                    default=self._serialize_datetime
                )
            logger.info(f"Tarefas salvas com sucesso: {len(self._tasks)} tarefas")
        except Exception as e:
            logger.error(f"Erro ao salvar tarefas: {str(e)}")
            logger.error(f"Arquivo: {self.tasks_file}")
            logger.error(f"Diretório existe: {self.tasks_file.parent.exists()}")
            logger.error(f"Permissões: {oct(self.tasks_file.parent.stat().st_mode)[-3:]}")
            if 'tasks_data' in locals():
                logger.error(f"Conteúdo que tentou salvar: {tasks_data}")

    def _ensure_directories(self):
        """Garante que os diretórios necessários existem"""
        os.makedirs(self.config.audios_dir, exist_ok=True)
        os.makedirs(self.config.transcriptions_dir, exist_ok=True)

    def _get_transcriber(self, force_cpu: Optional[bool], version_model: Optional[str]) -> AudioTranscriber:
        """Obtém ou cria uma instância do transcritor"""
        if self.transcriber is None:
            self.transcriber = AudioTranscriber(
                version_model=version_model or self.config.version_model,
                hf_token=self.config.hf_token,
                force_cpu=force_cpu if force_cpu is not None else self.config.force_cpu
            )
        return self.transcriber

    async def process_transcription(
        self, 
        task_id: str, 
        audio_path: str,
        output_format: OutputFormat,
        force_cpu: Optional[bool],
        version_model: Optional[str],
        include_timestamps: bool = True,
        include_speaker_diarization: bool = True,
        base_task_id: Optional[str] = None,
        transcription_suffix: Optional[str] = None
    ):
        try:
            task = self._tasks[task_id]
            self._tasks[task_id] = task.update_task(
                status=TranscriptionStatus.PROCESSING
            )
            self._save_tasks()  # Salva após atualizar status

            transcriber = self._get_transcriber(force_cpu, version_model)
            # Usa base_task_id se fornecido, senão usa task_id
            folder_id = base_task_id if base_task_id else task_id
            output_file = transcriber.transcribe(
                audio_path=audio_path,
                output_dir=self.config.transcriptions_dir,
                output_format=output_format,
                include_timestamps=include_timestamps,
                include_speaker_diarization=include_speaker_diarization,
                task_id=folder_id,
                transcription_suffix=transcription_suffix
            )
            
            self._tasks[task_id] = task.update_task(
                status=TranscriptionStatus.COMPLETED,
                completed_at=datetime.now(),
                output_file=output_file
            )
            self._save_tasks()  # Salva após completar
            
        except Exception as e:
            logger.error(f"Erro na transcrição: {str(e)}")
            self._tasks[task_id] = task.update_task(
                status=TranscriptionStatus.FAILED,
                completed_at=datetime.now(),
                error=str(e)
            )
            self._save_tasks()  # Salva após erro

    def get_task_status(self, task_id: str) -> Optional[TranscriptionTask]:
        """Retorna o status de uma tarefa"""
        return self._tasks.get(task_id)

    def list_tasks(self) -> List[TranscriptionTask]:
        """Lista todas as tarefas"""
        return list(self._tasks.values())

    def create_task(self, task_id: str, filename: str) -> TranscriptionTask:
        """Cria uma nova tarefa de transcrição"""
        task = TranscriptionTask(
            task_id=task_id,
            filename=filename,
            status=TranscriptionStatus.PENDING,
            created_at=datetime.now()
        )
        self._tasks[task_id] = task
        self._save_tasks()  # Salva após criar
        return task

    def cancel_task(self, task_id: str) -> Optional[TranscriptionTask]:
        """
        Cancela uma tarefa de transcrição em andamento
        Só pode cancelar tarefas que estão PENDING ou PROCESSING
        """
        task = self._tasks.get(task_id)
        if not task:
            logger.warning(f"Tentativa de cancelar tarefa inexistente: {task_id}")
            return None
        
        if task.status in [TranscriptionStatus.COMPLETED, TranscriptionStatus.FAILED]:
            logger.warning(f"Não é possível cancelar tarefa {task_id} com status {task.status}")
            return None
        
        # Atualiza o status da tarefa
        updated_task = task.update_task(
            status=TranscriptionStatus.FAILED,
            completed_at=datetime.now(),
            error="Tarefa cancelada pelo usuário"
        )
        
        self._tasks[task_id] = updated_task
        self._save_tasks()
        
        logger.info(f"Tarefa {task_id} cancelada com sucesso")
        return updated_task

    def delete_task(self, task_id: str, delete_files: bool = True) -> bool:
        """
        Exclui uma tarefa e, opcionalmente, seus arquivos associados
        
        Args:
            task_id: ID da tarefa a ser excluída
            delete_files: Se True, remove também os arquivos de áudio e transcrição
        
        Returns:
            bool: True se a tarefa foi excluída com sucesso
        """
        task = self._tasks.get(task_id)
        if not task:
            logger.warning(f"Tentativa de excluir tarefa inexistente: {task_id}")
            return False
        
        try:
            if delete_files:
                # Remove arquivos de áudio (pasta do task_id)
                audio_dir = Path(self.config.audios_dir) / task_id
                if audio_dir.exists():
                    shutil.rmtree(audio_dir)
                    logger.info(f"Diretório de áudio removido: {audio_dir}")
                
                # Remove arquivos de transcrição (pasta do task_id)
                transcription_dir = Path(self.config.transcriptions_dir) / task_id
                if transcription_dir.exists():
                    shutil.rmtree(transcription_dir)
                    logger.info(f"Diretório de transcrição removido: {transcription_dir}")
                
                # Se há um arquivo de output específico, remove também
                if task.output_file and os.path.exists(task.output_file):
                    os.remove(task.output_file)
                    logger.info(f"Arquivo de output removido: {task.output_file}")
            
            # Remove a tarefa da memória e do arquivo
            del self._tasks[task_id]
            self._save_tasks()
            
            logger.info(f"Tarefa {task_id} excluída com sucesso (delete_files={delete_files})")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao excluir tarefa {task_id}: {str(e)}")
            return False

    def get_task_files_info(self, task_id: str) -> Dict[str, Any]:
        """
        Retorna informações sobre os arquivos associados a uma tarefa
        """
        task = self._tasks.get(task_id)
        if not task:
            return {}
        
        info = {
            "task_id": task_id,
            "audio_files": [],
            "transcription_files": [],
            "total_size": 0
        }
        
        # Verifica arquivos de áudio
        audio_dir = Path(self.config.audios_dir) / task_id
        if audio_dir.exists():
            for file_path in audio_dir.iterdir():
                if file_path.is_file():
                    size = file_path.stat().st_size
                    info["audio_files"].append({
                        "name": file_path.name,
                        "size": size,
                        "path": str(file_path)
                    })
                    info["total_size"] += size
        
        # Verifica arquivos de transcrição
        transcription_dir = Path(self.config.transcriptions_dir) / task_id
        if transcription_dir.exists():
            for file_path in transcription_dir.iterdir():
                if file_path.is_file():
                    size = file_path.stat().st_size
                    info["transcription_files"].append({
                        "name": file_path.name,
                        "size": size,
                        "path": str(file_path)
                    })
                    info["total_size"] += size
        
        return info