from transcription_simple import AudioTranscriber
import os
import logging
import whisperx

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    os.makedirs("transcricoes", exist_ok=True)
    
    transcriber = AudioTranscriber(
        version_model="turbo",
        force_cpu=False
    )

    output_file = transcriber.transcribe(
        audio_path="audios/audio.wav",
        output_dir="transcricoes"
    )
    
    logger.info(f"Transcrição concluída com sucesso!")
    logger.info(f"Arquivo de saída: {output_file}")
    
except Exception as e:
    logger.error(f"Erro durante a execução: {str(e)}")
    logger.error("Stack trace completo:", exc_info=True)