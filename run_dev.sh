#!/bin/bash

# Script para iniciar API e Frontend simultaneamente
# Alternativa em shell script para run_full_stack.py

set -e  # Para na primeira falha

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

# Função para cleanup quando script é interrompido
cleanup() {
    echo -e "\n${YELLOW}⏹️  Parando aplicações...${NC}"
    
    # Para todos os processos filhos
    if [[ -n $BACKEND_PID ]]; then
        echo -e "${RED}🛑 Parando backend (PID: $BACKEND_PID)${NC}"
        kill $BACKEND_PID 2>/dev/null || true
    fi
    
    if [[ -n $FRONTEND_PID ]]; then
        echo -e "${RED}🛑 Parando frontend (PID: $FRONTEND_PID)${NC}"
        kill $FRONTEND_PID 2>/dev/null || true
    fi
    
    # Mata processos por porta se necessário
    lsof -ti:8000 | xargs kill -9 2>/dev/null || true  # Backend
    lsof -ti:3000 | xargs kill -9 2>/dev/null || true  # Frontend
    
    echo -e "${GREEN}✅ Aplicações paradas${NC}"
    exit 0
}

# Captura sinais para cleanup
trap cleanup SIGINT SIGTERM EXIT

echo -e "${PURPLE}🔥 Iniciando Full Stack - API + Frontend${NC}"
echo "=================================================="

# Verifica se Node.js está instalado
if ! command -v node &> /dev/null; then
    echo -e "${RED}❌ Node.js não encontrado. Instale o Node.js primeiro.${NC}"
    exit 1
fi

# Verifica se Python está disponível
if ! command -v python3 &> /dev/null && ! command -v python &> /dev/null; then
    echo -e "${RED}❌ Python não encontrado.${NC}"
    exit 1
fi

# Define comando Python (prioriza venv se existir)
PYTHON_CMD="python3"
if ! command -v python3 &> /dev/null; then
    PYTHON_CMD="python"
fi

# Usa Python do venv se existir
if [[ -f "venv/bin/python" ]]; then
    PYTHON_CMD="venv/bin/python"
    echo -e "${GREEN}✅ Usando ambiente virtual${NC}"
elif [[ -f "venv/Scripts/python.exe" ]]; then
    PYTHON_CMD="venv/Scripts/python.exe"
    echo -e "${GREEN}✅ Usando ambiente virtual${NC}"
else
    echo -e "${YELLOW}⚠️  Ambiente virtual não encontrado, usando Python global${NC}"
    echo -e "${BLUE}💡 Para melhor compatibilidade, execute: python run_venv.py${NC}"
fi

# Instala dependências do frontend se necessário
if [[ ! -d "frontend/node_modules" ]]; then
    echo -e "${YELLOW}📦 Instalando dependências do frontend...${NC}"
    cd frontend && npm install && cd ..
    echo -e "${GREEN}✅ Dependências do frontend instaladas${NC}"
fi

# Inicia backend em background
echo -e "${BLUE}🚀 Iniciando backend (FastAPI)...${NC}"
$PYTHON_CMD main.py > backend.log 2>&1 &
BACKEND_PID=$!

# Aguarda backend inicializar
echo -e "${YELLOW}⏳ Aguardando backend inicializar...${NC}"
sleep 3

# Verifica se backend está rodando
if ! kill -0 $BACKEND_PID 2>/dev/null; then
    echo -e "${RED}❌ Falha ao iniciar backend. Verifique backend.log${NC}"
    cat backend.log
    exit 1
fi

# Inicia frontend em background
echo -e "${BLUE}🎨 Iniciando frontend (Next.js)...${NC}"
cd frontend && npm run dev > ../frontend.log 2>&1 &
FRONTEND_PID=$!
cd ..

# Aguarda frontend inicializar
echo -e "${YELLOW}⏳ Aguardando frontend inicializar...${NC}"
sleep 5

# Verifica se frontend está rodando
if ! kill -0 $FRONTEND_PID 2>/dev/null; then
    echo -e "${RED}❌ Falha ao iniciar frontend. Verifique frontend.log${NC}"
    cat frontend.log
    exit 1
fi

echo -e "\n${GREEN}🎉 Aplicações iniciadas com sucesso!${NC}"
echo -e "${BLUE}📝 URLs:${NC}"
echo -e "   Backend:  ${YELLOW}http://localhost:8000${NC}"
echo -e "   Docs API: ${YELLOW}http://localhost:8000/docs${NC}"
echo -e "   Frontend: ${YELLOW}http://localhost:3000${NC}"
echo ""
echo -e "${PURPLE}💡 Pressione Ctrl+C para parar ambas as aplicações${NC}"
echo -e "${BLUE}📋 Logs salvos em: backend.log e frontend.log${NC}"
echo "=================================================="

# Monitora processos em loop
while true; do
    # Verifica se backend ainda está rodando
    if ! kill -0 $BACKEND_PID 2>/dev/null; then
        echo -e "${RED}❌ Backend parou inesperadamente${NC}"
        break
    fi
    
    # Verifica se frontend ainda está rodando
    if ! kill -0 $FRONTEND_PID 2>/dev/null; then
        echo -e "${RED}❌ Frontend parou inesperadamente${NC}"
        break
    fi
    
    sleep 2
done

# Cleanup será chamado automaticamente pelo trap