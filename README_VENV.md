# 🐍 API de Transcrição - Ambiente Virtual

Este guia mostra como usar a API de transcrição com ambiente virtual Python.

## 🚀 Execução Rápida

### Opção 1: Script Automático (Recomendado)
```bash
python3 run_venv.py
```

### Opção 2: Setup Manual
```bash
# 1. Criar e configurar ambiente virtual
./setup_venv.sh

# 2. Ativar ambiente virtual
source venv/bin/activate

# 3. Executar aplicação
python main.py
```

## 📋 Pré-requisitos

### 1. Python 3.8+
```bash
python3 --version
```

### 2. FFmpeg
```bash
# Ubuntu/Debian
sudo apt install ffmpeg

# macOS
brew install ffmpeg
```

### 3. Token do HuggingFace
1. Acesse: https://huggingface.co/settings/tokens
2. Crie um token
3. Aceite os termos dos modelos PyAnnote

## 🐍 Gerenciamento do Ambiente Virtual

### Criar Ambiente Virtual
```bash
python3 -m venv venv
```

### Ativar Ambiente Virtual
```bash
# Linux/macOS
source venv/bin/activate

# Windows
venv\Scripts\activate

# Ou use o script
./activate_venv.sh
```

### Desativar Ambiente Virtual
```bash
deactivate
```

### Instalar Dependências
```bash
# Com ambiente ativado
pip install -r requirements.txt

# Ou use o script automático
python3 run_venv.py
```

## 📁 Estrutura com Ambiente Virtual

```
transcription/
├── venv/                  # Ambiente virtual
├── public/
│   ├── audios/           # Áudios enviados
│   └── transcriptions/   # Transcrições geradas
├── logs/                 # Logs da aplicação
├── .env                  # Configurações
├── run_venv.py          # Script automático
├── setup_venv.sh        # Setup com venv
├── activate_venv.sh     # Ativar venv
└── README_VENV.md       # Este arquivo
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

## 🔧 Scripts Disponíveis

### `run_venv.py`
- ✅ Cria ambiente virtual automaticamente
- ✅ Instala dependências
- ✅ Configura diretórios
- ✅ Executa aplicação
- ✅ Gerencia tudo automaticamente

### `setup_venv.sh`
- ✅ Cria ambiente virtual
- ✅ Instala dependências
- ✅ Configura diretórios
- ⚠️ Requer ativação manual

### `activate_venv.sh`
- ✅ Ativa ambiente virtual
- ✅ Mostra informações do Python/pip
- ✅ Lista comandos disponíveis

## 🌐 Endpoints

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

## 🔄 Fluxo de Trabalho

### Primeira Execução
```bash
# 1. Execute o script automático
python3 run_venv.py

# 2. Configure o token no arquivo .env
# 3. A API estará disponível em http://localhost:8000
```

### Execuções Subsequentes
```bash
# Opção 1: Script automático
python3 run_venv.py

# Opção 2: Manual
source venv/bin/activate
python main.py
```

## 🎯 Vantagens do Ambiente Virtual

| Aspecto | Com Venv | Sem Venv |
|---------|----------|----------|
| **Isolamento** | ✅ Completo | ❌ Sistema |
| **Dependências** | ✅ Controladas | ⚠️ Globais |
| **Conflitos** | ✅ Evitados | ❌ Possíveis |
| **Portabilidade** | ✅ Alta | ⚠️ Baixa |
| **Debug** | ✅ Fácil | ⚠️ Complexo |

## 🚨 Troubleshooting

### Erro: "venv não encontrado"
```bash
# Recrie o ambiente virtual
rm -rf venv
python3 run_venv.py
```

### Erro: "Módulo não encontrado"
```bash
# Reinstale as dependências
source venv/bin/activate
pip install -r requirements.txt --force-reinstall
```

### Erro: "Permissão negada"
```bash
# Torne os scripts executáveis
chmod +x setup_venv.sh activate_venv.sh
```

### Erro: "Token não encontrado"
```bash
# Configure o token no arquivo .env
echo "HUGGING_FACE_HUB_TOKEN=seu_token_aqui" >> .env
```

## 📊 Monitoramento

### Verificar Ambiente Virtual
```bash
# Ver se está ativo
which python

# Ver dependências instaladas
pip list
```

### Logs da Aplicação
```bash
# Ver logs em tempo real
tail -f logs/app.log
```

## 🎯 Exemplo Completo

```bash
# 1. Clone o repositório
git clone <url-do-repositorio>
cd transcription

# 2. Execute o script automático
python3 run_venv.py

# 3. Configure o token no arquivo .env
# 4. A API estará disponível em http://localhost:8000

# 5. Teste com um arquivo de áudio
curl -X POST "http://localhost:8000/transcribe/" \
  -F "file=@exemplo.wav"
```

## 💡 Dicas

1. **Sempre use o ambiente virtual** para evitar conflitos
2. **Configure o token** antes de executar
3. **Use o script automático** para facilitar o setup
4. **Monitore os logs** para debug
5. **Teste com arquivos pequenos** primeiro

## 📞 Suporte

Se encontrar problemas:
1. Verifique se o FFmpeg está instalado
2. Confirme se o token do HuggingFace está correto
3. Verifique os logs em `logs/app.log`
4. Teste com arquivos de áudio pequenos primeiro 