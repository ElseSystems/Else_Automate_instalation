# -*- mode: python ; coding: utf-8 -*-
# ══════════════════════════════════════════════════════════════════════════════
# AutoSetup Empresarial - Arquivo de Especificação PyInstaller
# ══════════════════════════════════════════════════════════════════════════════
#
# Para compilar usando este arquivo:
#   pyinstaller AutoSetup_Empresarial.spec
#
# Este arquivo oferece mais controle sobre o processo de build
# ══════════════════════════════════════════════════════════════════════════════

import os
from pathlib import Path

# Diretório do projeto
PROJECT_ROOT = Path(SPECPATH)

# Coleta todos os arquivos da pasta installers
installers_folder = PROJECT_ROOT / 'installers'
installer_files = []

if installers_folder.exists():
    for file in installers_folder.iterdir():
        if file.suffix.lower() in ['.exe', '.msi']:
            installer_files.append((str(file), 'installers'))

# Configuração do Analysis
a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=installer_files,  # Inclui os instaladores
    hiddenimports=[
        'customtkinter',
        'PIL',
        'PIL._tkinter_finder',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)

# Remove arquivos desnecessários para reduzir tamanho
a.datas = [x for x in a.datas if not x[0].startswith('tcl/tzdata')]

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='AutoSetup_Empresarial',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,  # Compressão UPX (se disponível)
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Sem janela de console
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon.ico' if (PROJECT_ROOT / 'icon.ico').exists() else None,
    version='version_info.txt' if (PROJECT_ROOT / 'version_info.txt').exists() else None,
)

