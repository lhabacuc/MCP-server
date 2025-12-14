@echo off
REM ============================================
REM MCP DevOps Agent - Build Script para Windows
REM ============================================

echo.
echo ================================================
echo    MCP DevOps Agent - Build System (Windows)
echo ================================================
echo.

REM Verificar Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERRO] Python nao encontrado!
    echo Por favor, instale Python 3.8 ou superior
    pause
    exit /b 1
)

echo [OK] Python encontrado

REM Verificar pip
pip --version >nul 2>&1
if errorlevel 1 (
    echo [ERRO] pip nao encontrado!
    pause
    exit /b 1
)

echo [OK] pip encontrado

REM Menu de opcoes
:menu
echo.
echo Escolha uma opcao:
echo 1. Instalar dependencias
echo 2. Build completo (pasta)
echo 3. Build arquivo unico
echo 4. Build otimizado (producao)
echo 5. Limpar builds
echo 6. Testar executavel
echo 7. Criar pacote distribuivel
echo 0. Sair
echo.
set /p choice="Digite sua escolha: "

if "%choice%"=="1" goto install
if "%choice%"=="2" goto build
if "%choice%"=="3" goto build_onefile
if "%choice%"=="4" goto build_prod
if "%choice%"=="5" goto clean
if "%choice%"=="6" goto test
if "%choice%"=="7" goto package
if "%choice%"=="0" goto end
goto menu

:install
echo.
echo [*] Instalando dependencias...
pip install -r requirements.txt
pip install pyinstaller
echo [OK] Dependencias instaladas
pause
goto menu

:build
echo.
echo [*] Compilando (build completo)...
pyinstaller --name mcp-agent ^
    --add-data "index.html;." ^
    --add-data "mcp_pc_devops_agent.py;." ^
    --hidden-import=mcp ^
    --hidden-import=mcp.client ^
    --hidden-import=mcp.server ^
    --hidden-import=fastmcp ^
    --hidden-import=groq ^
    --hidden-import=aiohttp ^
    --hidden-import=pyautogui ^
    --collect-all mcp ^
    --collect-all fastmcp ^
    --noconfirm ^
    web_server.py
echo.
echo [OK] Build concluido: dist\mcp-agent\mcp-agent.exe
pause
goto menu

:build_onefile
echo.
echo [*] Compilando (arquivo unico)...
pyinstaller --name mcp-agent ^
    --onefile ^
    --add-data "index.html;." ^
    --add-data "mcp_pc_devops_agent.py;." ^
    --hidden-import=mcp ^
    --hidden-import=mcp.client ^
    --hidden-import=mcp.server ^
    --hidden-import=fastmcp ^
    --hidden-import=groq ^
    --hidden-import=aiohttp ^
    --hidden-import=pyautogui ^
    --collect-all mcp ^
    --collect-all fastmcp ^
    --noconfirm ^
    web_server.py
echo.
echo [OK] Build concluido: dist\mcp-agent.exe
pause
goto menu

:build_prod
echo.
echo [*] Compilando (otimizado para producao)...
pyinstaller --name mcp-agent ^
    --onefile ^
    --windowed ^
    --add-data "index.html;." ^
    --add-data "mcp_pc_devops_agent.py;." ^
    --hidden-import=mcp ^
    --hidden-import=fastmcp ^
    --hidden-import=groq ^
    --collect-all mcp ^
    --strip ^
    --noconfirm ^
    web_server.py
echo.
echo [OK] Build otimizado concluido
pause
goto menu

:clean
echo.
echo [*] Limpando builds...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist __pycache__ rmdir /s /q __pycache__
del /q *.spec 2>nul
echo [OK] Limpeza concluida
pause
goto menu

:test
echo.
echo [*] Testando executavel...
if exist dist\mcp-agent.exe (
    echo [OK] Executavel encontrado
    echo [*] Iniciando servidor de teste...
    start /B dist\mcp-agent.exe
    timeout /t 3 >nul
    curl -s http://localhost:8080/health
    taskkill /F /IM mcp-agent.exe >nul 2>&1
) else (
    echo [ERRO] Executavel nao encontrado
    echo Execute o build primeiro
)
pause
goto menu

:package
echo.
echo [*] Criando pacote distribuivel...
if not exist release mkdir release
if exist dist\mcp-agent.exe (
    powershell Compress-Archive -Path dist\mcp-agent.exe,index.html,mcp_pc_devops_agent.py -DestinationPath release\mcp-agent-windows.zip -Force
    echo [OK] Pacote criado: release\mcp-agent-windows.zip
) else (
    echo [ERRO] Executavel nao encontrado
    echo Execute o build primeiro
)
pause
goto menu

:end
echo.
echo Ate logo!
exit /b 0
