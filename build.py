#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    AutoSetup Empresarial - Build System                      ║
║                     Script de Compilação em Python                           ║
║                                                                              ║
║  Autor: Samuel Else                                                          ║
║  GitHub: https://github.com/SamuelElse/AutoSetup-Empresarial                 ║
║  Licença: MIT                                                                ║
╚══════════════════════════════════════════════════════════════════════════════╝

Este script compila o AutoSetup Empresarial em um executável único (.exe)
com todos os instaladores embutidos.

Uso:
    python build.py              # Build padrão
    python build.py --clean      # Limpa arquivos anteriores antes de compilar
    python build.py --no-console # Sem janela de console (padrão)
    python build.py --console    # Com janela de console (debug)
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path


# ══════════════════════════════════════════════════════════════════════════════
# CONFIGURAÇÕES DO BUILD
# ══════════════════════════════════════════════════════════════════════════════

APP_NAME = "AutoSetup_Empresarial"
MAIN_SCRIPT = "main.py"
ICON_FILE = "icon.ico"
INSTALLERS_FOLDER = "installers"

# Cores para output no terminal
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'


def print_header():
    """Exibe o cabeçalho do build"""
    print(f"""
{Colors.CYAN}================================================================
         AutoSetup Empresarial - Build System                   
================================================================{Colors.ENDC}
""")


def print_success(message: str):
    print(f"{Colors.GREEN}[OK] {message}{Colors.ENDC}")


def print_error(message: str):
    print(f"{Colors.FAIL}[ERRO] {message}{Colors.ENDC}")


def print_warning(message: str):
    print(f"{Colors.WARNING}[AVISO] {message}{Colors.ENDC}")


def print_info(message: str):
    print(f"{Colors.BLUE}[INFO] {message}{Colors.ENDC}")


def check_python():
    """Verifica a versão do Python"""
    version = sys.version_info
    print_info(f"Python {version.major}.{version.minor}.{version.micro} detectado")
    
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print_error("Python 3.8 ou superior é necessário!")
        return False
    
    print_success("Versão do Python OK")
    return True


