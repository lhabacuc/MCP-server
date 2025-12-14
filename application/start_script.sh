#!/bin/bash

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   MCP DevOps Agent - Web Interface   ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════╝${NC}"
echo ""

# Verificar Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 não encontrado!${NC}"
    echo "   Instale Python 3.8 ou superior"
    exit 1
fi

echo -e "${GREEN}✓${NC} Python encontrado: $(python3 --version)"

# Verificar GROQ_API_KEY
if [ -z "$GROQ_API_KEY" ]; then
    echo -e "${YELLOW}⚠${NC}  GROQ_API_KEY não configurada"
    echo ""
    read -p "   Digite sua GROQ API Key: " api_key
    export GROQ_API_KEY="$api_key"
    echo -e "${GREEN}✓${NC} API Key configurada"
fi

# Verificar DISPLAY (para Linux com GUI)
if [ -z "$DISPLAY" ] && [ "$(uname)" = "Linux" ]; then
    echo -e "${YELLOW}⚠${NC}  DISPLAY não configurado, usando :0"
    export DISPLAY=:0
fi

# Verificar se as dependências estão instaladas
echo ""
echo -e "${BLUE}Verificando dependências...${NC}"

missing_deps=0
for pkg in aiohttp groq mcp fastmcp; do
    if ! python3 -c "import $pkg" 2>/dev/null; then
        echo -e "${RED}✗${NC} $pkg não instalado"
        missing_deps=1
    else
        echo -e "${GREEN}✓${NC} $pkg instalado"
    fi
done

# Instalar dependências se necessário
if [ $missing_deps -eq 1 ]; then
    echo ""
    echo -e "${YELLOW}Instalando dependências...${NC}"
    pip3 install -r requirements.txt
fi

# Verificar se os arquivos necessários existem
echo ""
echo -e "${BLUE}Verificando arquivos...${NC}"

files=("mcp_pc_devops_agent.py" "web_server.py" "index.html")
for file in "${files[@]}"; do
    if [ ! -f "$file" ]; then
        echo -e "${RED}✗${NC} $file não encontrado"
        exit 1
    else
        echo -e "${GREEN}✓${NC} $file encontrado"
    fi
done

# Verificar porta 8080
if lsof -Pi :8080 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo ""
    echo -e "${YELLOW}⚠${NC}  Porta 8080 já está em uso"
    read -p "   Deseja parar o processo? (s/n): " stop_process
    if [ "$stop_process" = "s" ] || [ "$stop_process" = "S" ]; then
        kill $(lsof -t -i:8080) 2>/dev/null
        echo -e "${GREEN}✓${NC} Processo parado"
    else
        exit 1
    fi
fi

# Iniciar servidor
echo ""
echo -e "${GREEN}🚀 Iniciando servidor...${NC}"
echo ""
echo -e "${BLUE}   Interface Web:${NC} http://localhost:8080"
echo -e "${BLUE}   WebSocket:${NC}     ws://localhost:8080/ws"
echo -e "${BLUE}   Health Check:${NC}  http://localhost:8080/health"
echo ""
echo -e "${YELLOW}Pressione Ctrl+C para parar o servidor${NC}"
echo ""

# Abrir navegador automaticamente (opcional)
if command -v xdg-open &> /dev/null; then
    sleep 2 && xdg-open http://localhost:8080 &
elif command -v open &> /dev/null; then
    sleep 2 && open http://localhost:8080 &
fi

# Executar servidor
python3 web_server.py
