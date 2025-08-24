from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class OutputFormat(str, Enum):
    TXT = "txt"
    JSON = "json"
    SRT = "srt"

class TranscriptionStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class TranscriptionRequest(BaseModel):
    output_format: str = Field(default="txt", description="Formato de saída desejado")
    force_cpu: bool = Field(default=True, description="Força o uso de CPU")
    version_model: str = Field(default="turbo", description="Nome do modelo a ser usado")
    include_timestamps: bool = Field(default=True, description="Incluir marcações de tempo na transcrição")
    include_speaker_diarization: bool = Field(default=True, description="Incluir distinção de falantes na transcrição")

class TranscriptionTask(BaseModel):
    task_id: str
    filename: str
    status: TranscriptionStatus
    created_at: datetime
    completed_at: Optional[datetime] = None
    output_file: Optional[str] = None
    error: Optional[str] = None

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

    def update_task(
        self,
        status: Optional[TranscriptionStatus] = None,
        completed_at: Optional[datetime] = None,
        output_file: Optional[str] = None,
        error: Optional[str] = None
    ) -> 'TranscriptionTask':
        """Retorna uma nova instância atualizada da tarefa"""
        return TranscriptionTask(
            task_id=self.task_id,
            filename=self.filename,
            status=status or self.status,
            created_at=self.created_at,
            completed_at=completed_at or self.completed_at,
            output_file=output_file or self.output_file,
            error=error or self.error
        )

class TranscriptionListResponse(BaseModel):
    tasks: list[TranscriptionTask]
    total: int

class BatchUploadTask(BaseModel):
    """Representa uma tarefa individual em um upload em lote"""
    filename: str
    file_size: int
    task: Optional[TranscriptionTask] = None
    error: Optional[str] = None
    status: str = "pending"  # pending, processing, completed, failed

class BatchUploadResponse(BaseModel):
    """Resposta para upload em lote"""
    batch_id: str
    total_files: int
    tasks: list[BatchUploadTask]
    message: str