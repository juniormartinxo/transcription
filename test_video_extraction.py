#!/usr/bin/env python3
"""
Script de teste para o endpoint de extração de áudio
"""
import requests
import tempfile
import subprocess
import os

def create_test_video():
    """Cria um vídeo de teste simples usando FFmpeg"""
    with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as temp_video:
        # Cria um vídeo de teste de 3 segundos com áudio sintético
        cmd = [
            'ffmpeg', '-y',
            '-f', 'lavfi', '-i', 'testsrc2=duration=3:size=320x240:rate=30',
            '-f', 'lavfi', '-i', 'sine=frequency=1000:duration=3',
            '-c:v', 'libx264', '-c:a', 'aac',
            '-shortest', temp_video.name
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Vídeo de teste criado: {temp_video.name}")
            return temp_video.name
        else:
            print(f"❌ Erro ao criar vídeo de teste: {result.stderr}")
            return None

def test_extract_audio_endpoint():
    """Testa o endpoint de extração de áudio"""
    video_path = create_test_video()
    if not video_path:
        return
    
    try:
        # Testa o endpoint
        with open(video_path, 'rb') as video_file:
            files = {'file': ('test_video.mp4', video_file, 'video/mp4')}
            response = requests.post('http://localhost:8000/transcribe/extract-audio', files=files)
        
        if response.status_code == 200:
            print("✅ Endpoint funcionando corretamente!")
            print(f"📋 Content-Type: {response.headers.get('content-type')}")
            print(f"📏 Tamanho do áudio: {len(response.content)} bytes")
            
            # Salva o áudio extraído
            with open('audio_extraido_teste.wav', 'wb') as audio_file:
                audio_file.write(response.content)
            print("💾 Áudio salvo como 'audio_extraido_teste.wav'")
            
        else:
            print(f"❌ Erro no endpoint: {response.status_code}")
            print(f"📄 Resposta: {response.text}")
            
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")
    
    finally:
        # Limpa o arquivo de teste
        if os.path.exists(video_path):
            os.remove(video_path)
            print(f"🗑️ Arquivo de teste removido: {video_path}")

if __name__ == "__main__":
    print("🧪 Testando endpoint de extração de áudio...")
    test_extract_audio_endpoint()