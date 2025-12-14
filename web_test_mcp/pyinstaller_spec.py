# -*- mode: python ; coding: utf-8 -*-
"""
Arquivo de especificação PyInstaller customizado para MCP DevOps Agent
Permite builds otimizados e configuração avançada
"""

import sys
import os
from PyInstaller.utils.hooks import collect_all, collect_submodules

# Coletar todos os módulos necessários
datas = []
binaries = []
hiddenimports = []

# Adicionar arquivos de dados
datas += [
    ('index.html', '.'),
    ('mcp_pc_devops_agent.py', '.'),
]

# Coletar submódulos MCP
mcp_imports = collect_submodules('mcp')
hiddenimports += mcp_imports

# Coletar submódulos FastMCP
fastmcp_imports = collect_submodules('fastmcp')
hiddenimports += fastmcp_imports

# Imports adicionais necessários
hiddenimports += [
    'mcp',
    'mcp.client',
    'mcp.client.session',
    'mcp.client.stdio',
    'mcp.server',
    'mcp.server.fastmcp',
    'fastmcp',
    'groq',
    'aiohttp',
    'aiohttp.web',
    'pyautogui',
    'PIL',
    'asyncio',
]

# Coletar todos os arquivos do MCP
tmp_ret = collect_all('mcp')
datas += tmp_ret[0]
binaries += tmp_ret[1]
hiddenimports += tmp_ret[2]

# Coletar todos os arquivos do FastMCP
tmp_ret = collect_all('fastmcp')
datas += tmp_ret[0]
binaries += tmp_ret[1]
hiddenimports += tmp_ret[2]

# Analysis
a = Analysis(
    ['web_server.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib',
        'numpy',
        'pandas',
        'scipy',
        'pytest',
        'setuptools',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

# PYZ (arquivo de biblioteca Python compactado)
pyz = PYZ(
    a.pure,
    a.zipped_data,
    cipher=None,
)

# EXE (executável)
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='mcp-agent',
    debug=False,
    bootloader_ignore_signals=False,
    strip=True,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,  # Mude para False para Windows GUI
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # Adicione um ícone aqui se quiser
)

# Para criar um diretório ao invés de um arquivo único, use:
"""
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='mcp-agent',
    debug=False,
    bootloader_ignore_signals=False,
    strip=True,
    upx=True,
    console=True,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=True,
    upx=True,
    upx_exclude=[],
    name='mcp-agent',
)
"""
