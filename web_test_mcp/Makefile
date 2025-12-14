# Makefile para MCP DevOps Agent
# Compila tudo em um binário executável para Linux ou Windows

# Variáveis
PYTHON := python3
PIP := pip3
PYINSTALLER := pyinstaller
PROJECT_NAME := mcp-agent-devops
VERSION := 1.0.0

# Detectar sistema operacional
ifeq ($(OS),Windows_NT)
    DETECTED_OS := Windows
    EXE_EXT := .exe
    CLEAN_CMD := del /Q
    MKDIR := mkdir
else
    DETECTED_OS := $(shell uname -s)
    EXE_EXT :=
    CLEAN_CMD := rm -rf
    MKDIR := mkdir -p
endif

# Cores para output
GREEN := \033[0;32m
YELLOW := \033[1;33m
RED := \033[0;31m
NC := \033[0m # No Color

# Diretórios
BUILD_DIR := build
DIST_DIR := dist
SPEC_DIR := spec

# Arquivos
MAIN_FILE := web_server.py
SPEC_FILE := $(PROJECT_NAME).spec

.PHONY: all clean install build build-linux build-windows build-onefile test help setup

# Target padrão
all: help

# Ajuda
help:
	@echo "$(GREEN)╔════════════════════════════════════════════════════╗$(NC)"
	@echo "$(GREEN)║      MCP DevOps Agent - Build System             ║$(NC)"
	@echo "$(GREEN)╚════════════════════════════════════════════════════╝$(NC)"
	@echo ""
	@echo "$(YELLOW)Targets disponíveis:$(NC)"
	@echo "  make install        - Instala dependências"
	@echo "  make build          - Build para o sistema atual"
	@echo "  make build-linux    - Build para Linux"
	@echo "  make build-windows  - Build para Windows"
	@echo "  make build-onefile  - Build em arquivo único"
	@echo "  make build-docker   - Build imagem Docker"
	@echo "  make clean          - Remove arquivos de build"
	@echo "  make test           - Testa o executável"
	@echo "  make package        - Cria pacote distribuível"
	@echo "  make setup          - Setup completo (install + build)"
	@echo ""
	@echo "$(YELLOW)Sistema detectado:$(NC) $(DETECTED_OS)"

# Instalar dependências
install:
	@echo "$(GREEN)📦 Instalando dependências...$(NC)"
	$(PIP) install -r requirements.txt
	$(PIP) install pyinstaller
	@echo "$(GREEN)✓ Dependências instaladas$(NC)"

# Setup completo
setup: install
	@echo "$(GREEN)🔧 Setup completo concluído!$(NC)"

# Build para sistema atual
build:
	@echo "$(GREEN)🔨 Compilando para $(DETECTED_OS)...$(NC)"
	$(PYINSTALLER) --name $(PROJECT_NAME) \
		--add-data "index.html:." \
		--add-data "mcp_pc_devops_agent.py:." \
		--hidden-import=mcp \
		--hidden-import=mcp.client \
		--hidden-import=mcp.server \
		--hidden-import=fastmcp \
		--hidden-import=groq \
		--hidden-import=aiohttp \
		--hidden-import=pyautogui \
		--collect-all mcp \
		--collect-all fastmcp \
		--noconfirm \
		$(MAIN_FILE)
	@echo "$(GREEN)✓ Build concluído: dist/$(PROJECT_NAME)/$(PROJECT_NAME)$(EXE_EXT)$(NC)"

# Build arquivo único (mais lento mas portável)
build-onefile:
	@echo "$(GREEN)🔨 Compilando em arquivo único...$(NC)"
	$(PYINSTALLER) --name $(PROJECT_NAME) \
		--onefile \
		--add-data "index.html:." \
		--add-data "mcp_pc_devops_agent.py:." \
		--hidden-import=mcp \
		--hidden-import=mcp.client \
		--hidden-import=mcp.server \
		--hidden-import=fastmcp \
		--hidden-import=groq \
		--hidden-import=aiohttp \
		--hidden-import=pyautogui \
		--collect-all mcp \
		--collect-all fastmcp \
		--noconfirm \
		$(MAIN_FILE)
	@echo "$(GREEN)✓ Build concluído: dist/$(PROJECT_NAME)$(EXE_EXT)$(NC)"

# Build específico para Linux
build-linux:
ifeq ($(DETECTED_OS),Linux)
	@echo "$(GREEN)🐧 Compilando para Linux...$(NC)"
	$(MAKE) build
else
	@echo "$(RED)❌ Este comando deve ser executado no Linux$(NC)"
	@exit 1
endif

# Build específico para Windows
build-windows:
ifeq ($(DETECTED_OS),Windows_NT)
	@echo "$(GREEN)🪟 Compilando para Windows...$(NC)"
	$(MAKE) build
else
	@echo "$(YELLOW)⚠ Para compilar para Windows no Linux, use Docker:$(NC)"
	@echo "  make build-windows-docker"
endif

# Build Windows via Docker (cross-compilation)
build-windows-docker:
	@echo "$(GREEN)🐋 Compilando para Windows usando Docker...$(NC)"
	docker run --rm -v "$(PWD):/src" \
		cdrx/pyinstaller-windows:python3 \
		"pyinstaller --name $(PROJECT_NAME) \
		--onefile \
		--add-data 'index.html;.' \
		--add-data 'mcp_pc_devops_agent.py;.' \
		--hidden-import=mcp \
		--hidden-import=fastmcp \
		--hidden-import=groq \
		--hidden-import=aiohttp \
		--collect-all mcp \
		--noconfirm \
		web_server.py"
	@echo "$(GREEN)✓ Build Windows concluído$(NC)"

# Build imagem Docker
build-docker:
	@echo "$(GREEN)🐋 Criando imagem Docker...$(NC)"
	docker build -t $(PROJECT_NAME):$(VERSION) .
	@echo "$(GREEN)✓ Imagem Docker criada: $(PROJECT_NAME):$(VERSION)$(NC)"

# Testar executável
test:
	@echo "$(GREEN)🧪 Testando executável...$(NC)"
	@if [ -f "dist/$(PROJECT_NAME)$(EXE_EXT)" ]; then \
		echo "$(GREEN)✓ Executável encontrado$(NC)"; \
		echo "$(YELLOW)Iniciando servidor de teste...$(NC)"; \
		dist/$(PROJECT_NAME)$(EXE_EXT) & \
		sleep 3; \
		curl -s http://localhost:8080/health || echo "$(RED)❌ Servidor não respondeu$(NC)"; \
		pkill -f $(PROJECT_NAME); \
	else \
		echo "$(RED)❌ Executável não encontrado. Execute 'make build' primeiro.$(NC)"; \
	fi

# Criar pacote distribuível
package: build
	@echo "$(GREEN)📦 Criando pacote distribuível...$(NC)"
	$(MKDIR) release
	@if [ "$(DETECTED_OS)" = "Windows_NT" ]; then \
		powershell Compress-Archive -Path dist/$(PROJECT_NAME) -DestinationPath release/$(PROJECT_NAME)-$(VERSION)-windows.zip; \
	else \
		tar -czf release/$(PROJECT_NAME)-$(VERSION)-$(shell uname -m).tar.gz -C dist $(PROJECT_NAME); \
	fi
	@echo "$(GREEN)✓ Pacote criado em: release/$(NC)"

# Limpar arquivos de build
clean:
	@echo "$(YELLOW)🧹 Limpando arquivos de build...$(NC)"
	$(CLEAN_CMD) $(BUILD_DIR) $(DIST_DIR) *.spec __pycache__ *.pyc
	@echo "$(GREEN)✓ Limpeza concluída$(NC)"

# Limpar tudo (incluindo dependências)
clean-all: clean
	@echo "$(YELLOW)🧹 Limpando tudo (incluindo venv)...$(NC)"
	$(CLEAN_CMD) venv .pytest_cache .mypy_cache
	@echo "$(GREEN)✓ Limpeza completa concluída$(NC)"

# Criar spec file customizado
create-spec:
	@echo "$(GREEN)📝 Criando spec file customizado...$(NC)"
	$(PYINSTALLER) --name $(PROJECT_NAME) \
		--add-data "index.html:." \
		--add-data "mcp_pc_devops_agent.py:." \
		--hidden-import=mcp \
		--hidden-import=fastmcp \
		--hidden-import=groq \
		--collect-all mcp \
		--noconfirm \
		$(MAIN_FILE)
	@echo "$(GREEN)✓ Spec file criado: $(PROJECT_NAME).spec$(NC)"

# Verificar ambiente
check:
	@echo "$(GREEN)🔍 Verificando ambiente...$(NC)"
	@echo "Python: $(shell $(PYTHON) --version)"
	@echo "Pip: $(shell $(PIP) --version)"
	@echo "Sistema: $(DETECTED_OS)"
	@echo "Diretório: $(shell pwd)"
	@$(PYTHON) -c "import mcp, groq, aiohttp; print('✓ Dependências principais OK')" || echo "$(RED)❌ Faltam dependências$(NC)"

# Executar diretamente (desenvolvimento)
run:
	@echo "$(GREEN)▶ Executando em modo desenvolvimento...$(NC)"
	$(PYTHON) $(MAIN_FILE)

# Criar ambiente virtual
venv:
	@echo "$(GREEN)🐍 Criando ambiente virtual...$(NC)"
	$(PYTHON) -m venv venv
	@echo "$(GREEN)✓ Ambiente virtual criado$(NC)"
	@echo "$(YELLOW)Ative com: source venv/bin/activate (Linux/Mac) ou venv\\Scripts\\activate (Windows)$(NC)"

# Build otimizado (produção)
build-prod: clean
	@echo "$(GREEN)🚀 Build otimizado para produção...$(NC)"
	$(PYINSTALLER) --name $(PROJECT_NAME) \
		--onefile \
		--windowed \
		--add-data "index.html:." \
		--add-data "mcp_pc_devops_agent.py:." \
		--hidden-import=mcp \
		--hidden-import=fastmcp \
		--hidden-import=groq \
		--hidden-import=aiohttp \
		--collect-all mcp \
		--strip \
		--noupx \
		--noconfirm \
		$(MAIN_FILE)
	@echo "$(GREEN)✓ Build de produção concluído$(NC)"

# Informações sobre o build
info:
	@echo "$(GREEN)ℹ Informações do Build$(NC)"
	@echo "────────────────────────────────"
	@echo "Projeto: $(PROJECT_NAME)"
	@echo "Versão: $(VERSION)"
	@echo "Sistema: $(DETECTED_OS)"
	@echo "Python: $(shell $(PYTHON) --version)"
	@if [ -f "dist/$(PROJECT_NAME)$(EXE_EXT)" ]; then \
		echo "Status: $(GREEN)✓ Build existe$(NC)"; \
		ls -lh dist/$(PROJECT_NAME)$(EXE_EXT) | awk '{print "Tamanho: " $$5}'; \
	else \
		echo "Status: $(RED)✗ Build não encontrado$(NC)"; \
	fi
