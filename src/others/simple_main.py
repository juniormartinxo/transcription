import whisper
from pathlib import Path

# Carregar o modelo Whisper
# models disponíveis: "tiny", "base", "small", "medium", "large" e "turbo"
model = whisper.load_model("turbo") # turbo é o modelo mais rápido

# Definir o caminho do áudio
audio_path = "audios/audio.wav"

# Criar nome do arquivo de saída baseado no nome do arquivo de entrada
output_filename = Path(audio_path).stem + "_transcricao.txt"

print("Iniciando transcrição...")

# Realizar a transcrição
result = model.transcribe(audio_path)

# Salvar a transcrição em um arquivo
with open(output_filename, "w", encoding="utf-8") as f:
    f.write(result["text"].strip())

print(f"Transcrição salva no arquivo: {output_filename}")