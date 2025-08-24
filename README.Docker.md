# 🐳 Docker Setup - Aplicação de Transcrição

Este documento explica como executar a aplicação de transcrição usando Docker e Docker Compose.

## 📋 Pré-requisitos

- Docker (versão 20.10+)
- Docker Compose (versão 2.0+)
- Token do Hugging Face (para diarização de speaker)

## 🚀 Início Rápido

### 1. Configure o ambiente

```bash
# Clone o repositório (se ainda não fez)
git clone <repository-url>
cd transcription

# Configure o arquivo .env
cp .env.example .env
# Edite .env e adicione seu HUGGING_FACE_HUB_TOKEN
```

### 2. Execute a aplicação

```bash
# Método mais fácil: use o script de inicialização
./docker-start.sh

# Ou execute manualmente:
docker compose up --build -d
```

### 3. Acesse a aplicação

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **Documentação da API**: http://localhost:8000/docs

## 🏗️ Arquitetura

A aplicação consiste em dois serviços principais:

### Backend (FastAPI)
- **Porta**: 8000
- **Tecnologias**: Python, FastAPI, WhisperX, PyAnnote
- **Funcionalidades**: 
  - Transcrição de áudio/vídeo
  - Diarização de speaker
  - Upload em lote
  - API REST

### Frontend (Next.js)
- **Porta**: 3000  
- **Tecnologias**: React, Next.js, TypeScript, Tailwind CSS
- **Funcionalidades**:
  - Interface de upload
  - Dashboard de transcrições
  - Progresso em tempo real

## 🔧 Comandos Úteis

### Gerenciamento básico
```bash
# Iniciar serviços
docker compose up -d

# Parar serviços
docker compose down

# Reiniciar serviços
docker compose restart

# Ver status dos containers
docker compose ps
```

### Logs e debugging
```bash
# Ver logs de todos os serviços
docker compose logs -f

# Ver logs apenas do backend
docker compose logs -f backend

# Ver logs apenas do frontend  
docker compose logs -f frontend

# Acessar terminal do backend
docker compose exec backend bash

# Acessar terminal do frontend
docker compose exec frontend sh
```

### Build e limpeza
```bash
# Rebuild completo (forçar rebuild das imagens)
docker compose up --build --force-recreate

# Limpar volumes (CUIDADO: apaga dados!)
docker compose down -v

# Limpar imagens não utilizadas
docker system prune -a
```

## 🗂️ Volumes e Persistência

### Volumes de dados (persistem entre reinicializações)
- `./public/audios` → `/app/public/audios` - Arquivos de áudio
- `./public/transcriptions` → `/app/public/transcriptions` - Transcrições
- `./public/videos` → `/app/public/videos` - Arquivos de vídeo  
- `./logs` → `/app/logs` - Logs da aplicação

### Volumes de cache (otimização)
- `huggingface_cache` - Cache dos modelos Hugging Face
- `torch_cache` - Cache do PyTorch
- `matplotlib_config` - Configurações do matplotlib

## 🏭 Produção

Para execução em produção, use o arquivo específico:

```bash
# Produção (sem volumes de desenvolvimento)
docker compose -f docker-compose.prod.yml up -d --build
```

### Diferenças em produção:
- Sem volumes de desenvolvimento
- Start period mais longo para carregamento de modelos
- Configurações otimizadas de memória
- Logs reduzidos

## ⚙️ Configuração de Ambiente

### Variáveis obrigatórias (.env)
```bash
HUGGING_FACE_HUB_TOKEN=hf_your_token_here  # OBRIGATÓRIO
```

### Variáveis opcionais (.env)
```bash
# Modelo Whisper
VERSION_MODEL=turbo                    # turbo, base, small, medium, large
FORCE_CPU=true                        # true para usar CPU, false para GPU

# Logging  
LOG_LEVEL=INFO                        # DEBUG, INFO, WARNING, ERROR

# Recursos
MEMORY_LIMIT_BACKEND=6G               # Limite de memória do backend
MEMORY_LIMIT_FRONTEND=1G              # Limite de memória do frontend

# Frontend
NEXT_PUBLIC_API_URL=http://localhost:8000  # URL da API
NEXT_TELEMETRY_DISABLED=1             # Desabilitar telemetria
```

## 🔒 Segurança

- Containers executam como usuários não-root
- Network isolada para comunicação entre serviços
- Security opts configurados (`no-new-privileges`)
- Process init habilitado para melhor gerenciamento

## 🩺 Health Checks

Ambos os serviços possuem health checks configurados:

- **Backend**: `GET /health`
- **Frontend**: `GET /api/health`

Os health checks garantem que o frontend só inicie após o backend estar saudável.

## 🐛 Troubleshooting

### Container não inicia
```bash
# Verificar logs
docker compose logs <service_name>

# Verificar recursos do sistema
docker stats

# Verificar se portas estão disponíveis
netstat -tlnp | grep -E "(3000|8000)"
```

### Problemas de memória
- Backend usa até 6GB por padrão (ajuste `MEMORY_LIMIT_BACKEND`)
- GPU requer mais recursos que CPU
- Modelos grandes (large, large-v2) precisam mais memória

### Problemas de permissão
```bash
# Ajustar permissões das pastas
sudo chown -R $(whoami):$(whoami) public/ logs/
chmod -R 755 public/ logs/
```

### Token Hugging Face
- Obtenha em: https://huggingface.co/settings/tokens
- Tipo: "Read" é suficiente
- Necessário para modelos de diarização

## 📊 Monitoramento

### Recursos do sistema
```bash
# CPU e memória em tempo real
docker stats

# Uso de disco dos volumes
docker system df -v
```

### Logs estruturados
Os logs seguem formato estruturado com timestamps e níveis:
```
2024-XX-XX XX:XX:XX - module_name - LEVEL - Message
```

## 🔄 Atualizações

Para atualizar a aplicação:

```bash
# Parar serviços
docker compose down

# Atualizar código (git pull, etc.)
git pull

# Rebuild e reiniciar
docker compose up --build -d
```

## 💡 Dicas de Performance

1. **CPU vs GPU**: GPU é mais rápido mas requer mais configuração
2. **Modelos**: `turbo` é mais rápido, `large` mais preciso  
3. **Batch**: Upload múltiplo é mais eficiente
4. **Cache**: Volumes de cache aceleram reinicializações
5. **Memória**: Monitore uso para ajustar limites

---

Para dúvidas ou problemas, consulte os logs detalhados ou abra uma issue no repositório.