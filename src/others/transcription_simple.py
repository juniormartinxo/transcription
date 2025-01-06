# transcription_simple.py

import whisperx
import torch
from pathlib import Path
import logging
from typing import Optional, Literal
from datetime import datetime
import os
import traceback
import numpy as np
from pyannote.audio import Pipeline  # Adicionando o import correto

class AudioTranscriber:
    def _setup_logging(self) -> logging.Logger:
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger

    def __init__(
        self, 
        version_model: str = "base", 
        force_cpu: bool = False
    ):
        self.has_cuda = torch.cuda.is_available() and not force_cpu
        self.device = "cuda" if self.has_cuda else "cpu"
        self.logger = self._setup_logging()
        
        self.compute_type = "float16" if self.has_cuda else "int8"
        self.batch_size = 16 if self.has_cuda else 4
        
        self.logger.info(f"Usando dispositivo: {self.device}")
        self.logger.info(f"Tipo de computação: {self.compute_type}")
        
        try:
            self._load_model(version_model)
        except Exception as e:
            self.logger.error(f"Erro ao carregar modelo: {str(e)}")
            self.logger.error(traceback.format_exc())
            raise

    def _load_model(self, version_model: str):
        self.logger.info(f"Carregando modelo {version_model}...")
        self.model = whisperx.load_model(
            version_model,
            self.device,
            compute_type=self.compute_type
        )
        self.logger.info("Modelo carregado com sucesso")

    def transcribe(
        self,
        audio_path: str,
        output_dir: Optional[str] = None,
        output_format: Literal["txt", "json", "srt"] = "txt",
        batch_size: Optional[int] = None
    ) -> str:
        try:
            if not os.path.exists(audio_path):
                raise FileNotFoundError(f"Arquivo de áudio não encontrado: {audio_path}")
                
            batch_size = batch_size or self.batch_size
            
            self.logger.info(f"Iniciando transcrição: {audio_path}")
            result = self.model.transcribe(
                audio_path,
                batch_size=batch_size
            )
            self.logger.info("Transcrição inicial concluída")

            try:
                model_a, metadata = whisperx.load_align_model(
                    language_code=result["language"],
                    device=self.device
                )
                result = whisperx.align(
                    result["segments"],
                    model_a,
                    metadata,
                    audio_path,
                    self.device
                )
                self.logger.info("Alinhamento concluído com sucesso")
            except Exception as e:
                self.logger.error(f"Erro durante alinhamento: {str(e)}")
                self.logger.error(traceback.format_exc())
                self.logger.warning("Continuando sem alinhamento...")

            output_path = self._prepare_output_path(audio_path, output_dir, output_format)
            self._save_transcription(result, output_path, output_format)
            
            self.logger.info(f"Transcrição finalizada: {output_path}")
            return output_path

        except Exception as e:
            self.logger.error(f"Erro durante a transcrição: {str(e)}")
            self.logger.error(traceback.format_exc())
            raise

    def _prepare_output_path(
        self, 
        audio_path: str, 
        output_dir: Optional[str],
        output_format: str
    ) -> str:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        audio_filename = Path(audio_path).stem
        
        if output_dir:
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
        else:
            output_path = Path(audio_path).parent
            
        return str(output_path / f"{audio_filename}_transcricao_{timestamp}.{output_format}")

    def _save_transcription(
        self, 
        result: dict, 
        output_path: str,
        output_format: str
    ):
        try:
            if output_format == "txt":
                self._save_as_txt(result, output_path)
            elif output_format == "json":
                self._save_as_json(result, output_path)
            elif output_format == "srt":
                self._save_as_srt(result, output_path)
        except Exception as e:
            self.logger.error(f"Erro ao salvar no formato {output_format}: {str(e)}")
            self.logger.error(traceback.format_exc())
            fallback_path = str(Path(output_path).with_suffix('.txt'))
            self.logger.info(f"Tentando salvar em formato texto simples: {fallback_path}")
            with open(fallback_path, "w", encoding="utf-8") as f:
                f.write(str(result))
            raise

    def _save_as_txt(self, result: dict, output_path: str):
        with open(output_path, "w", encoding="utf-8") as f:
            for segment in result.get("segments", []):
                text = segment.get("text", "").strip()
                start = segment.get("start", 0)
                end = segment.get("end", 0)
                
                timestamp = f"[{self._format_time(start)} -> {self._format_time(end)}]"
                f.write(f"{timestamp} {text}\n")

    def _save_as_json(self, result: dict, output_path: str):
        import json
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)

    def _save_as_srt(self, result: dict, output_path: str):
        with open(output_path, "w", encoding="utf-8") as f:
            for i, segment in enumerate(result.get("segments", []), 1):
                start = self._format_time_srt(segment.get("start", 0))
                end = self._format_time_srt(segment.get("end", 0))
                text = segment.get("text", "").strip()
                
                f.write(f"{i}\n")
                f.write(f"{start} --> {end}\n")
                f.write(f"{text}\n\n")

    @staticmethod
    def _format_time(seconds: float) -> str:
        minutes = int(seconds // 60)
        seconds = int(seconds % 60)
        return f"{minutes:02d}:{seconds:02d}"

    @staticmethod
    def _format_time_srt(seconds: float) -> str:
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        seconds = int(seconds % 60)
        milliseconds = int((seconds % 1) * 1000)
        return f"{hours:02d}:{minutes:02d}:{seconds:02d},{milliseconds:03d}"