def check_pyinstaller():
    """Verifica se PyInstaller está instalado"""
    try:
        import PyInstaller
        print_success(f"PyInstaller {PyInstaller.__version__} encontrado")
        return True
    except ImportError:
        print_warning("PyInstaller não encontrado. Instalando...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
            print_success("PyInstaller instalado com sucesso")
            return True
        except subprocess.CalledProcessError:
            print_error("Falha ao instalar PyInstaller")
            return False


def check_dependencies():
    """Verifica se todas as dependências estão instaladas"""
    print_info("Verificando dependências...")
    
    required = ["customtkinter", "PIL"]
    missing = []
    
    for module in required:
        try:
            __import__(module)
        except ImportError:
            missing.append(module)
    
    if missing:
        print_warning(f"Dependências faltando: {', '.join(missing)}")
        print_info("Instalando dependências...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
            print_success("Dependências instaladas")
        except subprocess.CalledProcessError:
            print_error("Falha ao instalar dependências")
            return False
    else:
        print_success("Todas as dependências OK")
    
    return True


def get_installers():
    """Lista os instaladores na pasta"""
    installers_path = Path(INSTALLERS_FOLDER)
    
    if not installers_path.exists():
        print_warning(f"Pasta '{INSTALLERS_FOLDER}' não encontrada. Criando...")
        installers_path.mkdir(exist_ok=True)
        return []
    
    installers = list(installers_path.glob("*.exe")) + list(installers_path.glob("*.msi"))
    
    if installers:
        print_info(f"Instaladores encontrados ({len(installers)}):")
        for installer in installers:
            size_mb = installer.stat().st_size / (1024 * 1024)
            print(f"    -> {installer.name} ({size_mb:.1f} MB)")
    else:
        print_warning("Nenhum instalador encontrado na pasta 'installers/'")
        print_warning("O executável será criado sem instaladores embutidos.")
    
    return installers


def clean_build():
    """Remove arquivos de build anteriores"""
    print_info("Limpando builds anteriores...")
    
    dirs_to_clean = ["build", "dist", "__pycache__"]
    files_to_clean = [f"{APP_NAME}.spec"]
    
    for dir_name in dirs_to_clean:
        if Path(dir_name).exists():
            shutil.rmtree(dir_name)
            print(f"    Removido: {dir_name}/")
    
    for file_name in files_to_clean:
        if Path(file_name).exists():
            Path(file_name).unlink()
            print(f"    Removido: {file_name}")
    
    print_success("Limpeza concluída")


def build_executable(console: bool = False):
    """Compila o executável usando PyInstaller"""
    print_info("Iniciando compilação...")
    print()
    
    # Monta os argumentos do PyInstaller
    args = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",
        "--name", APP_NAME,
        "--uac-admin",  # Solicita privilégios de administrador
        "--clean",
    ]
    
    # Console ou não
    if console:
        args.append("--console")
        print_info("Modo: COM janela de console (debug)")
    else:
        args.append("--noconsole")
        print_info("Modo: SEM janela de console (produção)")
    
    # Ícone (se existir)
    if Path(ICON_FILE).exists():
        args.extend(["--icon", ICON_FILE])
        print_info(f"Ícone: {ICON_FILE}")
    else:
        print_warning(f"Ícone '{ICON_FILE}' não encontrado. Usando ícone padrão.")
    
    # Adiciona a pasta de instaladores
    if Path(INSTALLERS_FOLDER).exists():
        args.extend(["--add-data", f"{INSTALLERS_FOLDER};{INSTALLERS_FOLDER}"])
        print_info(f"Incluindo pasta: {INSTALLERS_FOLDER}/")
    
    # Hidden imports para CustomTkinter
    args.extend([
        "--hidden-import", "customtkinter",
        "--hidden-import", "PIL",
        "--hidden-import", "PIL._tkinter_finder",
    ])
    
    # Script principal
    args.append(MAIN_SCRIPT)
    
    print()
    print(f"{Colors.CYAN}{'=' * 60}{Colors.ENDC}")
    print(f"{Colors.BOLD}Executando PyInstaller...{Colors.ENDC}")
    print(f"{Colors.CYAN}{'=' * 60}{Colors.ENDC}")
    print()
    
    # Executa PyInstaller
    try:
        result = subprocess.run(args, check=True)
        return True
    except subprocess.CalledProcessError as e:
        print_error(f"PyInstaller falhou com código {e.returncode}")
        return False


def show_result():
    """Mostra o resultado do build"""
    exe_path = Path("dist") / f"{APP_NAME}.exe"
    
    print()
    print(f"{Colors.CYAN}{'=' * 60}{Colors.ENDC}")
    
    if exe_path.exists():
        size_mb = exe_path.stat().st_size / (1024 * 1024)
        
        print(f"""
{Colors.GREEN}{Colors.BOLD}================================================================
              BUILD CONCLUIDO COM SUCESSO!                  
================================================================

  Executavel criado em:
     {str(exe_path)}

  Tamanho: {size_mb:.1f} MB

  O executavel solicita privilegios de administrador

================================================================{Colors.ENDC}
""")
        return True
    else:
        print_error("Executavel nao foi criado!")
        return False


def main():
    """Função principal"""
    print_header()
    
    # Parse argumentos
    clean = "--clean" in sys.argv
    console = "--console" in sys.argv
    
    # Verificações
    if not check_python():
        return 1
    
    if not check_pyinstaller():
        return 1
    
    if not check_dependencies():
        return 1
    
    print()
    
    # Lista instaladores
    get_installers()
    print()
    
    # Limpa se solicitado
    if clean:
        clean_build()
        print()
    
    # Compila
    if not build_executable(console=console):
        return 1
    
    # Mostra resultado
    if not show_result():
        return 1
    
    return 0


if __name__ == "__main__":
    try:
        # Habilita cores no Windows
        if sys.platform == "win32":
            os.system("color")
        
        exit_code = main()
        
        print()
        input("Pressione ENTER para fechar...")
        sys.exit(exit_code)
        
    except KeyboardInterrupt:
        print()
        print_warning("Build cancelado pelo usuário")
        sys.exit(1)
    except Exception as e:
        print_error(f"Erro inesperado: {e}")
        input("Pressione ENTER para fechar...")
        sys.exit(1)


