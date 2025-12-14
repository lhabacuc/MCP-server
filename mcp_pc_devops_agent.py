import os
import subprocess
import logging
from typing import List

# =========================
# CONFIGURAR DISPLAY ANTES DE IMPORTAR PYAUTOGUI
# =========================
if 'DISPLAY' not in os.environ:
    os.environ['DISPLAY'] = ':0'

# Importação condicional do pyautogui
try:
    import pyautogui
    pyautogui.FAILSAFE = True
    PYAUTOGUI_AVAILABLE = True
except Exception as e:
    PYAUTOGUI_AVAILABLE = False
    print(f"⚠️  PyAutoGUI não disponível: {e}")

from mcp.server.fastmcp import FastMCP

# =========================
# CONFIGURAÇÕES GERAIS
# =========================
logging.basicConfig(level=logging.INFO)
app = FastMCP("mcp-devops-pc-agent")

# =========================
# DEVOPS / SISTEMA
# =========================
@app.tool()
def pwd() -> str:
    """Retorna o diretório atual"""
    return os.getcwd()

@app.tool()
def list_dir(path: str = ".") -> List[str]:
    """Lista arquivos e pastas"""
    return os.listdir(path)

@app.tool()
def read_file(path: str, start_line: int = 1, end_line: int = 500) -> str:
    """Lê um arquivo por intervalo de linhas"""
    with open(path, "r", encoding="utf-8") as f:
        lines = f.readlines()
    return "".join(lines[start_line - 1:end_line])

@app.tool()
def write_file(path: str, content: str) -> str:
    """Cria ou sobrescreve um arquivo"""
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    return "Arquivo escrito com sucesso"

@app.tool()
def append_file(path: str, content: str) -> str:
    """Adiciona conteúdo a um arquivo"""
    with open(path, "a", encoding="utf-8") as f:
        f.write(content)
    return "Conteúdo adicionado"

@app.tool()
def run_command(command: str) -> str:
    """
    Executa comandos no terminal (LOCAL)
    """
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=60
        )
        return f"STDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
    except Exception as e:
        return str(e)

# =========================
# GIT
# =========================
@app.tool()
def git_status() -> str:
    """Retorna o status do repositório Git"""
    return run_command("git status")

@app.tool()
def git_diff() -> str:
    """Mostra diferenças não commitadas"""
    return run_command("git diff")

@app.tool()
def git_log(n: int = 5) -> str:
    """Mostra histórico de commits"""
    return run_command(f"git log -n {n} --oneline")

@app.tool()
def git_add(files: str = ".") -> str:
    """Adiciona arquivos ao stage"""
    return run_command(f"git add {files}")

@app.tool()
def git_commit(message: str) -> str:
    """Cria um commit"""
    return run_command(f'git commit -m "{message}"')

@app.tool()
def git_push(branch: str = "main") -> str:
    """Faz push para o repositório remoto"""
    return run_command(f"git push origin {branch}")

# =========================
# AUTOMAÇÃO DE PC (pyautogui)
# =========================
if PYAUTOGUI_AVAILABLE:
    @app.tool()
    def screen_size() -> str:
        """Retorna resolução da tela"""
        width, height = pyautogui.size()
        return f"{width}x{height}"

    @app.tool()
    def mouse_position() -> str:
        """Retorna posição atual do mouse"""
        x, y = pyautogui.position()
        return f"x={x}, y={y}"

    @app.tool()
    def move_mouse(x: int, y: int, duration: float = 0.2) -> str:
        """Move o mouse para coordenadas específicas"""
        pyautogui.moveTo(x, y, duration=duration)
        return f"Mouse movido para ({x}, {y})"

    @app.tool()
    def click(x: int = None, y: int = None, button: str = "left") -> str:
        """Clica com o mouse"""
        pyautogui.click(x=x, y=y, button=button)
        return f"Clique {button} executado"

    @app.tool()
    def double_click(x: int = None, y: int = None) -> str:
        """Clique duplo"""
        pyautogui.doubleClick(x=x, y=y)
        return "Clique duplo executado"

    @app.tool()
    def right_click(x: int = None, y: int = None) -> str:
        """Clique direito"""
        pyautogui.rightClick(x=x, y=y)
        return "Clique direito executado"

    @app.tool()
    def type_text(text: str, interval: float = 0.02) -> str:
        """Digita texto no teclado"""
        pyautogui.write(text, interval=interval)
        return f"Texto digitado: '{text}'"

    @app.tool()
    def press_key(key: str) -> str:
        """Pressiona uma tecla específica"""
        pyautogui.press(key)
        return f"Tecla '{key}' pressionada"

    @app.tool()
    def hotkey(*keys: str) -> str:
        """Executa combinação de teclas (ex: ctrl, c)"""
        pyautogui.hotkey(*keys)
        return f"Combinação executada: {'+'.join(keys)}"

    @app.tool()
    def screenshot(path: str = "screenshot.png") -> str:
        """Captura screenshot e salva em arquivo"""
        img = pyautogui.screenshot()
        img.save(path)
        return f"Screenshot salva em {path}"

    @app.tool()
    def scroll(clicks: int, x: int = None, y: int = None) -> str:
        """Rola a página (positivo = cima, negativo = baixo)"""
        pyautogui.scroll(clicks, x=x, y=y)
        return f"Scrolled {clicks} clicks"

# =========================
# CONTROLE / SEGURANÇA
# =========================
@app.tool()
def wait(seconds: float) -> str:
    """Pausa execução por N segundos"""
    import time
    time.sleep(seconds)
    return f"Aguardou {seconds} segundos"

@app.tool()
def abort() -> str:
    """Abortar execução (emergência)"""
    raise RuntimeError("Execução abortada manualmente pelo usuário")

# =========================
# INFORMAÇÕES DO SISTEMA
# =========================
@app.tool()
def system_info() -> str:
    """Retorna informações do sistema"""
    import platform
    info = {
        "Sistema": platform.system(),
        "Versão": platform.version(),
        "Arquitetura": platform.machine(),
        "Processador": platform.processor(),
        "Python": platform.python_version(),
        "Diretório atual": os.getcwd(),
        "PyAutoGUI disponível": PYAUTOGUI_AVAILABLE
    }
    return "\n".join([f"{k}: {v}" for k, v in info.items()])

# =========================
# MAIN
# =========================
if __name__ == "__main__":
    print("🚀 Servidor MCP DevOps PC Agent iniciado")
    print(f"   PyAutoGUI: {'✓ Disponível' if PYAUTOGUI_AVAILABLE else '✗ Não disponível'}")
    print(f"   DISPLAY: {os.environ.get('DISPLAY', 'não configurado')}")
    app.run()
