# Frontend - Sistema de Transcrição de Áudio

Frontend Next.js para o sistema de transcrição de áudio usando WhisperX.

## 🚀 Funcionalidades

- **Upload de Arquivos**: Suporte para áudio e vídeo com progress bar
- **Múltiplos Modos**:
  - Transcrição de áudio direto
  - Extração de áudio de vídeo + transcrições automáticas (4 variações)
  - Extração de frames de vídeo
- **Dashboard em Tempo Real**: Acompanhe o status das transcrições
- **Download de Resultados**: Baixe as transcrições concluídas
- **Interface Responsiva**: Funciona bem em desktop e mobile

## 🛠️ Tecnologias

- **Next.js 15** com App Router
- **TypeScript** para tipagem segura
- **Tailwind CSS** para estilização
- **Lucide React** para ícones
- **Axios** para comunicação com API

## ⚙️ Configuração

### 1. Instalar Dependências
```bash
npm install
```

### 2. Configurar Variáveis de Ambiente
Crie o arquivo `.env.local`:
```bash
# URL da API FastAPI
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### 3. Executar em Desenvolvimento
```bash
npm run dev
```

Acesse: http://localhost:3000

## 📁 Estrutura do Projeto

```
frontend/
├── src/
│   ├── app/
│   │   └── page.tsx              # Página principal
│   ├── components/
│   │   ├── FileUploader.tsx      # Componente de upload
│   │   └── TranscriptionDashboard.tsx # Dashboard de tarefas
│   └── lib/
│       ├── api.ts                # Cliente para API FastAPI
│       └── types.ts              # Tipos TypeScript
├── .env.local                    # Variáveis de ambiente
└── README.md
```

## 🎯 Componentes Principais

### FileUploader
- Upload por drag & drop ou seleção
- 3 modos: áudio, vídeo (transcrição), vídeo (frames)
- Configurações personalizáveis
- Progress bar em tempo real

### TranscriptionDashboard
- Lista todas as transcrições
- Filtros por status e busca por nome
- Polling automático para atualizações
- Download de arquivos concluídos
- Estatísticas resumidas

### API Client
- Tipagem completa baseada nos schemas Pydantic
- Polling inteligente para status de tarefas
- Upload com progress tracking
- Tratamento de erros

## 🔌 Integração com Backend

O frontend se comunica com a API FastAPI através dos endpoints:
- `POST /transcribe/` - Upload e transcrição de áudio
- `POST /transcribe/extract-audio` - Upload de vídeo + transcrições
- `POST /transcribe/extract-frames` - Extração de frames
- `GET /transcribe/` - Listar transcrições
- `GET /transcribe/{id}` - Status de tarefa específica
- `GET /transcribe/{id}/download` - Download de transcrição

## 🏃‍♂️ Como Usar

### 1. Iniciar Backend
Certifique-se de que a API FastAPI esteja rodando:
```bash
cd ..  # volta para pasta raiz
python main.py  # ou python run_local.py
```

### 2. Iniciar Frontend
```bash
npm run dev
```

### 3. Usar a Interface
1. **Upload**: Selecione áudio/vídeo e configure opções
2. **Aguardar**: Veja o progresso no dashboard
3. **Download**: Baixe as transcrições concluídas

## 📋 Variações de Transcrição (Vídeo)

Ao fazer upload de vídeo, são criadas 4 transcrições automaticamente:
- **limpa**: Apenas texto, sem timestamps nem diarização
- **timestamps**: Com timestamps, sem diarização
- **diarization**: Sem timestamps, com identificação de falantes
- **completa**: Com timestamps e diarização

## 🎨 Customização

### Temas
O projeto usa Tailwind CSS. Para personalizar cores:
```css
/* tailwind.config.js */
theme: {
  extend: {
    colors: {
      primary: '#1d4ed8',  // azul customizado
    }
  }
}
```

### API URL
Para produção, ajuste a variável de ambiente:
```bash
NEXT_PUBLIC_API_URL=https://sua-api.com
```

## 🚀 Produção

### Build
```bash
npm run build
npm run start
```

### Deploy
O projeto pode ser implantado em:
- **Vercel** (recomendado para Next.js)
- **Netlify**
- **Docker**

### Docker (Opcional)
```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
RUN npm run build
EXPOSE 3000
CMD ["npm", "start"]
```

## 🔧 Scripts Disponíveis

- `npm run dev` - Desenvolvimento
- `npm run build` - Build para produção
- `npm run start` - Executar build
- `npm run lint` - Linting do código

## 🆘 Solução de Problemas

### API não conecta
- Verifique se a API FastAPI está rodando na porta 8000
- Confirme a URL em `.env.local`
- Verifique se o CORS está configurado no backend

### Upload falha
- Verifique os formatos de arquivo suportados
- Confirme os limites de tamanho (100MB áudio, 500MB vídeo)
- Veja os logs da API para detalhes do erro

### Polling não funciona
- Verifique conexão com a API
- Confirme se o task_id está correto
- Veja o console do navegador para erros

## 📝 TODO

- [ ] Autenticação de usuários
- [ ] Histórico persistente
- [ ] Notificações em tempo real (WebSocket)
- [ ] Preview de transcrições
- [ ] Configurações avançadas de modelo
- [ ] Suporte a múltiplos idiomas
