#!/bin/bash

# ============================================
# MCP DevOps Agent - Quick Build Script
# Compila tudo em um comando
# ============================================

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m'

clear
echo -e "${CYAN}"
cat << "EOF"
╔════════════════════════════════════════════════════╗
║                                                    ║
║         MCP DevOps Agent - Quick Build            ║
║              Compilação Automatizada               ║
║                                                    ║
╚════════════════════════════════════════════════════╝
EOF
echo -e "${NC}"

function	log_info()
{
    echo -e "${BLUE}ℹ${NC}  $1"
}

function	log_success()
{
    echo -e "${GREEN}✓${NC}  $1"
}

function	log_error()
{
    echo -e "${RED}✗${NC}  $1"
}

function	log_warning()
{
    echo -e "${YELLOW}⚠${NC}  $1"
}

log_info "Verificando Python..."
if ! command -v python3 &> /dev/null; then
    log_error "Python 3 não encontrado!"
    log_warning "Instale Python 3.8 ou superior"
    exit 1
fi
PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
log_success "Python $PYTHON_VERSION encontrado"

log_info "Verificando pip..."
if ! command -v pip3 &> /dev/null; then
    log_error "pip não encontrado!"
    exit 1
fi
log_success "pip encontrado"

echo ""
echo -e "${YELLOW}Escolha o tipo de build:${NC}"
echo "1) Build rápido (diretório)"
echo "2) Build portável (arquivo único) ⭐ Recomendado"
echo "3) Build otimizado (produção)"
echo "4) Build + Testar"
echo "5) Build + Empacotar"
echo ""
read -p "Digite sua escolha (1-5): " BUILD_TYPE

if [[ ! "$BUILD_TYPE" =~ ^[1-5]$ ]]; then
    log_error "Escolha inválida!"
    exit 1
fi

echo ""
log_info "Instalando dependências..."
pip3 install -q -r requirements.txt
pip3 install -q pyinstaller
log_success "Dependências instaladas"

if [ -d "dist" ] || [ -d "build" ]; then
    log_info "Limpando builds anteriores..."
    rm -rf dist build *.spec
    log_success "Limpeza concluída"
fi

echo ""
case $BUILD_TYPE in
    1)
        log_info "Iniciando build rápido (diretório)..."
        pyinstaller --name mcp-agent \
            --add-data "index.html:." \
            --add-data "mcp_pc_devops_agent.py:." \
            --hidden-import=mcp \
            --hidden-import=fastmcp \
            --hidden-import=groq \
            --collect-all mcp \
            --noconfirm \
            web_server.py > /dev/null 2>&1
        BUILD_PATH="dist/mcp-agent/mcp-agent"
        ;;
    2)
        log_info "Iniciando build portável (arquivo único)..."
        pyinstaller --name mcp-agent \
            --onefile \
            --add-data "index.html:." \
            --add-data "mcp_pc_devops_agent.py:." \
            --hidden-import=mcp \
            --hidden-import=fastmcp \
            --hidden-import=groq \
            --collect-all mcp \
            --noconfirm \
            web_server.py > /dev/null 2>&1
        BUILD_PATH="dist/mcp-agent"
        ;;
    3)
        log_info "Iniciando build otimizado (produção)..."
        pyinstaller --name mcp-agent \
            --onefile \
            --add-data "index.html:." \
            --add-data "mcp_pc_devops_agent.py:." \
            --hidden-import=mcp \
            --hidden-import=fastmcp \
            --hidden-import=groq \
            --collect-all mcp \
            --strip \
            --noconfirm \
            web_server.py > /dev/null 2>&1
        BUILD_PATH="dist/mcp-agent"
        ;;
    4|5)
        log_info "Iniciando build portável..."
        pyinstaller --name mcp-agent \
            --onefile \
            --add-data "index.html:." \
            --add-data "mcp_pc_devops_agent.py:." \
            --hidden-import=mcp \
            --hidden-import=fastmcp \
            --hidden-import=groq \
            --collect-all mcp \
            --noconfirm \
            web_server.py > /dev/null 2>&1
        BUILD_PATH="dist/mcp-agent"
        ;;
esac

if [ -f "$BUILD_PATH" ]; then
    log_success "Build concluído com sucesso!"
    
    echo ""
    echo -e "${CYAN}╔════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║            Informações do Build                   ║${NC}"
    echo -e "${CYAN}╚════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "  ${PURPLE}📦 Executável:${NC} $BUILD_PATH"
    echo -e "  ${PURPLE}📏 Tamanho:${NC}    $(du -h $BUILD_PATH | cut -f1)"
    echo -e "  ${PURPLE}🕐 Data:${NC}       $(date)"
    echo ""
    
    if [ "$BUILD_TYPE" = "4" ]; then
        echo ""
        log_info "Testando executável..."
        
        if [ -z "$GROQ_API_KEY" ]; then
            log_warning "GROQ_API_KEY não configurada"
            read -p "Digite sua GROQ API Key: " GROQ_API_KEY
            export GROQ_API_KEY
        fi
        
        $BUILD_PATH &
        SERVER_PID=$!
        sleep 3
        
        if curl -s http://localhost:8080/health > /dev/null; then
            log_success "Servidor respondendo corretamente!"
            echo ""
            echo -e "${GREEN}🌐 Acesse: http://localhost:8080${NC}"
        else
            log_error "Servidor não respondeu"
        fi
        
        echo ""
        read -p "Manter servidor rodando? (s/n): " KEEP_RUNNING
        if [[ ! "$KEEP_RUNNING" =~ ^[Ss]$ ]]; then
            kill $SERVER_PID 2>/dev/null
            log_info "Servidor parado"
        fi
    fi
    
    if [ "$BUILD_TYPE" = "5" ]; then
        echo ""
        log_info "Criando pacote distribuível..."
        
        mkdir -p release
        PACKAGE_NAME="mcp-agent-$(uname -m)-$(date +%Y%m%d).tar.gz"
        
        tar -czf "release/$PACKAGE_NAME" \
            -C dist mcp-agent \
            -C .. index.html \
            -C . mcp_pc_devops_agent.py
        
        log_success "Pacote criado: release/$PACKAGE_NAME"
        echo -e "  ${PURPLE}📦 Tamanho:${NC} $(du -h release/$PACKAGE_NAME | cut -f1)"
    fi
    
    echo ""
    echo -e "${CYAN}╔════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║              Build Finalizado! 🎉                  ║${NC}"
    echo -e "${CYAN}╚════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${GREEN}Para executar:${NC}"
    echo -e "  ${YELLOW}$BUILD_PATH${NC}"
    echo ""
    echo -e "${GREEN}Ou configure a API key e execute:${NC}"
    echo -e "  ${YELLOW}export GROQ_API_KEY='sua_chave'${NC}"
    echo -e "  ${YELLOW}$BUILD_PATH${NC}"
    echo ""
    
else
    log_error "Build falhou!"
    log_warning "Verifique os logs acima para mais detalhes"
    exit 1
fi
