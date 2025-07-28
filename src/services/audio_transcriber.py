# transcription.py
import logging
import os
import subprocess
import traceback
import warnings
from datetime import datetime
from pathlib import Path
from typing import Literal, Optional

import numpy as np
import pandas as pd  # Adicionar este import no topo do arquivo
import torch
import whisperx
from pyannote.audio import Pipeline  # Adicionando o import correto

from src.core.colored_formatter import ColoredFormatter
from src.core.logger_config import get_logger

# Suprimir warnings de compatibilidade conhecidos
warnings.filterwarnings("ignore", message=".*torch.cuda.amp.custom_fwd.*")
warnings.filterwarnings("ignore", message=".*TensorFloat-32.*")
warnings.filterwarnings("ignore", message=".*torchaudio._backend.list_audio_backends.*")
warnings.filterwarnings("ignore", message=".*Model was trained with.*")

logger = get_logger(__name__)

class AudioTranscriber:
    def __init__(
        self, 
        version_model: str = "base", 
        hf_token: str = None,
        force_cpu: bool = True  # Forçar CPU por padrão
    ):
        self.logger = get_logger(__name__)  # Usa o logger global
        
        # Forçar CPU se especificado ou se houver problemas de CUDA
        self.has_cuda = torch.cuda.is_available() and not force_cpu
        self.device = "cuda" if self.has_cuda else "cpu"
        self.torch_device = torch.device(self.device)
        
        # Configurar TF32 para melhor compatibilidade
        if self.has_cuda:
            torch.backends.cuda.matmul.allow_tf32 = True
            torch.backends.cudnn.allow_tf32 = True
        
        # Log adicional para debug
        self.logger.info(f"CUDA disponível: {torch.cuda.is_available()}")
        self.logger.info(f"Force CPU: {force_cpu}")
        self.logger.info(f"Dispositivo final: {self.device}")
        
        # Configurações baseadas no dispositivo
        self.compute_type = "float16" if self.has_cuda else "int8"
        self.batch_size = 16 if self.has_cuda else 4
        
        # Verificar token do HuggingFace
        self.hf_token = hf_token or os.getenv("HUGGING_FACE_HUB_TOKEN")
        if not self.hf_token:
            raise ValueError("HuggingFace token não encontrado. Configure HF_TOKEN ou a variável de ambiente HUGGING_FACE_HUB_TOKEN")
        
        self.logger.info(f"Usando dispositivo: {self.device}")
        self.logger.info(f"Tipo de computação: {self.compute_type}")
        
        try:
            self._load_models(version_model)
        except Exception as e:
            self.logger.error(f"Erro ao carregar modelos: {e}")
            raise

    def _load_models(self, version_model: str):
        """Carrega os modelos necessários."""
        self.logger.info(f"Carregando modelo {version_model}...")
        
        # Primeiro carrega o modelo Whisper
        try:
            self.model = whisperx.load_model(
                version_model,
                self.device,
                compute_type=self.compute_type
            )
            self.logger.info("Modelo Whisper carregado com sucesso")
        except Exception as e:
            self.logger.error(f"Erro ao carregar modelo Whisper: {e}")
            raise
        
        # Tenta carregar o modelo de diarização
        try:
            self.logger.info("Carregando modelo de diarização...")
            self.diarize_model = Pipeline.from_pretrained(
                "pyannote/speaker-diarization@2.1",
                use_auth_token=self.hf_token
            )
            if self.device == "cuda":
                self.diarize_model = self.diarize_model.to(self.torch_device)
            self.logger.info("Modelo de diarização carregado com sucesso")
            self.has_diarization = True
        except Exception as e:
            self.logger.error(f"Erro ao carregar modelo de diarização: {e}")
            self.logger.error("Verifique se você:\n    1. Aceitou os termos em https://huggingface.co/pyannote/speaker-diarization\n    2. Aceitou os termos em https://huggingface.co/pyannote/segmentation\n    3. Está usando um token válido do HuggingFace")
            self.has_diarization = False
            # Não raise aqui, permite continuar sem diarização

    def _convert_to_wav(self, input_path: str) -> str:
        """Converte arquivo de áudio para WAV se necessário."""
        input_path = Path(input_path)
        output_path = input_path.parent / f"{input_path.stem}.wav"
        
        try:
            # Converte para WAV usando ffmpeg
            command = [
                'ffmpeg', '-i', str(input_path),
                '-acodec', 'pcm_s16le',  # Formato WAV padrão
                '-ac', '1',              # Mono
                '-ar', '16000',          # Sample rate 16kHz
                str(output_path),
                '-y'                     # Sobrescreve se existir
            ]
            
            result = subprocess.run(
                command,
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                raise RuntimeError(f"Erro na conversão: {result.stderr}")
                
            return str(output_path)
            
        except Exception as e:
            logger.error(f"Erro ao converter áudio: {e}")
            raise

    def _convert_diarize_segments(self, diarize_segments):
        """
        Converte os segmentos de diarização para o formato esperado pelo WhisperX.
        """
        try:
            # Converter para um formato intermediário mais simples
            segments = []
            for segment, track, speaker in diarize_segments.itertracks(yield_label=True):
                segments.append({
                    'start': segment.start,
                    'end': segment.end,
                    'speaker': f"SPEAKER_{speaker}"
                })
            
            # Ordenar por tempo de início
            segments.sort(key=lambda x: x['start'])
            
            return {
                'segments': segments,
                'speakers': list(set(s['speaker'] for s in segments))
            }
        except Exception as e:
            self.logger.error(f"Erro na conversão dos segmentos: {str(e)}")
            self.logger.error(traceback.format_exc())
            return None

    def _process_diarization(self, diarization, result):
        """
        Processa a saída da diarização e a combina com o resultado do Whisper.
        """
        try:
            # Converter a diarização para um formato DataFrame
            segments = []
            for turn, _, speaker in diarization.itertracks(yield_label=True):
                segments.append({
                    "start": turn.start,
                    "end": turn.end,
                    "speaker": speaker
                })
            
            diarize_df = pd.DataFrame(segments)
            
            # Adicionar informações do speaker aos segmentos do Whisper
            for segment in result["segments"]:
                segment_start = segment["start"]
                segment_end = segment["end"]
                
                # Encontrar o speaker que mais se sobrepõe com este segmento
                overlaps = []
                for _, row in diarize_df.iterrows():
                    overlap_start = max(segment_start, row["start"])
                    overlap_end = min(segment_end, row["end"])
                    overlap_duration = max(0, overlap_end - overlap_start)
                    overlaps.append((overlap_duration, row["speaker"]))
                
                if overlaps:
                    # Atribuir o speaker com maior sobreposição
                    best_speaker = max(overlaps, key=lambda x: x[0])[1]
                    segment["speaker"] = f"SPEAKER_{best_speaker}"
                else:
                    segment["speaker"] = "SPEAKER_UNKNOWN"
            
            return result
            
        except Exception as e:
            self.logger.error(f"Erro ao processar diarização: {str(e)}")
            self.logger.error(traceback.format_exc())
            return result

    def transcribe(
        self,
        audio_path: str,
        output_dir: Optional[str] = None,
        output_format: Literal["txt", "json", "srt"] = "txt",
        batch_size: Optional[int] = None,
        include_timestamps: bool = True,
        include_speaker_diarization: bool = True
    ) -> str:
        try:
            if not os.path.exists(audio_path):
                raise FileNotFoundError(f"Arquivo de áudio não encontrado: {audio_path}")
            
            # Converte para WAV se não for WAV
            if not audio_path.lower().endswith('.wav'):
                logger.info(f"Convertendo {audio_path} para WAV...")
                audio_path = self._convert_to_wav(audio_path)
                logger.info(f"Arquivo convertido: {audio_path}")
                
            batch_size = batch_size or self.batch_size
            
            # Transcrição inicial
            self.logger.info(f"Iniciando transcrição: {audio_path}")
            result = self.model.transcribe(
                audio_path,
                batch_size=batch_size
            )
            self.logger.info("Transcrição inicial concluída")

            # Alinhamento
            self.logger.info("Realizando alinhamento de texto")
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

            # Diarização (apenas se solicitada)
            if include_speaker_diarization and hasattr(self, 'has_diarization') and self.has_diarization:
                self.logger.info("Iniciando processo de diarização...")
                try:
                    diarization = self.diarize_model(audio_path)
                    
                    if diarization is not None:
                        self.logger.info("Processando resultado da diarização...")
                        result = self._process_diarization(diarization, result)
                        self.logger.info("Diarização processada com sucesso")
                    else:
                        self.logger.warning("Diarização não produziu resultados")
                except Exception as e:
                    self.logger.error(f"Erro durante diarização: {str(e)}")
                    self.logger.error(traceback.format_exc())
                    self.logger.warning("Continuando sem diarização...")
            else:
                if not include_speaker_diarization:
                    self.logger.info("Diarização desabilitada pelo usuário")
                else:
                    self.logger.info("Diarização não disponível - continuando sem diarização")
            
            # Salvar resultado
            output_path = self._prepare_output_path(audio_path, output_dir, output_format)
            self._save_transcription(result, output_path, output_format, include_timestamps, include_speaker_diarization)
            
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
        output_format: str,
        include_timestamps: bool = True,
        include_speaker_diarization: bool = True
    ):
        """Salva a transcrição no formato especificado."""
        try:
            if output_format == "txt":
                self._save_as_txt(result, output_path, include_timestamps, include_speaker_diarization)
            elif output_format == "json":
                self._save_as_json(result, output_path)
            elif output_format == "srt":
                self._save_as_srt(result, output_path, include_timestamps, include_speaker_diarization)
        except Exception as e:
            self.logger.error(f"Erro ao salvar no formato {output_format}: {str(e)}")
            self.logger.error(traceback.format_exc())
            # Tentar salvar em formato texto simples como fallback
            fallback_path = str(Path(output_path).with_suffix('.txt'))
            self.logger.info(f"Tentando salvar em formato texto simples: {fallback_path}")
            with open(fallback_path, "w", encoding="utf-8") as f:
                f.write(str(result))
            raise

    def _save_as_txt(self, result: dict, output_path: str, include_timestamps: bool = True, include_speaker_diarization: bool = True):
        """Salva a transcrição em formato TXT com opções de timestamps e falantes."""
        current_speaker = None
        with open(output_path, "w", encoding="utf-8") as f:
            for segment in result.get("segments", []):
                text = segment.get("text", "").strip()
                start = segment.get("start", 0)
                end = segment.get("end", 0)
                speaker = segment.get("speaker", "").replace("SPEAKER_", "Falante ") if include_speaker_diarization else ""
                
                # Construir linha com base nas opções selecionadas
                parts = []
                
                if include_timestamps:
                    timestamp = f"[{self._format_time(start)} -> {self._format_time(end)}]"
                    parts.append(timestamp)
                
                if include_speaker_diarization and speaker:
                    # Se mudou o falante, adiciona uma linha em branco para melhor legibilidade
                    if speaker != current_speaker:
                        if current_speaker is not None:
                            f.write("\n")
                        current_speaker = speaker
                    parts.append(f"{speaker}:")
                
                parts.append(text)
                line = " ".join(parts)
                f.write(f"{line}\n")

    def _save_as_json(self, result: dict, output_path: str):
        import json
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)

    def _save_as_srt(self, result: dict, output_path: str, include_timestamps: bool = True, include_speaker_diarization: bool = True):
        with open(output_path, "w", encoding="utf-8") as f:
            for i, segment in enumerate(result["segments"], 1):
                start = self._format_time_srt(segment["start"]) if include_timestamps else "00:00:00,000"
                end = self._format_time_srt(segment["end"]) if include_timestamps else "00:00:00,000"
                speaker = segment.get("speaker", "Desconhecido") if include_speaker_diarization else ""
                text = segment["text"].strip()
                
                f.write(f"{i}\n")
                if include_timestamps:
                    f.write(f"{start} --> {end}\n")
                
                if include_speaker_diarization and speaker:
                    f.write(f"{speaker}: {text}\n\n")
                else:
                    f.write(f"{text}\n\n")

    @staticmethod
    def _format_time(seconds: float) -> str:
        """Formata o tempo em formato mais detalhado HH:MM:SS."""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        seconds = int(seconds % 60)
        ms = int((seconds % 1) * 1000)
        
        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{seconds:02d}.{ms:03d}"
        else:
            return f"{minutes:02d}:{seconds:02d}.{ms:03d}"

    @staticmethod
    def _format_time_srt(seconds: float) -> str:
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        seconds = int(seconds % 60)
        milliseconds = int((seconds % 1) * 1000)
        return f"{hours:02d}:{minutes:02d}:{seconds:02d},{milliseconds:03d}"