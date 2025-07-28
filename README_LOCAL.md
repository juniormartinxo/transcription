# 🎵 API de Transcrição - Execução Local

Este guia te ajudará a rodar a API de transcrição localmente sem Docker.

## 📋 Pré-requisitos

### 1. Python 3.8+
```bash
python --version
# ou
python3 --version
```

### 2. FFmpeg
```bash
# Ubuntu/Debian
sudo apt update && sudo apt install ffmpeg

# macOS
brew install ffmpeg

# Windows
# Baixe de: https://ffmpeg.org/download.html
```

### 3. Token do HuggingFace
1. Acesse: https://huggingface.co/settings/tokens
2. Crie um novo token
3. Aceite os termos dos modelos:
   - https://huggingface.co/pyannote/speaker-diarization
   - https://huggingface.co/pyannote/segmentation

## 🚀 Execução Rápida

### Opção 1: Script Automático
```bash
python run_local.py
```

### Opção 2: Manual
```bash
# 1. Instalar dependências
pip install -r requirements.txt

# 2. Criar diretórios
mkdir -p public/audios public/transcriptions logs

# 3. Configurar .env
cp .env.example .env
# Edite o arquivo .env com seu token

# 4. Executar
python main.py
```

## ⚙️ Configuração

### Arquivo .env
```env
# Token obrigatório do HuggingFace
HUGGING_FACE_HUB_TOKEN=seu_token_aqui

# Configurações opcionais
VERSION_MODEL=turbo
FORCE_CPU=true
AUDIOS_DIR=./public/audios
TRANSCRIPTIONS_DIR=./public/transcriptions
LOG_LEVEL=INFO
```

## 🌐 Endpoints Disponíveis

### Teste de Saúde
```bash
curl http://localhost:8000/health
```

### Documentação
```bash
# Abra no navegador
http://localhost:8000/docs
```

### Upload de Áudio
```bash
curl -X POST "http://localhost:8000/transcribe/" \
  -F "file=@/caminho/para/seu/audio.wav"
```

### Status da Transcrição
```bash
curl http://localhost:8000/transcribe/{task_id}
```

## 📁 Estrutura de Diretórios

```
transcription/
├── public/
│   ├── audios/          # Áudios enviados
│   └── transcriptions/  # Transcrições geradas
├── logs/                # Logs da aplicação
├── src/                 # Código fonte
├── main.py             # Ponto de entrada
├── run_local.py        # Script de execução
└── requirements.txt    # Dependências
```

## 🔧 Troubleshooting

### Erro: "Token do HuggingFace não encontrado"
```bash
# Verifique se o arquivo .env existe e tem o token
cat .env
```

### Erro: "FFmpeg não encontrado"
```bash
# Instale o FFmpeg
sudo apt install ffmpeg  # Ubuntu/Debian
brew install ffmpeg      # macOS
```

### Erro: "Módulo não encontrado"
```bash
# Reinstale as dependências
pip install -r requirements.txt --force-reinstall
```

### Erro: "CUDA não disponível"
```bash
# Configure FORCE_CPU=true no .env
# Isso força o uso de CPU em vez de GPU
```

## 📊 Monitoramento

### Logs
```bash
# Ver logs em tempo real
tail -f logs/app.log
```

### Status da API
```bash
# Verificar se está funcionando
curl http://localhost:8000/health
```

## 🎯 Exemplo Completo

```bash
# 1. Clone o repositório
git clone <url-do-repositorio>
cd transcription

# 2. Execute o script automático
python run_local.py

# 3. Configure o token no arquivo .env
# 4. A API estará disponível em http://localhost:8000

# 5. Teste com um arquivo de áudio
curl -X POST "http://localhost:8000/transcribe/" \
  -F "file=@exemplo.wav"
```

## 🔄 Diferenças do Docker

| Aspecto | Docker | Local |
|---------|--------|-------|
| **Isolamento** | ✅ Completo | ❌ Sistema local |
| **Setup** | ✅ Automático | ⚠️ Manual |
| **Performance** | ⚠️ Overhead | ✅ Direto |
| **Debug** | ❌ Complexo | ✅ Fácil |
| **Dependências** | ✅ Garantidas | ⚠️ Sistema |

## 🚨 Notas Importantes

1. **Primeira execução**: Pode demorar para baixar os modelos
2. **Memória**: WhisperX precisa de pelo menos 2GB RAM
3. **CPU**: Recomendado usar CPU com pelo menos 4 cores
4. **Internet**: Necessária apenas na primeira execução para baixar modelos

## 📞 Suporte

Se encontrar problemas:
1. Verifique os logs em `logs/app.log`
2. Confirme se o FFmpeg está instalado
3. Verifique se o token do HuggingFace está correto
4. Teste com arquivos de áudio pequenos primeiro 