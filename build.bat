@echo off
REM ══════════════════════════════════════════════════════════════════════════════
REM AutoSetup Empresarial - Script de Build
REM ══════════════════════════════════════════════════════════════════════════════
REM
REM Este script compila o aplicativo em um único executável (.exe)
REM com todos os instaladores embutidos.
REM
REM Requisitos:
REM   1. Python 3.8+ instalado
REM   2. Dependências instaladas: pip install -r requirements.txt
REM   3. Instaladores colocados na pasta 'installers/'
REM
REM ══════════════════════════════════════════════════════════════════════════════

echo.
echo ╔══════════════════════════════════════════════════════════════════╗
echo ║           AutoSetup Empresarial - Build System                   ║
echo ╚══════════════════════════════════════════════════════════════════╝
echo.

REM Verifica se o Python está instalado
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERRO] Python nao encontrado! Instale o Python 3.8 ou superior.
    pause
    exit /b 1
)

REM Verifica se PyInstaller está instalado
python -c "import PyInstaller" >nul 2>&1
if %errorlevel% neq 0 (
    echo [INFO] Instalando PyInstaller...
    pip install pyinstaller
)

REM Verifica se existem arquivos na pasta installers
dir /b "installers\*.exe" >nul 2>&1
if %errorlevel% neq 0 (
    dir /b "installers\*.msi" >nul 2>&1
    if %errorlevel% neq 0 (
        echo [AVISO] Nenhum instalador encontrado na pasta 'installers/'
        echo         O executavel sera criado sem instaladores embutidos.
        echo.
    )
)

echo [INFO] Iniciando compilacao...
echo.

REM Compila o executável
pyinstaller ^
    --onefile ^
    --noconsole ^
    --name "AutoSetup_Empresarial" ^
    --icon "icon.ico" ^
    --add-data "installers;installers" ^
    --clean ^
    main.py

if %errorlevel% equ 0 (
    echo.
    echo ╔══════════════════════════════════════════════════════════════════╗
    echo ║                    BUILD CONCLUIDO COM SUCESSO!                  ║
    echo ╠══════════════════════════════════════════════════════════════════╣
    echo ║  O executavel foi criado em: dist\AutoSetup_Empresarial.exe     ║
    echo ╚══════════════════════════════════════════════════════════════════╝
) else (
    echo.
    echo [ERRO] Falha na compilacao. Verifique os erros acima.
)

echo.
pause

