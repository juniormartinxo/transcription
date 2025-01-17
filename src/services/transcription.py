import json
import os
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
        self.tasks_file = Path(self.config.transcriptions_dir) / "tasks.json"
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
        version_model: Optional[str]
    ):
        try:
            task = self._tasks[task_id]
            self._tasks[task_id] = task.update_task(
                status=TranscriptionStatus.PROCESSING
            )
            self._save_tasks()  # Salva após atualizar status

            transcriber = self._get_transcriber(force_cpu, version_model)
            output_file = transcriber.transcribe(
                audio_path=audio_path,
                output_dir=self.config.transcriptions_dir,
                output_format=output_format
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