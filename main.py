# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║                    AUTOSETUP EMPRESARIAL v1.0                                ║
# ║              Assistente de Pós-Formatação Automatizado                       ║
# ║                                                                              ║
# ║  Autor: Samuel Else                                                          ║
# ║  GitHub: https://github.com/SamuelElse/AutoSetup-Empresarial                 ║
# ║  Licença: MIT                                                                ║
# ╚══════════════════════════════════════════════════════════════════════════════╝
#
# Descrição:
#   Ferramenta para automatizar a instalação de softwares após formatação.
#   Permite instalação expressa, personalizada, com arquivos locais ou da nuvem.
#
# Uso:
#   python main.py           # Executa a aplicação
#   python build.py          # Compila para executável (.exe)
#
# Documentação completa: README.md

import os
import sys
import json
import shutil
import subprocess
import threading
import uuid
import tempfile
import urllib.request
import urllib.error
import ssl
import ctypes
import webbrowser
from tkinter import filedialog
from typing import List, Dict, Optional, Callable
from datetime import datetime

# ══════════════════════════════════════════════════════════════════════════════
# ELEVAÇÃO DE PRIVILÉGIOS - SOLICITAR ADMINISTRADOR
# ══════════════════════════════════════════════════════════════════════════════

def is_admin() -> bool:
    """Verifica se o programa está rodando como administrador"""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except:
        return False


def run_as_admin():
    """
    Reinicia o programa com privilégios de administrador.
    Mostra o prompt do UAC (Controle de Conta de Usuário).
    """
    if sys.platform != "win32":
        return False
    
    try:
        # Obtém o caminho do executável
        if getattr(sys, 'frozen', False):
            # Rodando como executável compilado
            script = sys.executable
        else:
            # Rodando como script Python
            script = sys.executable
            # Adiciona o script como argumento
        
        # Parâmetros para ShellExecuteW
        # Verifica se é um script ou executável
        if getattr(sys, 'frozen', False):
            params = ""
        else:
            params = f'"{os.path.abspath(__file__)}"'
        
        # Solicita elevação usando ShellExecuteW
        # "runas" = executar como administrador
        result = ctypes.windll.shell32.ShellExecuteW(
            None,           # hwnd
            "runas",        # operação (executar como admin)
            script,         # arquivo
            params,         # parâmetros
            None,           # diretório
            1               # SW_SHOWNORMAL
        )
        
        # Se result > 32, a operação foi bem sucedida
        return result > 32
        
    except Exception as e:
        print(f"Erro ao solicitar elevação: {e}")
        return False


def ensure_admin():
    """
    Garante que o programa está rodando como administrador.
    Se não estiver, solicita elevação e fecha a instância atual.
    """
    if sys.platform != "win32":
        return  # Não aplicável em outros sistemas
    
    if not is_admin():
        # Tenta reiniciar como admin
        if run_as_admin():
            # Fecha esta instância (a nova com admin vai abrir)
            sys.exit(0)
        else:
            # Se o usuário cancelou o UAC ou houve erro, 
            # continua sem admin (algumas funções podem falhar)
            pass


# Solicita privilégios de administrador ANTES de importar GUI
# para evitar múltiplas janelas
ensure_admin()


import customtkinter as ctk
from customtkinter import CTkImage
from PIL import Image

# ══════════════════════════════════════════════════════════════════════════════
# CONFIGURAÇÃO DE CAMINHOS - MODO PORTÁTIL (PENDRIVE)
# ══════════════════════════════════════════════════════════════════════════════

def get_exe_directory() -> str:
    """
    Retorna o diretório onde o executável está localizado.
    Funciona tanto em desenvolvimento quanto compilado.
    
    MODO PORTÁTIL: Sempre usa o diretório do executável/script,
    permitindo que o programa rode de um pendrive.
    """
    if getattr(sys, 'frozen', False):
        # Executável compilado - usa o diretório do .exe
        return os.path.dirname(sys.executable)
    else:
        # Rodando como script Python
        return os.path.dirname(os.path.abspath(__file__))


def resource_path(relative_path: str) -> str:
    """
    Retorna o caminho absoluto para recursos embutidos no executável.
    """
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.dirname(os.path.abspath(__file__))
    
    return os.path.join(base_path, relative_path)


def get_app_data_path() -> str:
    """
    Retorna o caminho para dados persistentes da aplicação.
    
    MODO PORTÁTIL: Usa o mesmo diretório do executável,
    não usa AppData. Permite rodar de pendrive.
    """
    app_data = get_exe_directory()
    return app_data


def get_installers_path() -> str:
    """
    Retorna o caminho da pasta de instaladores.
    
    MODO PORTÁTIL: A pasta 'installers' fica no mesmo
    diretório do executável (ex: pendrive).
    """
    path = os.path.join(get_exe_directory(), "installers")
    os.makedirs(path, exist_ok=True)
    return path


def get_temp_download_path() -> str:
    """Retorna o caminho para downloads temporários"""
    path = os.path.join(tempfile.gettempdir(), "AutoSetupDownloads")
    os.makedirs(path, exist_ok=True)
    return path


# ══════════════════════════════════════════════════════════════════════════════
# DOWNLOAD MANAGER - BAIXAR ARQUIVOS DA NUVEM
# ══════════════════════════════════════════════════════════════════════════════

class DownloadResult:
    """Resultado de um download"""
    def __init__(self, success: bool, filepath: str = "", message: str = ""):
        self.success = success
        self.filepath = filepath
        self.message = message


def download_with_urllib(url: str, dest_path: str, progress_callback: Optional[Callable] = None) -> DownloadResult:
    """
    Tenta baixar usando urllib com headers completos de navegador.
    """
    try:
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        
        # Headers completos para parecer um navegador real
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0',
        }
        
        request = urllib.request.Request(url, headers=headers)
        
        with urllib.request.urlopen(request, context=ssl_context, timeout=120) as response:
            total_size = response.headers.get('Content-Length')
            total_size = int(total_size) if total_size else 0
            
            downloaded = 0
            block_size = 65536  # 64KB para downloads mais rápidos
            
            with open(dest_path, 'wb') as f:
                while True:
                    buffer = response.read(block_size)
                    if not buffer:
                        break
                    
                    downloaded += len(buffer)
                    f.write(buffer)
                    
                    if progress_callback and total_size > 0:
                        percent = (downloaded / total_size) * 100
                        progress_callback(percent, downloaded, total_size)
        
        # Verifica se o arquivo foi baixado corretamente
        if os.path.exists(dest_path) and os.path.getsize(dest_path) > 0:
            return DownloadResult(success=True, filepath=dest_path, message="Download concluído")
        else:
            return DownloadResult(success=False, message="Arquivo vazio ou não criado")
            
    except urllib.error.HTTPError as e:
        return DownloadResult(success=False, message=f"HTTP {e.code}: {e.reason}")
    except urllib.error.URLError as e:
        return DownloadResult(success=False, message=f"Erro de conexão: {str(e.reason)}")
    except Exception as e:
        return DownloadResult(success=False, message=f"Erro: {str(e)}")


def download_with_powershell(url: str, dest_path: str) -> DownloadResult:
    """
    Usa PowerShell para baixar (mais confiável no Windows para URLs protegidas).
    O PowerShell usa as configurações de proxy e certificados do sistema.
    """
    try:
        # Comando PowerShell para download
        ps_command = f'''
        [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
        $ProgressPreference = 'SilentlyContinue'
        try {{
            Invoke-WebRequest -Uri "{url}" -OutFile "{dest_path}" -UseBasicParsing -ErrorAction Stop
            Write-Output "SUCCESS"
        }} catch {{
            Write-Output "ERROR: $($_.Exception.Message)"
        }}
        '''
        
        result = subprocess.run(
            ['powershell', '-NoProfile', '-NonInteractive', '-Command', ps_command],
            capture_output=True,
            text=True,
            timeout=300,  # 5 minutos de timeout
            creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
        )
        
        output = result.stdout.strip()
        
        if "SUCCESS" in output and os.path.exists(dest_path) and os.path.getsize(dest_path) > 0:
            return DownloadResult(success=True, filepath=dest_path, message="Download concluído via PowerShell")
        else:
            error_msg = output.replace("ERROR:", "").strip() if "ERROR:" in output else "Falha no download"
            return DownloadResult(success=False, message=error_msg)
            
    except subprocess.TimeoutExpired:
        return DownloadResult(success=False, message="Timeout: download demorou mais de 5 minutos")
    except Exception as e:
        return DownloadResult(success=False, message=f"Erro PowerShell: {str(e)}")


def download_with_curl(url: str, dest_path: str) -> DownloadResult:
    """
    Usa curl como fallback (disponível no Windows 10+).
    """
    try:
        result = subprocess.run(
            [
                'curl', '-L', '-o', dest_path,
                '-A', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                '--connect-timeout', '30',
                '--max-time', '300',
                '-s', '-S',  # Silent mas mostra erros
                url
            ],
            capture_output=True,
            text=True,
            timeout=320,
            creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
        )
        
        if result.returncode == 0 and os.path.exists(dest_path) and os.path.getsize(dest_path) > 0:
            return DownloadResult(success=True, filepath=dest_path, message="Download concluído via curl")
        else:
            return DownloadResult(success=False, message=result.stderr or "Falha no download com curl")
            
    except FileNotFoundError:
        return DownloadResult(success=False, message="curl não encontrado")
    except Exception as e:
        return DownloadResult(success=False, message=f"Erro curl: {str(e)}")


def download_file(url: str, filename: str, progress_callback: Optional[Callable] = None) -> DownloadResult:
    """
    Baixa um arquivo da URL especificada usando múltiplos métodos como fallback.
    
    Ordem de tentativa:
    1. urllib com headers de navegador
    2. PowerShell (usa credenciais do sistema)
    3. curl (disponível no Windows 10+)
    
    Args:
        url: URL do arquivo para download
        filename: Nome do arquivo a ser salvo
        progress_callback: Função opcional para reportar progresso
    
    Returns:
        DownloadResult com status e caminho do arquivo
    """
    dest_path = os.path.join(get_temp_download_path(), filename)
    
    # Remove arquivo existente se houver
    if os.path.exists(dest_path):
        try:
            os.remove(dest_path)
        except:
            pass
    
    # Método 1: urllib (mais rápido, funciona para a maioria dos casos)
    result = download_with_urllib(url, dest_path, progress_callback)
    if result.success:
        return result
    
    urllib_error = result.message
    
    # Método 2: PowerShell (usa configurações do sistema, bom para URLs corporativas)
    if sys.platform == "win32":
        result = download_with_powershell(url, dest_path)
        if result.success:
            return result
        
        powershell_error = result.message
        
        # Método 3: curl (fallback final)
        result = download_with_curl(url, dest_path)
        if result.success:
            return result
        
        curl_error = result.message
        
        # Todos os métodos falharam
        return DownloadResult(
            success=False,
            message=f"Todos os métodos falharam. urllib: {urllib_error}"
        )
    
    return DownloadResult(success=False, message=urllib_error)


def extract_filename_from_url(url: str) -> str:
    """Extrai o nome do arquivo de uma URL"""
    # Remove parâmetros da URL
    clean_url = url.split('?')[0]
    # Pega o último segmento
    filename = os.path.basename(clean_url)
    # Se não tiver extensão válida, usa um nome genérico
    if not filename or '.' not in filename:
        filename = "installer.exe"
    return filename


# ══════════════════════════════════════════════════════════════════════════════
# CATÁLOGO DE SOFTWARE - PADRÃO E PERSISTÊNCIA
# ══════════════════════════════════════════════════════════════════════════════

DEFAULT_SOFTWARE_CATALOG: List[Dict] = [
    {
        "id": "chrome",
        "name": "Google Chrome",
        "filename": "ChromeSetup.exe",
        "url": "",  # Vazio = arquivo local
        "args": ["/silent", "/install"],
        "is_express": True,
        "description": "Navegador web rápido e seguro do Google"
    },
    {
        "id": "adobe_reader",
        "name": "Adobe Acrobat Reader DC",
        "filename": "AcroRdrDC.exe",
        "url": "",
        "args": ["/sAll", "/rs", "/msi", "EULA_ACCEPT=YES"],
        "is_express": True,
        "description": "Leitor de PDF padrão da indústria"
    },
    {
        "id": "7zip",
        "name": "7-Zip",
        "filename": "7z_installer.exe",
        "url": "",
        "args": ["/S"],
        "is_express": True,
        "description": "Compactador de arquivos open-source"
    },
    {
        "id": "winrar",
        "name": "WinRAR",
        "filename": "winrar.exe",
        "url": "",
        "args": ["/S"],
        "is_express": False,
        "description": "Compactador de arquivos com suporte a RAR"
    },
    {
        "id": "nodejs",
        "name": "Node.js LTS",
        "filename": "node.msi",
        "url": "",
        "args": ["/qn"],
        "is_express": False,
        "description": "Runtime JavaScript para desenvolvimento"
    },
]

# ══════════════════════════════════════════════════════════════════════════════
# DETECÇÃO INTELIGENTE DE ARGUMENTOS SILENCIOSOS
# ══════════════════════════════════════════════════════════════════════════════

# Switches básicos por extensão
EXTENSION_SWITCHES = {
    ".exe": "/S",
    ".msi": "/qn /norestart",
}

# Detecção avançada por padrões no nome do arquivo
# Ordem importa: padrões mais específicos primeiro
INSTALLER_PATTERNS = [
    # Adobe
    (["acrobat", "adobe", "reader", "acrordr"], "/sAll /rs /msi EULA_ACCEPT=YES"),
    # Google Chrome
    (["chrome", "chromeset"], "/silent /install"),
    # Firefox
    (["firefox"], "-ms"),
    # 7-Zip (NSIS)
    (["7z", "7zip", "7-zip"], "/S"),
    # WinRAR (NSIS)  
    (["winrar", "rar"], "/S"),
    # VLC
    (["vlc"], "/S /L=1046"),
    # Notepad++
    (["notepad++", "npp"], "/S"),
    # VS Code
    (["vscode", "code"], "/VERYSILENT /NORESTART /MERGETASKS=!runcode"),
    # Git
    (["git-"], "/VERYSILENT /NORESTART"),
    # Node.js
    (["node"], "/qn"),
    # Python
    (["python"], "/quiet InstallAllUsers=1 PrependPath=1"),
    # Java/JDK/JRE
    (["jdk", "jre", "java"], "/s"),
    # .NET Framework
    (["dotnet", "ndp", "netfx"], "/q /norestart"),
    # Zoom
    (["zoom"], "/silent /install"),
    # Teams
    (["teams"], "-s"),
    # Slack
    (["slack"], "-s"),
    # Discord
    (["discord"], "-s"),
    # AnyDesk
    (["anydesk"], "--install"),
    # TeamViewer
    (["teamviewer"], "/S"),
    # PuTTY
    (["putty"], "/VERYSILENT"),
    # WinSCP
    (["winscp"], "/VERYSILENT /NORESTART"),
    # FileZilla
    (["filezilla"], "/S"),
    # Postman
    (["postman"], "/S"),
    # GIMP
    (["gimp"], "/VERYSILENT /NORESTART"),
    # LibreOffice
    (["libreoffice"], "/qn"),
    # Foxit Reader
    (["foxit"], "/VERYSILENT /NORESTART"),
    # Skype
    (["skype"], "/VERYSILENT"),
    # Spotify
    (["spotify"], "/silent"),
    # Inno Setup genérico
    (["setup"], "/VERYSILENT /SUPPRESSMSGBOXES /NORESTART"),
]


def detect_installer_args(filepath_or_filename: str) -> str:
    """
    Detecta automaticamente os argumentos silenciosos baseado no nome do arquivo.
    
    Args:
        filepath_or_filename: Caminho completo ou nome do arquivo
        
    Returns:
        String com os argumentos sugeridos
    """
    filename = os.path.basename(filepath_or_filename).lower()
    _, extension = os.path.splitext(filename)
    
    # Primeiro, tenta detectar pelo padrão do nome
    for patterns, args in INSTALLER_PATTERNS:
        for pattern in patterns:
            if pattern in filename:
                return args
    
    # Se não encontrou padrão específico, usa baseado na extensão
    if extension == ".msi":
        return "/qn /norestart"
    elif extension == ".exe":
        # Tenta adivinhar o tipo de instalador
        if "setup" in filename:
            return "/VERYSILENT /SUPPRESSMSGBOXES /NORESTART"  # Provável Inno Setup
        else:
            return "/S"  # NSIS padrão
    
    return "/S"  # Fallback


class CatalogManager:
    """Gerencia o catálogo de software com persistência em JSON"""
    
    CATALOG_FILE = "software_catalog.json"
    
    def __init__(self):
        self.catalog: List[Dict] = []
        self.load()
    
    def get_catalog_path(self) -> str:
        return os.path.join(get_app_data_path(), self.CATALOG_FILE)
    
    def load(self):
        catalog_path = self.get_catalog_path()
        
        if os.path.exists(catalog_path):
            try:
                with open(catalog_path, 'r', encoding='utf-8') as f:
                    self.catalog = json.load(f)
                # Garante que todos os itens têm o campo 'url'
                for item in self.catalog:
                    if 'url' not in item:
                        item['url'] = ""
                return
            except (json.JSONDecodeError, IOError):
                pass
        
        self.catalog = [item.copy() for item in DEFAULT_SOFTWARE_CATALOG]
        self.save()
    
    def save(self):
        catalog_path = self.get_catalog_path()
        try:
            with open(catalog_path, 'w', encoding='utf-8') as f:
                json.dump(self.catalog, f, indent=2, ensure_ascii=False)
        except IOError as e:
            print(f"Erro ao salvar catálogo: {e}")
    
    def add_software(self, name: str, filename: str, args: List[str], 
                     is_express: bool, description: str = "", url: str = "") -> Dict:
        software_id = str(uuid.uuid4())[:8]
        
        new_software = {
            "id": software_id,
            "name": name,
            "filename": filename,
            "url": url,
            "args": args,
            "is_express": is_express,
            "description": description
        }
        
        self.catalog.append(new_software)
        self.save()
        return new_software
    
    def remove_software(self, software_id: str) -> bool:
        for i, software in enumerate(self.catalog):
            if software["id"] == software_id:
                # Remove o arquivo local se existir e não for da nuvem
                if not software.get("url"):
                    installer_path = os.path.join(get_installers_path(), software["filename"])
                    if os.path.exists(installer_path):
                        try:
                            os.remove(installer_path)
                        except OSError:
                            pass
                
                self.catalog.pop(i)
                self.save()
                return True
        return False
    
    def update_software(self, software_id: str, **kwargs) -> bool:
        for software in self.catalog:
            if software["id"] == software_id:
                software.update(kwargs)
                self.save()
                return True
        return False
    
    def get_software(self, software_id: str) -> Optional[Dict]:
        for software in self.catalog:
            if software["id"] == software_id:
                return software
        return None


catalog_manager = CatalogManager()


# ══════════════════════════════════════════════════════════════════════════════
# SMART RUNNER - LÓGICA DE INSTALAÇÃO INTELIGENTE
# ══════════════════════════════════════════════════════════════════════════════

class InstallResult:
    """Classe para representar o resultado de uma instalação"""
    def __init__(self, success: bool, software_name: str, message: str, return_code: int = 0):
        self.success = success
        self.software_name = software_name
        self.message = message
        self.return_code = return_code


def detect_installer_type(filepath: str) -> str:
    """Wrapper para compatibilidade - usa a nova função de detecção"""
    return detect_installer_args(filepath)


def run_installer(filepath: str, args: List[str], software_name: str) -> InstallResult:
    """
    Executa um instalador de forma inteligente, detectando automaticamente
    se é um arquivo .msi ou .exe e montando o comando apropriado.
    """
    if not os.path.exists(filepath):
        return InstallResult(
            success=False,
            software_name=software_name,
            message=f"Arquivo não encontrado: {filepath}",
            return_code=-1
        )
    
    _, extension = os.path.splitext(filepath.lower())
    
    try:
        if extension == ".msi":
            command = ["msiexec", "/i", filepath] + args
        elif extension == ".exe":
            command = [filepath] + args
        else:
            return InstallResult(
                success=False,
                software_name=software_name,
                message=f"Extensão não suportada: {extension}",
                return_code=-1
            )
        
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=600,
            creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
        )
        
        if result.returncode in [0, 3010]:
            msg = "Instalação concluída com sucesso!"
            if result.returncode == 3010:
                msg += " (Reinicialização necessária)"
            return InstallResult(
                success=True,
                software_name=software_name,
                message=msg,
                return_code=result.returncode
            )
        else:
            return InstallResult(
                success=False,
                software_name=software_name,
                message=f"Código de retorno: {result.returncode}",
                return_code=result.returncode
            )
            
    except subprocess.TimeoutExpired:
        return InstallResult(
            success=False,
            software_name=software_name,
            message="Timeout: instalação demorou mais de 10 minutos",
            return_code=-2
        )
    except Exception as e:
        return InstallResult(
            success=False,
            software_name=software_name,
            message=f"Erro inesperado: {str(e)}",
            return_code=-3
        )


# ══════════════════════════════════════════════════════════════════════════════
# INTERFACE GRÁFICA - CUSTOMTKINTER
# ══════════════════════════════════════════════════════════════════════════════

class AutoSetupApp(ctk.CTk):
    """Aplicação principal do AutoSetup Empresarial"""
    
    COLORS = {
        "bg_dark": "#0a0a0f",
        "bg_card": "#12121a",
        "bg_hover": "#1a1a25",
        "accent": "#6366f1",
        "accent_hover": "#818cf8",
        "success": "#22c55e",
        "error": "#ef4444",
        "warning": "#f59e0b",
        "text": "#f8fafc",
        "text_muted": "#94a3b8",
        "border": "#1e293b",
        "danger": "#dc2626",
        "danger_hover": "#b91c1c",
        "cloud": "#0ea5e9",
        "cloud_hover": "#0284c7"
    }
    
    def __init__(self):
        super().__init__()
        
        self.title("AutoSetup Empresarial v1.0")
        self.geometry("900x700")
        self.minsize(850, 600)
        
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        self.configure(fg_color=self.COLORS["bg_dark"])
        
        self.selected_software: Dict[str, ctk.BooleanVar] = {}
        self.checkboxes: Dict[str, ctk.CTkCheckBox] = {}
        self.is_installing = False
        
        self.main_container = ctk.CTkFrame(self, fg_color="transparent")
        self.main_container.pack(fill="both", expand=True, padx=20, pady=20)
        
        self.refresh_software_vars()
        self.show_home_screen()
    
    def refresh_software_vars(self):
        self.selected_software.clear()
        for software in catalog_manager.catalog:
            self.selected_software[software["id"]] = ctk.BooleanVar(value=software["is_express"])
    
    def clear_container(self):
        for widget in self.main_container.winfo_children():
            widget.destroy()
    
    # ═══════════════════════════════════════════════════════════════════════
    # TELA 1: HOME
    # ═══════════════════════════════════════════════════════════════════════
    
    def show_home_screen(self):
        self.clear_container()
        self.refresh_software_vars()
        
        # Botão de ajuda no canto superior direito
        help_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        help_frame.pack(fill="x", anchor="ne")
        
        help_btn = ctk.CTkButton(
            help_frame,
            text="?",
            font=ctk.CTkFont(size=18, weight="bold"),
            width=40,
            height=40,
            corner_radius=20,
            fg_color=self.COLORS["bg_card"],
            hover_color=self.COLORS["accent"],
            border_width=2,
            border_color=self.COLORS["border"],
            command=self.show_help_screen
        )
        help_btn.pack(side="right", padx=5, pady=5)
        
        center_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        center_frame.place(relx=0.5, rely=0.5, anchor="center")
        
        logo_label = ctk.CTkLabel(center_frame, text="⚙️", font=ctk.CTkFont(size=72))
        logo_label.pack(pady=(0, 10))
        
        title_label = ctk.CTkLabel(
            center_frame,
            text="AutoSetup Empresarial",
            font=ctk.CTkFont(family="Segoe UI", size=36, weight="bold"),
            text_color=self.COLORS["text"]
        )
        title_label.pack(pady=(0, 5))
        
        version_label = ctk.CTkLabel(
            center_frame,
            text="v1.0 • Assistente de Pós-Formatação",
            font=ctk.CTkFont(size=14),
            text_color=self.COLORS["text_muted"]
        )
        version_label.pack(pady=(0, 40))
        
        buttons_frame = ctk.CTkFrame(center_frame, fg_color="transparent")
        buttons_frame.pack()
        
        express_count = sum(1 for s in catalog_manager.catalog if s['is_express'])
        express_btn = ctk.CTkButton(
            buttons_frame,
            text="⚡  Instalação Expressa",
            font=ctk.CTkFont(size=16, weight="bold"),
            width=280,
            height=56,
            corner_radius=12,
            fg_color=self.COLORS["accent"],
            hover_color=self.COLORS["accent_hover"],
            command=self.start_express_install
        )
        express_btn.pack(pady=(0, 15))
        
        express_desc = ctk.CTkLabel(
            buttons_frame,
            text=f"Instala {express_count} programas essenciais automaticamente",
            font=ctk.CTkFont(size=12),
            text_color=self.COLORS["text_muted"]
        )
        express_desc.pack(pady=(0, 25))
        
        custom_btn = ctk.CTkButton(
            buttons_frame,
            text="🎯  Instalação Personalizada",
            font=ctk.CTkFont(size=16, weight="bold"),
            width=280,
            height=56,
            corner_radius=12,
            fg_color=self.COLORS["bg_card"],
            hover_color=self.COLORS["bg_hover"],
            border_width=2,
            border_color=self.COLORS["border"],
            command=self.show_selection_screen
        )
        custom_btn.pack(pady=(0, 15))
        
        custom_desc = ctk.CTkLabel(
            buttons_frame,
            text="Escolha exatamente quais programas instalar",
            font=ctk.CTkFont(size=12),
            text_color=self.COLORS["text_muted"]
        )
        custom_desc.pack(pady=(0, 30))
        
        separator = ctk.CTkFrame(buttons_frame, fg_color=self.COLORS["border"], height=1, width=200)
        separator.pack(pady=(0, 30))
        
        manage_btn = ctk.CTkButton(
            buttons_frame,
            text="📦  Gerenciar Instaladores",
            font=ctk.CTkFont(size=14, weight="bold"),
            width=220,
            height=44,
            corner_radius=10,
            fg_color="transparent",
            hover_color=self.COLORS["bg_hover"],
            border_width=1,
            border_color=self.COLORS["border"],
            text_color=self.COLORS["text_muted"],
            command=self.show_manage_screen
        )
        manage_btn.pack()
        
        footer_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        footer_frame.pack(side="bottom", fill="x", pady=(0, 10))
        
        # Dica
        tip_label = ctk.CTkLabel(
            footer_frame,
            text="💡 Dica: Use 'Gerenciar Instaladores' para adicionar programas locais ou da nuvem",
            font=ctk.CTkFont(size=11),
            text_color=self.COLORS["text_muted"]
        )
        tip_label.pack(pady=(0, 15))
        
        # Separador
        separator = ctk.CTkFrame(footer_frame, fg_color=self.COLORS["border"], height=1, width=300)
        separator.pack(pady=(0, 10))
        
        # Desenvolvido por ELSE SYSTEMS
        dev_frame = ctk.CTkFrame(footer_frame, fg_color="transparent")
        dev_frame.pack()
        
        # Ícone de código </> em verde
        code_icon = ctk.CTkLabel(
            dev_frame,
            text="</>",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#22c55e"  # Verde
        )
        code_icon.pack(side="left", padx=(0, 8))
        
        # Texto clicável com sublinhado
        dev_label = ctk.CTkLabel(
            dev_frame,
            text="Desenvolvido por ELSE SYSTEMS LTDA",
            font=ctk.CTkFont(size=12, underline=True),
            text_color=self.COLORS["text_muted"],
            cursor="hand2"
        )
        dev_label.pack(side="left")
        
        # Bind para abrir o link ao clicar
        def open_else_website(event=None):
            webbrowser.open("https://elsesystems.com")
        
        dev_label.bind("<Button-1>", open_else_website)
        code_icon.bind("<Button-1>", open_else_website)
        
        # Efeito hover para mudar cor
        def on_enter(event):
            dev_label.configure(text_color="#22c55e")
        
        def on_leave(event):
            dev_label.configure(text_color=self.COLORS["text_muted"])
        
        dev_label.bind("<Enter>", on_enter)
        dev_label.bind("<Leave>", on_leave)
        code_icon.bind("<Enter>", on_enter)
        code_icon.bind("<Leave>", on_leave)
    
    # ═══════════════════════════════════════════════════════════════════════
    # TELA 2: SELEÇÃO DE SOFTWARE
    # ═══════════════════════════════════════════════════════════════════════
    
    def show_selection_screen(self):
        self.clear_container()
        self.refresh_software_vars()
        
        header_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 20))
        
        back_btn = ctk.CTkButton(
            header_frame,
            text="← Voltar",
            font=ctk.CTkFont(size=13),
            width=100,
            height=36,
            corner_radius=8,
            fg_color="transparent",
            hover_color=self.COLORS["bg_hover"],
            text_color=self.COLORS["text_muted"],
            command=self.show_home_screen
        )
        back_btn.pack(side="left")
        
        title_label = ctk.CTkLabel(
            header_frame,
            text="Selecione os Programas",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=self.COLORS["text"]
        )
        title_label.pack(side="left", padx=20)
        
        actions_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        actions_frame.pack(fill="x", pady=(0, 15))
        
        select_all_btn = ctk.CTkButton(
            actions_frame,
            text="Selecionar Todos",
            font=ctk.CTkFont(size=12),
            width=130,
            height=32,
            corner_radius=6,
            fg_color=self.COLORS["bg_card"],
            hover_color=self.COLORS["bg_hover"],
            command=self.select_all
        )
        select_all_btn.pack(side="left", padx=(0, 10))
        
        select_none_btn = ctk.CTkButton(
            actions_frame,
            text="Limpar Seleção",
            font=ctk.CTkFont(size=12),
            width=130,
            height=32,
            corner_radius=6,
            fg_color=self.COLORS["bg_card"],
            hover_color=self.COLORS["bg_hover"],
            command=self.select_none
        )
        select_none_btn.pack(side="left")
        
        self.selection_count_label = ctk.CTkLabel(
            actions_frame,
            text="",
            font=ctk.CTkFont(size=12),
            text_color=self.COLORS["text_muted"]
        )
        self.selection_count_label.pack(side="right")
        self.update_selection_count()
        
        scroll_frame = ctk.CTkScrollableFrame(
            self.main_container,
            fg_color=self.COLORS["bg_card"],
            corner_radius=12,
            border_width=1,
            border_color=self.COLORS["border"]
        )
        scroll_frame.pack(fill="both", expand=True, pady=(0, 20))
        
        self.checkboxes.clear()
        
        if not catalog_manager.catalog:
            empty_label = ctk.CTkLabel(
                scroll_frame,
                text="Nenhum instalador cadastrado.\nClique em 'Gerenciar Instaladores' para adicionar.",
                font=ctk.CTkFont(size=14),
                text_color=self.COLORS["text_muted"]
            )
            empty_label.pack(pady=50)
        else:
            for i, software in enumerate(catalog_manager.catalog):
                item_frame = ctk.CTkFrame(scroll_frame, fg_color="transparent", height=80)
                item_frame.pack(fill="x", padx=15, pady=8)
                item_frame.pack_propagate(False)
                
                checkbox = ctk.CTkCheckBox(
                    item_frame,
                    text="",
                    variable=self.selected_software[software["id"]],
                    width=24,
                    height=24,
                    checkbox_width=22,
                    checkbox_height=22,
                    corner_radius=6,
                    border_width=2,
                    fg_color=self.COLORS["accent"],
                    hover_color=self.COLORS["accent_hover"],
                    command=self.update_selection_count
                )
                checkbox.pack(side="left", padx=(0, 15))
                self.checkboxes[software["id"]] = checkbox
                
                info_frame = ctk.CTkFrame(item_frame, fg_color="transparent")
                info_frame.pack(side="left", fill="both", expand=True)
                
                name_label = ctk.CTkLabel(
                    info_frame,
                    text=software["name"],
                    font=ctk.CTkFont(size=15, weight="bold"),
                    text_color=self.COLORS["text"],
                    anchor="w"
                )
                name_label.pack(anchor="w")
                
                # Fonte do arquivo
                source_text = "☁️ Nuvem" if software.get("url") else "💾 Local"
                source_label = ctk.CTkLabel(
                    info_frame,
                    text=f"{source_text}  •  {software.get('description', '')}",
                    font=ctk.CTkFont(size=11),
                    text_color=self.COLORS["text_muted"],
                    anchor="w"
                )
                source_label.pack(anchor="w")
                
                # Badges
                badges_frame = ctk.CTkFrame(item_frame, fg_color="transparent")
                badges_frame.pack(side="right", padx=10)
                
                if software.get("url"):
                    cloud_badge = ctk.CTkLabel(
                        badges_frame,
                        text="☁️ NUVEM",
                        font=ctk.CTkFont(size=9, weight="bold"),
                        text_color=self.COLORS["cloud"],
                        fg_color=self.COLORS["bg_hover"],
                        corner_radius=4,
                        padx=6,
                        pady=2
                    )
                    cloud_badge.pack(pady=(0, 4))
                
                if software["is_express"]:
                    badge = ctk.CTkLabel(
                        badges_frame,
                        text="EXPRESS",
                        font=ctk.CTkFont(size=9, weight="bold"),
                        text_color=self.COLORS["accent"],
                        fg_color=self.COLORS["bg_hover"],
                        corner_radius=4,
                        padx=6,
                        pady=2
                    )
                    badge.pack()
                
                if i < len(catalog_manager.catalog) - 1:
                    separator = ctk.CTkFrame(scroll_frame, fg_color=self.COLORS["border"], height=1)
                    separator.pack(fill="x", padx=15)
        
        install_btn = ctk.CTkButton(
            self.main_container,
            text="🚀  Instalar Selecionados",
            font=ctk.CTkFont(size=16, weight="bold"),
            height=52,
            corner_radius=10,
            fg_color=self.COLORS["accent"],
            hover_color=self.COLORS["accent_hover"],
            command=self.start_custom_install
        )
        install_btn.pack(fill="x")
    
    def select_all(self):
        for var in self.selected_software.values():
            var.set(True)
        self.update_selection_count()
    
    def select_none(self):
        for var in self.selected_software.values():
            var.set(False)
        self.update_selection_count()
    
    def update_selection_count(self):
        count = sum(1 for var in self.selected_software.values() if var.get())
        total = len(catalog_manager.catalog)
        if hasattr(self, 'selection_count_label'):
            self.selection_count_label.configure(text=f"{count} de {total} selecionados")
    
    # ═══════════════════════════════════════════════════════════════════════
    # TELA 3: GERENCIAR INSTALADORES
    # ═══════════════════════════════════════════════════════════════════════
    
    def show_manage_screen(self):
        self.clear_container()
        
        header_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 15))
        
        back_btn = ctk.CTkButton(
            header_frame,
            text="← Voltar",
            font=ctk.CTkFont(size=13),
            width=100,
            height=36,
            corner_radius=8,
            fg_color="transparent",
            hover_color=self.COLORS["bg_hover"],
            text_color=self.COLORS["text_muted"],
            command=self.show_home_screen
        )
        back_btn.pack(side="left")
        
        title_label = ctk.CTkLabel(
            header_frame,
            text="📦  Gerenciar Instaladores",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=self.COLORS["text"]
        )
        title_label.pack(side="left", padx=20)
        
        add_btn = ctk.CTkButton(
            header_frame,
            text="➕  Adicionar Novo",
            font=ctk.CTkFont(size=13, weight="bold"),
            width=150,
            height=36,
            corner_radius=8,
            fg_color=self.COLORS["success"],
            hover_color="#16a34a",
            command=self.show_add_installer_dialog
        )
        add_btn.pack(side="right")
        
        # Info da pasta
        info_frame = ctk.CTkFrame(self.main_container, fg_color=self.COLORS["bg_card"], corner_radius=8)
        info_frame.pack(fill="x", pady=(0, 10))
        
        info_label = ctk.CTkLabel(
            info_frame,
            text=f"📁 Pasta local: {get_installers_path()}",
            font=ctk.CTkFont(size=11),
            text_color=self.COLORS["text_muted"]
        )
        info_label.pack(pady=6, padx=15, anchor="w")
        
        cloud_info = ctk.CTkLabel(
            info_frame,
            text="☁️ Instaladores da nuvem são baixados automaticamente durante a instalação",
            font=ctk.CTkFont(size=11),
            text_color=self.COLORS["cloud"]
        )
        cloud_info.pack(pady=(0, 6), padx=15, anchor="w")
        
        # Frame scrollável para lista
        self.manage_scroll_frame = ctk.CTkScrollableFrame(
            self.main_container,
            fg_color=self.COLORS["bg_card"],
            corner_radius=12,
            border_width=1,
            border_color=self.COLORS["border"]
        )
        self.manage_scroll_frame.pack(fill="both", expand=True)
        
        self.render_installer_list()
    
    def render_installer_list(self):
        for widget in self.manage_scroll_frame.winfo_children():
            widget.destroy()
        
        if not catalog_manager.catalog:
            empty_frame = ctk.CTkFrame(self.manage_scroll_frame, fg_color="transparent")
            empty_frame.pack(fill="both", expand=True, pady=30)
            
            empty_icon = ctk.CTkLabel(empty_frame, text="📭", font=ctk.CTkFont(size=48))
            empty_icon.pack()
            
            empty_label = ctk.CTkLabel(
                empty_frame,
                text="Nenhum instalador cadastrado",
                font=ctk.CTkFont(size=16, weight="bold"),
                text_color=self.COLORS["text"]
            )
            empty_label.pack(pady=(10, 5))
            
            # Instruções detalhadas
            instructions_frame = ctk.CTkFrame(empty_frame, fg_color=self.COLORS["bg_card"], corner_radius=10)
            instructions_frame.pack(pady=15, padx=20, fill="x")
            
            step1 = ctk.CTkLabel(
                instructions_frame,
                text="📁 Passo 1: Coloque os instaladores (.exe/.msi) na pasta 'installers'",
                font=ctk.CTkFont(size=12),
                text_color=self.COLORS["text_muted"],
                anchor="w"
            )
            step1.pack(pady=(15, 5), padx=15, anchor="w")
            
            path_hint = ctk.CTkLabel(
                instructions_frame,
                text="(mesma pasta onde está este programa)",
                font=ctk.CTkFont(size=11),
                text_color=self.COLORS["accent"],
                anchor="w"
            )
            path_hint.pack(pady=(0, 5), padx=25, anchor="w")
            
            path_label = ctk.CTkLabel(
                instructions_frame,
                text=f"Caminho atual: {get_installers_path()}",
                font=ctk.CTkFont(family="Consolas", size=10),
                text_color=self.COLORS["text_muted"],
                anchor="w"
            )
            path_label.pack(pady=(0, 10), padx=25, anchor="w")
            
            step2 = ctk.CTkLabel(
                instructions_frame,
                text="➕ Passo 2: Clique em 'Adicionar Novo' para cadastrar cada programa",
                font=ctk.CTkFont(size=12),
                text_color=self.COLORS["text_muted"],
                anchor="w"
            )
            step2.pack(pady=(5, 5), padx=15, anchor="w")
            
            step3 = ctk.CTkLabel(
                instructions_frame,
                text="☁️ Dica: Você também pode usar URLs para baixar da nuvem!",
                font=ctk.CTkFont(size=12),
                text_color=self.COLORS["cloud"],
                anchor="w"
            )
            step3.pack(pady=(5, 15), padx=15, anchor="w")
            
            # Botão para abrir a pasta
            open_folder_btn = ctk.CTkButton(
                empty_frame,
                text="📂  Abrir Pasta de Instaladores",
                font=ctk.CTkFont(size=13, weight="bold"),
                width=220,
                height=40,
                corner_radius=8,
                fg_color=self.COLORS["accent"],
                hover_color=self.COLORS["accent_hover"],
                command=self.open_installers_folder
            )
            open_folder_btn.pack(pady=(5, 10))
            
            empty_hint = ctk.CTkLabel(
                empty_frame,
                text="Após adicionar os arquivos, clique em '➕ Adicionar Novo'",
                font=ctk.CTkFont(size=13),
                text_color=self.COLORS["text_muted"]
            )
            empty_hint.pack()
            return
        
        for i, software in enumerate(catalog_manager.catalog):
            item_frame = ctk.CTkFrame(self.manage_scroll_frame, fg_color="transparent", height=95)
            item_frame.pack(fill="x", padx=15, pady=10)
            item_frame.pack_propagate(False)
            
            # Ícone baseado na fonte
            is_cloud = bool(software.get("url"))
            icon_text = "☁️" if is_cloud else ("📦" if software["filename"].endswith(".exe") else "📀")
            icon_label = ctk.CTkLabel(item_frame, text=icon_text, font=ctk.CTkFont(size=28))
            icon_label.pack(side="left", padx=(0, 15))
            
            info_frame = ctk.CTkFrame(item_frame, fg_color="transparent")
            info_frame.pack(side="left", fill="both", expand=True)
            
            name_label = ctk.CTkLabel(
                info_frame,
                text=software["name"],
                font=ctk.CTkFont(size=15, weight="bold"),
                text_color=self.COLORS["text"],
                anchor="w"
            )
            name_label.pack(anchor="w")
            
            # Fonte (URL ou arquivo)
            if is_cloud:
                url_display = software["url"][:50] + "..." if len(software["url"]) > 50 else software["url"]
                source_text = f"🔗 {url_display}"
            else:
                source_text = f"📄 {software['filename']}"
            
            source_label = ctk.CTkLabel(
                info_frame,
                text=source_text,
                font=ctk.CTkFont(size=11),
                text_color=self.COLORS["text_muted"],
                anchor="w"
            )
            source_label.pack(anchor="w")
            
            args_label = ctk.CTkLabel(
                info_frame,
                text=f"Args: {' '.join(software['args'])}",
                font=ctk.CTkFont(size=11),
                text_color=self.COLORS["text_muted"],
                anchor="w"
            )
            args_label.pack(anchor="w")
            
            if software.get("description"):
                desc_label = ctk.CTkLabel(
                    info_frame,
                    text=software["description"],
                    font=ctk.CTkFont(size=10),
                    text_color=self.COLORS["text_muted"],
                    anchor="w"
                )
                desc_label.pack(anchor="w")
            
            # Badges e botões
            actions_frame = ctk.CTkFrame(item_frame, fg_color="transparent")
            actions_frame.pack(side="right", padx=(10, 0))
            
            if is_cloud:
                cloud_badge = ctk.CTkLabel(
                    actions_frame,
                    text="☁️ NUVEM",
                    font=ctk.CTkFont(size=9, weight="bold"),
                    text_color=self.COLORS["cloud"],
                    fg_color=self.COLORS["bg_hover"],
                    corner_radius=4,
                    padx=6,
                    pady=2
                )
                cloud_badge.pack(pady=(0, 4))
            
            if software["is_express"]:
                badge = ctk.CTkLabel(
                    actions_frame,
                    text="EXPRESS",
                    font=ctk.CTkFont(size=9, weight="bold"),
                    text_color=self.COLORS["accent"],
                    fg_color=self.COLORS["bg_hover"],
                    corner_radius=4,
                    padx=6,
                    pady=2
                )
                badge.pack(pady=(0, 4))
            
            # Verifica se arquivo local existe
            if not is_cloud:
                installer_path = os.path.join(get_installers_path(), software["filename"])
                if not os.path.exists(installer_path):
                    missing_badge = ctk.CTkLabel(
                        actions_frame,
                        text="⚠️ ARQUIVO",
                        font=ctk.CTkFont(size=9, weight="bold"),
                        text_color=self.COLORS["warning"],
                        fg_color=self.COLORS["bg_hover"],
                        corner_radius=4,
                        padx=6,
                        pady=2
                    )
                    missing_badge.pack(pady=(0, 4))
            
            # Frame para botões de ação
            btns_frame = ctk.CTkFrame(actions_frame, fg_color="transparent")
            btns_frame.pack()
            
            # Botão editar
            edit_btn = ctk.CTkButton(
                btns_frame,
                text="✏️",
                font=ctk.CTkFont(size=14),
                width=36,
                height=36,
                corner_radius=8,
                fg_color=self.COLORS["bg_hover"],
                hover_color=self.COLORS["accent"],
                command=lambda sid=software["id"]: self.show_edit_installer_dialog(sid)
            )
            edit_btn.pack(side="left", padx=(0, 5))
            
            # Botão remover
            remove_btn = ctk.CTkButton(
                btns_frame,
                text="🗑️",
                font=ctk.CTkFont(size=14),
                width=36,
                height=36,
                corner_radius=8,
                fg_color=self.COLORS["bg_hover"],
                hover_color=self.COLORS["danger"],
                command=lambda sid=software["id"], sname=software["name"]: self.confirm_remove_installer(sid, sname)
            )
            remove_btn.pack(side="left")
            
            if i < len(catalog_manager.catalog) - 1:
                separator = ctk.CTkFrame(self.manage_scroll_frame, fg_color=self.COLORS["border"], height=1)
                separator.pack(fill="x", padx=15)
    
    def confirm_remove_installer(self, software_id: str, software_name: str):
        dialog = ctk.CTkToplevel(self)
        dialog.title("Confirmar Remoção")
        dialog.geometry("450x200")
        dialog.resizable(False, False)
        dialog.transient(self)
        dialog.grab_set()
        
        dialog.update_idletasks()
        x = self.winfo_x() + (self.winfo_width() - 450) // 2
        y = self.winfo_y() + (self.winfo_height() - 200) // 2
        dialog.geometry(f"+{x}+{y}")
        
        dialog.configure(fg_color=self.COLORS["bg_dark"])
        
        icon_label = ctk.CTkLabel(dialog, text="🗑️", font=ctk.CTkFont(size=42))
        icon_label.pack(pady=(25, 10))
        
        msg_label = ctk.CTkLabel(
            dialog,
            text=f"Deseja remover '{software_name}'?",
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color=self.COLORS["text"]
        )
        msg_label.pack()
        
        hint_label = ctk.CTkLabel(
            dialog,
            text="O arquivo local (se existir) também será removido.",
            font=ctk.CTkFont(size=12),
            text_color=self.COLORS["text_muted"]
        )
        hint_label.pack(pady=(5, 20))
        
        btn_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        btn_frame.pack()
        
        cancel_btn = ctk.CTkButton(
            btn_frame,
            text="Cancelar",
            width=120,
            height=38,
            corner_radius=8,
            fg_color=self.COLORS["bg_card"],
            hover_color=self.COLORS["bg_hover"],
            command=dialog.destroy
        )
        cancel_btn.pack(side="left", padx=(0, 10))
        
        def do_remove():
            catalog_manager.remove_software(software_id)
            dialog.destroy()
            self.render_installer_list()
        
        remove_btn = ctk.CTkButton(
            btn_frame,
            text="Remover",
            width=120,
            height=38,
            corner_radius=8,
            fg_color=self.COLORS["danger"],
            hover_color=self.COLORS["danger_hover"],
            command=do_remove
        )
        remove_btn.pack(side="left")
    
    # ═══════════════════════════════════════════════════════════════════════
    # DIÁLOGO: ADICIONAR INSTALADOR (ROLÁVEL)
    # ═══════════════════════════════════════════════════════════════════════
    
    def show_add_installer_dialog(self):
        dialog = ctk.CTkToplevel(self)
        dialog.title("Adicionar Novo Instalador")
        dialog.geometry("600x650")
        dialog.resizable(False, True)
        dialog.minsize(600, 500)
        dialog.transient(self)
        dialog.grab_set()
        
        dialog.update_idletasks()
        x = self.winfo_x() + (self.winfo_width() - 600) // 2
        y = self.winfo_y() + (self.winfo_height() - 650) // 2
        dialog.geometry(f"+{x}+{y}")
        
        dialog.configure(fg_color=self.COLORS["bg_dark"])
        
        # Título
        title_label = ctk.CTkLabel(
            dialog,
            text="➕  Adicionar Novo Instalador",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=self.COLORS["text"]
        )
        title_label.pack(pady=(20, 10))
        
        # Frame ROLÁVEL para o formulário
        form_scroll = ctk.CTkScrollableFrame(
            dialog,
            fg_color="transparent",
            scrollbar_button_color=self.COLORS["bg_hover"],
            scrollbar_button_hover_color=self.COLORS["accent"]
        )
        form_scroll.pack(fill="both", expand=True, padx=25, pady=(0, 10))
        
        # Variáveis do formulário
        source_type = ctk.StringVar(value="local")  # "local" ou "cloud"
        selected_file_path = ctk.StringVar()
        selected_filename = ctk.StringVar()
        
        # ─────────────────────────────────────────────────────
        # SEÇÃO: TIPO DE FONTE
        # ─────────────────────────────────────────────────────
        
        section_source = ctk.CTkLabel(
            form_scroll,
            text="📍 Origem do Instalador",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=self.COLORS["text"]
        )
        section_source.pack(anchor="w", pady=(10, 10))
        
        source_frame = ctk.CTkFrame(form_scroll, fg_color=self.COLORS["bg_card"], corner_radius=10)
        source_frame.pack(fill="x", pady=(0, 15))
        
        def on_source_change():
            is_cloud = source_type.get() == "cloud"
            # Mostra/esconde frames apropriados
            if is_cloud:
                local_frame.pack_forget()
                cloud_frame.pack(fill="x", pady=(0, 15), after=source_frame)
            else:
                cloud_frame.pack_forget()
                local_frame.pack(fill="x", pady=(0, 15), after=source_frame)
        
        local_radio = ctk.CTkRadioButton(
            source_frame,
            text="💾  Arquivo Local",
            variable=source_type,
            value="local",
            font=ctk.CTkFont(size=13),
            fg_color=self.COLORS["accent"],
            command=on_source_change
        )
        local_radio.pack(side="left", padx=20, pady=15)
        
        cloud_radio = ctk.CTkRadioButton(
            source_frame,
            text="☁️  URL da Nuvem",
            variable=source_type,
            value="cloud",
            font=ctk.CTkFont(size=13),
            fg_color=self.COLORS["cloud"],
            command=on_source_change
        )
        cloud_radio.pack(side="left", padx=20, pady=15)
        
        # ─────────────────────────────────────────────────────
        # SEÇÃO: ARQUIVO LOCAL
        # ─────────────────────────────────────────────────────
        
        local_frame = ctk.CTkFrame(form_scroll, fg_color="transparent")
        
        local_file_label = ctk.CTkLabel(
            local_frame,
            text="📂 Selecionar Arquivo *",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=self.COLORS["text"]
        )
        local_file_label.pack(anchor="w", pady=(0, 5))
        
        local_file_frame = ctk.CTkFrame(local_frame, fg_color="transparent")
        local_file_frame.pack(fill="x", pady=(0, 5))
        
        file_entry = ctk.CTkEntry(
            local_file_frame,
            textvariable=selected_filename,
            placeholder_text="Nenhum arquivo selecionado",
            height=40,
            corner_radius=8,
            fg_color=self.COLORS["bg_card"],
            border_color=self.COLORS["border"],
            state="disabled"
        )
        file_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        # Referência para args_entry (declarada depois)
        args_entry_ref = [None]
        
        def browse_file():
            filepath = filedialog.askopenfilename(
                title="Selecione o arquivo instalador",
                filetypes=[
                    ("Instaladores", "*.exe *.msi"),
                    ("Executáveis", "*.exe"),
                    ("MSI", "*.msi"),
                    ("Todos", "*.*")
                ]
            )
            if filepath:
                selected_file_path.set(filepath)
                filename = os.path.basename(filepath)
                selected_filename.set(filename)
                
                suggested = detect_installer_type(filepath)
                if args_entry_ref[0] and not args_entry_ref[0].get():
                    args_entry_ref[0].delete(0, "end")
                    args_entry_ref[0].insert(0, suggested)
        
        browse_btn = ctk.CTkButton(
            local_file_frame,
            text="📂 Localizar",
            font=ctk.CTkFont(size=13),
            width=110,
            height=40,
            corner_radius=8,
            fg_color=self.COLORS["accent"],
            hover_color=self.COLORS["accent_hover"],
            command=browse_file
        )
        browse_btn.pack(side="right")
        
        local_hint = ctk.CTkLabel(
            local_frame,
            text="O arquivo será copiado para a pasta de instaladores",
            font=ctk.CTkFont(size=11),
            text_color=self.COLORS["text_muted"]
        )
        local_hint.pack(anchor="w")
        
        local_frame.pack(fill="x", pady=(0, 15))  # Mostra por padrão
        
        # ─────────────────────────────────────────────────────
        # SEÇÃO: URL DA NUVEM
        # ─────────────────────────────────────────────────────
        
        cloud_frame = ctk.CTkFrame(form_scroll, fg_color="transparent")
        
        cloud_url_label = ctk.CTkLabel(
            cloud_frame,
            text="🔗 URL do Download *",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=self.COLORS["text"]
        )
        cloud_url_label.pack(anchor="w", pady=(0, 5))
        
        url_entry = ctk.CTkEntry(
            cloud_frame,
            placeholder_text="https://exemplo.com/instalador.exe",
            height=40,
            corner_radius=8,
            fg_color=self.COLORS["bg_card"],
            border_color=self.COLORS["border"]
        )
        url_entry.pack(fill="x", pady=(0, 5))
        
        cloud_hint = ctk.CTkLabel(
            cloud_frame,
            text="💡 O arquivo será baixado automaticamente durante a instalação",
            font=ctk.CTkFont(size=11),
            text_color=self.COLORS["cloud"]
        )
        cloud_hint.pack(anchor="w", pady=(0, 10))
        
        cloud_filename_label = ctk.CTkLabel(
            cloud_frame,
            text="📄 Nome do Arquivo (opcional)",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=self.COLORS["text"]
        )
        cloud_filename_label.pack(anchor="w", pady=(0, 5))
        
        cloud_filename_entry = ctk.CTkEntry(
            cloud_frame,
            placeholder_text="instalador.exe (deixe vazio para detectar da URL)",
            height=40,
            corner_radius=8,
            fg_color=self.COLORS["bg_card"],
            border_color=self.COLORS["border"]
        )
        cloud_filename_entry.pack(fill="x")
        
        # Cloud frame escondido inicialmente
        # cloud_frame.pack(fill="x", pady=(0, 15))
        
        # ─────────────────────────────────────────────────────
        # SEÇÃO: INFORMAÇÕES DO PROGRAMA
        # ─────────────────────────────────────────────────────
        
        section_info = ctk.CTkLabel(
            form_scroll,
            text="📝 Informações do Programa",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=self.COLORS["text"]
        )
        section_info.pack(anchor="w", pady=(15, 10))
        
        name_label = ctk.CTkLabel(
            form_scroll,
            text="Nome do Programa *",
            font=ctk.CTkFont(size=13),
            text_color=self.COLORS["text"]
        )
        name_label.pack(anchor="w", pady=(0, 5))
        
        name_entry = ctk.CTkEntry(
            form_scroll,
            placeholder_text="Ex: Google Chrome",
            height=40,
            corner_radius=8,
            fg_color=self.COLORS["bg_card"],
            border_color=self.COLORS["border"]
        )
        name_entry.pack(fill="x", pady=(0, 15))
        
        desc_label = ctk.CTkLabel(
            form_scroll,
            text="Descrição (opcional)",
            font=ctk.CTkFont(size=13),
            text_color=self.COLORS["text"]
        )
        desc_label.pack(anchor="w", pady=(0, 5))
        
        desc_entry = ctk.CTkEntry(
            form_scroll,
            placeholder_text="Ex: Navegador web rápido e seguro",
            height=40,
            corner_radius=8,
            fg_color=self.COLORS["bg_card"],
            border_color=self.COLORS["border"]
        )
        desc_entry.pack(fill="x", pady=(0, 15))
        
        # ─────────────────────────────────────────────────────
        # SEÇÃO: CONFIGURAÇÃO DE INSTALAÇÃO
        # ─────────────────────────────────────────────────────
        
        section_config = ctk.CTkLabel(
            form_scroll,
            text="⚙️ Configuração de Instalação",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=self.COLORS["text"]
        )
        section_config.pack(anchor="w", pady=(15, 10))
        
        args_label = ctk.CTkLabel(
            form_scroll,
            text="Argumentos Silenciosos *",
            font=ctk.CTkFont(size=13),
            text_color=self.COLORS["text"]
        )
        args_label.pack(anchor="w", pady=(0, 5))
        
        args_entry = ctk.CTkEntry(
            form_scroll,
            placeholder_text="Ex: /S ou /qn ou /VERYSILENT",
            height=40,
            corner_radius=8,
            fg_color=self.COLORS["bg_card"],
            border_color=self.COLORS["border"]
        )
        args_entry.pack(fill="x", pady=(0, 5))
        args_entry_ref[0] = args_entry  # Atualiza referência
        
        args_hint = ctk.CTkLabel(
            form_scroll,
            text="💡 Switches comuns: /S (NSIS), /qn (MSI), /VERYSILENT (Inno Setup)",
            font=ctk.CTkFont(size=11),
            text_color=self.COLORS["text_muted"]
        )
        args_hint.pack(anchor="w", pady=(0, 15))
        
        express_var = ctk.BooleanVar(value=False)
        express_check = ctk.CTkCheckBox(
            form_scroll,
            text="⚡ Incluir na Instalação Expressa",
            variable=express_var,
            font=ctk.CTkFont(size=13),
            fg_color=self.COLORS["accent"],
            hover_color=self.COLORS["accent_hover"]
        )
        express_check.pack(anchor="w", pady=(0, 20))
        
        # Mensagem de erro
        error_label = ctk.CTkLabel(
            form_scroll,
            text="",
            font=ctk.CTkFont(size=12),
            text_color=self.COLORS["error"]
        )
        error_label.pack(pady=(0, 10))
        
        # ─────────────────────────────────────────────────────
        # BOTÕES
        # ─────────────────────────────────────────────────────
        
        btn_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        btn_frame.pack(pady=(0, 20))
        
        cancel_btn = ctk.CTkButton(
            btn_frame,
            text="Cancelar",
            width=130,
            height=42,
            corner_radius=8,
            fg_color=self.COLORS["bg_card"],
            hover_color=self.COLORS["bg_hover"],
            command=dialog.destroy
        )
        cancel_btn.pack(side="left", padx=(0, 15))
        
        def save_installer():
            # Validação
            name = name_entry.get().strip()
            description = desc_entry.get().strip()
            args_text = args_entry.get().strip()
            is_express = express_var.get()
            is_cloud = source_type.get() == "cloud"
            
            if not name:
                error_label.configure(text="⚠️ Digite o nome do programa")
                return
            
            if not args_text:
                error_label.configure(text="⚠️ Digite os argumentos silenciosos")
                return
            
            if is_cloud:
                # Modo nuvem
                url = url_entry.get().strip()
                if not url:
                    error_label.configure(text="⚠️ Digite a URL do instalador")
                    return
                
                if not url.startswith(('http://', 'https://')):
                    error_label.configure(text="⚠️ URL deve começar com http:// ou https://")
                    return
                
                # Nome do arquivo
                filename = cloud_filename_entry.get().strip()
                if not filename:
                    filename = extract_filename_from_url(url)
                
                # Adiciona ao catálogo
                args = args_text.split()
                catalog_manager.add_software(
                    name=name,
                    filename=filename,
                    args=args,
                    is_express=is_express,
                    description=description,
                    url=url
                )
            else:
                # Modo local
                filepath = selected_file_path.get()
                if not filepath:
                    error_label.configure(text="⚠️ Selecione o arquivo instalador")
                    return
                
                # Copia o arquivo
                filename = os.path.basename(filepath)
                dest_path = os.path.join(get_installers_path(), filename)
                
                try:
                    if filepath != dest_path:
                        shutil.copy2(filepath, dest_path)
                except Exception as e:
                    error_label.configure(text=f"⚠️ Erro ao copiar: {e}")
                    return
                
                # Adiciona ao catálogo
                args = args_text.split()
                catalog_manager.add_software(
                    name=name,
                    filename=filename,
                    args=args,
                    is_express=is_express,
                    description=description,
                    url=""
                )
            
            dialog.destroy()
            self.render_installer_list()
        
        save_btn = ctk.CTkButton(
            btn_frame,
            text="💾  Salvar",
            font=ctk.CTkFont(size=14, weight="bold"),
            width=130,
            height=42,
            corner_radius=8,
            fg_color=self.COLORS["success"],
            hover_color="#16a34a",
            command=save_installer
        )
        save_btn.pack(side="left")
    
    # ═══════════════════════════════════════════════════════════════════════
    # DIÁLOGO: EDITAR INSTALADOR
    # ═══════════════════════════════════════════════════════════════════════
    
    def show_edit_installer_dialog(self, software_id: str):
        """Exibe o diálogo para editar um instalador existente"""
        software = catalog_manager.get_software(software_id)
        if not software:
            return
        
        dialog = ctk.CTkToplevel(self)
        dialog.title(f"Editar: {software['name']}")
        dialog.geometry("600x700")
        dialog.resizable(False, True)
        dialog.minsize(600, 550)
        dialog.transient(self)
        dialog.grab_set()
        
        dialog.update_idletasks()
        x = self.winfo_x() + (self.winfo_width() - 600) // 2
        y = self.winfo_y() + (self.winfo_height() - 700) // 2
        dialog.geometry(f"+{x}+{y}")
        
        dialog.configure(fg_color=self.COLORS["bg_dark"])
        
        # Título
        title_label = ctk.CTkLabel(
            dialog,
            text=f"✏️  Editar Instalador",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=self.COLORS["text"]
        )
        title_label.pack(pady=(20, 10))
        
        # Frame ROLÁVEL para o formulário
        form_scroll = ctk.CTkScrollableFrame(
            dialog,
            fg_color="transparent",
            scrollbar_button_color=self.COLORS["bg_hover"],
            scrollbar_button_hover_color=self.COLORS["accent"]
        )
        form_scroll.pack(fill="both", expand=True, padx=25, pady=(0, 10))
        
        # Variáveis do formulário (preenchidas com dados existentes)
        is_cloud = bool(software.get("url"))
        source_type = ctk.StringVar(value="cloud" if is_cloud else "local")
        selected_file_path = ctk.StringVar()
        selected_filename = ctk.StringVar(value=software["filename"])
        
        # ─────────────────────────────────────────────────────
        # SEÇÃO: TIPO DE FONTE
        # ─────────────────────────────────────────────────────
        
        section_source = ctk.CTkLabel(
            form_scroll,
            text="📍 Origem do Instalador",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=self.COLORS["text"]
        )
        section_source.pack(anchor="w", pady=(10, 10))
        
        source_frame = ctk.CTkFrame(form_scroll, fg_color=self.COLORS["bg_card"], corner_radius=10)
        source_frame.pack(fill="x", pady=(0, 15))
        
        def on_source_change():
            is_cloud_now = source_type.get() == "cloud"
            if is_cloud_now:
                local_frame.pack_forget()
                cloud_frame.pack(fill="x", pady=(0, 15), after=source_frame)
            else:
                cloud_frame.pack_forget()
                local_frame.pack(fill="x", pady=(0, 15), after=source_frame)
        
        local_radio = ctk.CTkRadioButton(
            source_frame,
            text="💾  Arquivo Local",
            variable=source_type,
            value="local",
            font=ctk.CTkFont(size=13),
            fg_color=self.COLORS["accent"],
            command=on_source_change
        )
        local_radio.pack(side="left", padx=20, pady=15)
        
        cloud_radio = ctk.CTkRadioButton(
            source_frame,
            text="☁️  URL da Nuvem",
            variable=source_type,
            value="cloud",
            font=ctk.CTkFont(size=13),
            fg_color=self.COLORS["cloud"],
            command=on_source_change
        )
        cloud_radio.pack(side="left", padx=20, pady=15)
        
        # ─────────────────────────────────────────────────────
        # SEÇÃO: ARQUIVO LOCAL
        # ─────────────────────────────────────────────────────
        
        local_frame = ctk.CTkFrame(form_scroll, fg_color="transparent")
        
        local_file_label = ctk.CTkLabel(
            local_frame,
            text="📂 Arquivo Atual / Selecionar Novo",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=self.COLORS["text"]
        )
        local_file_label.pack(anchor="w", pady=(0, 5))
        
        local_file_frame = ctk.CTkFrame(local_frame, fg_color="transparent")
        local_file_frame.pack(fill="x", pady=(0, 5))
        
        file_entry = ctk.CTkEntry(
            local_file_frame,
            textvariable=selected_filename,
            height=40,
            corner_radius=8,
            fg_color=self.COLORS["bg_card"],
            border_color=self.COLORS["border"],
            state="disabled"
        )
        file_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        args_entry_ref = [None]
        
        def browse_file():
            filepath = filedialog.askopenfilename(
                title="Selecione o arquivo instalador",
                filetypes=[
                    ("Instaladores", "*.exe *.msi"),
                    ("Executáveis", "*.exe"),
                    ("MSI", "*.msi"),
                    ("Todos", "*.*")
                ]
            )
            if filepath:
                selected_file_path.set(filepath)
                filename = os.path.basename(filepath)
                selected_filename.set(filename)
                
                # Auto-detecta argumentos
                suggested = detect_installer_args(filepath)
                if args_entry_ref[0]:
                    args_entry_ref[0].delete(0, "end")
                    args_entry_ref[0].insert(0, suggested)
        
        browse_btn = ctk.CTkButton(
            local_file_frame,
            text="📂 Alterar",
            font=ctk.CTkFont(size=13),
            width=110,
            height=40,
            corner_radius=8,
            fg_color=self.COLORS["accent"],
            hover_color=self.COLORS["accent_hover"],
            command=browse_file
        )
        browse_btn.pack(side="right")
        
        local_hint = ctk.CTkLabel(
            local_frame,
            text="Selecione um novo arquivo para substituir o atual",
            font=ctk.CTkFont(size=11),
            text_color=self.COLORS["text_muted"]
        )
        local_hint.pack(anchor="w")
        
        # ─────────────────────────────────────────────────────
        # SEÇÃO: URL DA NUVEM
        # ─────────────────────────────────────────────────────
        
        cloud_frame = ctk.CTkFrame(form_scroll, fg_color="transparent")
        
        cloud_url_label = ctk.CTkLabel(
            cloud_frame,
            text="🔗 URL do Download",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=self.COLORS["text"]
        )
        cloud_url_label.pack(anchor="w", pady=(0, 5))
        
        url_entry = ctk.CTkEntry(
            cloud_frame,
            height=40,
            corner_radius=8,
            fg_color=self.COLORS["bg_card"],
            border_color=self.COLORS["border"]
        )
        url_entry.pack(fill="x", pady=(0, 5))
        if software.get("url"):
            url_entry.insert(0, software["url"])
        
        def on_url_change(event=None):
            url = url_entry.get().strip()
            if url and args_entry_ref[0]:
                filename = extract_filename_from_url(url)
                suggested = detect_installer_args(filename)
                current_args = args_entry_ref[0].get().strip()
                if not current_args or current_args in ["/S", "/qn", "/qn /norestart"]:
                    args_entry_ref[0].delete(0, "end")
                    args_entry_ref[0].insert(0, suggested)
        
        url_entry.bind("<FocusOut>", on_url_change)
        
        cloud_hint = ctk.CTkLabel(
            cloud_frame,
            text="💡 O arquivo será baixado automaticamente durante a instalação",
            font=ctk.CTkFont(size=11),
            text_color=self.COLORS["cloud"]
        )
        cloud_hint.pack(anchor="w", pady=(0, 10))
        
        cloud_filename_label = ctk.CTkLabel(
            cloud_frame,
            text="📄 Nome do Arquivo",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=self.COLORS["text"]
        )
        cloud_filename_label.pack(anchor="w", pady=(0, 5))
        
        cloud_filename_entry = ctk.CTkEntry(
            cloud_frame,
            height=40,
            corner_radius=8,
            fg_color=self.COLORS["bg_card"],
            border_color=self.COLORS["border"]
        )
        cloud_filename_entry.pack(fill="x")
        if is_cloud:
            cloud_filename_entry.insert(0, software["filename"])
        
        # Mostra o frame correto inicialmente
        if is_cloud:
            cloud_frame.pack(fill="x", pady=(0, 15), after=source_frame)
        else:
            local_frame.pack(fill="x", pady=(0, 15), after=source_frame)
        
        # ─────────────────────────────────────────────────────
        # SEÇÃO: INFORMAÇÕES DO PROGRAMA
        # ─────────────────────────────────────────────────────
        
        section_info = ctk.CTkLabel(
            form_scroll,
            text="📝 Informações do Programa",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=self.COLORS["text"]
        )
        section_info.pack(anchor="w", pady=(15, 10))
        
        name_label = ctk.CTkLabel(
            form_scroll,
            text="Nome do Programa *",
            font=ctk.CTkFont(size=13),
            text_color=self.COLORS["text"]
        )
        name_label.pack(anchor="w", pady=(0, 5))
        
        name_entry = ctk.CTkEntry(
            form_scroll,
            height=40,
            corner_radius=8,
            fg_color=self.COLORS["bg_card"],
            border_color=self.COLORS["border"]
        )
        name_entry.pack(fill="x", pady=(0, 15))
        name_entry.insert(0, software["name"])
        
        desc_label = ctk.CTkLabel(
            form_scroll,
            text="Descrição (opcional)",
            font=ctk.CTkFont(size=13),
            text_color=self.COLORS["text"]
        )
        desc_label.pack(anchor="w", pady=(0, 5))
        
        desc_entry = ctk.CTkEntry(
            form_scroll,
            height=40,
            corner_radius=8,
            fg_color=self.COLORS["bg_card"],
            border_color=self.COLORS["border"]
        )
        desc_entry.pack(fill="x", pady=(0, 15))
        if software.get("description"):
            desc_entry.insert(0, software["description"])
        
        # ─────────────────────────────────────────────────────
        # SEÇÃO: CONFIGURAÇÃO DE INSTALAÇÃO
        # ─────────────────────────────────────────────────────
        
        section_config = ctk.CTkLabel(
            form_scroll,
            text="⚙️ Configuração de Instalação",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=self.COLORS["text"]
        )
        section_config.pack(anchor="w", pady=(15, 10))
        
        args_label = ctk.CTkLabel(
            form_scroll,
            text="Argumentos Silenciosos *",
            font=ctk.CTkFont(size=13),
            text_color=self.COLORS["text"]
        )
        args_label.pack(anchor="w", pady=(0, 5))
        
        args_entry = ctk.CTkEntry(
            form_scroll,
            height=40,
            corner_radius=8,
            fg_color=self.COLORS["bg_card"],
            border_color=self.COLORS["border"]
        )
        args_entry.pack(fill="x", pady=(0, 5))
        args_entry.insert(0, " ".join(software["args"]))
        args_entry_ref[0] = args_entry
        
        # Botão para auto-detectar argumentos
        def auto_detect_args():
            if source_type.get() == "cloud":
                url = url_entry.get().strip()
                if url:
                    filename = cloud_filename_entry.get().strip() or extract_filename_from_url(url)
                    suggested = detect_installer_args(filename)
                    args_entry.delete(0, "end")
                    args_entry.insert(0, suggested)
            else:
                filename = selected_filename.get()
                if filename:
                    suggested = detect_installer_args(filename)
                    args_entry.delete(0, "end")
                    args_entry.insert(0, suggested)
        
        args_hint_frame = ctk.CTkFrame(form_scroll, fg_color="transparent")
        args_hint_frame.pack(fill="x", pady=(0, 15))
        
        args_hint = ctk.CTkLabel(
            args_hint_frame,
            text="💡 /S (NSIS), /qn (MSI), /VERYSILENT (Inno)",
            font=ctk.CTkFont(size=11),
            text_color=self.COLORS["text_muted"]
        )
        args_hint.pack(side="left")
        
        auto_detect_btn = ctk.CTkButton(
            args_hint_frame,
            text="🔍 Auto-detectar",
            font=ctk.CTkFont(size=11),
            width=100,
            height=26,
            corner_radius=6,
            fg_color=self.COLORS["bg_card"],
            hover_color=self.COLORS["bg_hover"],
            command=auto_detect_args
        )
        auto_detect_btn.pack(side="right")
        
        express_var = ctk.BooleanVar(value=software["is_express"])
        express_check = ctk.CTkCheckBox(
            form_scroll,
            text="⚡ Incluir na Instalação Expressa",
            variable=express_var,
            font=ctk.CTkFont(size=13),
            fg_color=self.COLORS["accent"],
            hover_color=self.COLORS["accent_hover"]
        )
        express_check.pack(anchor="w", pady=(0, 20))
        
        # Mensagem de erro
        error_label = ctk.CTkLabel(
            form_scroll,
            text="",
            font=ctk.CTkFont(size=12),
            text_color=self.COLORS["error"]
        )
        error_label.pack(pady=(0, 10))
        
        # ─────────────────────────────────────────────────────
        # BOTÕES
        # ─────────────────────────────────────────────────────
        
        btn_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        btn_frame.pack(pady=(0, 20))
        
        cancel_btn = ctk.CTkButton(
            btn_frame,
            text="Cancelar",
            width=130,
            height=42,
            corner_radius=8,
            fg_color=self.COLORS["bg_card"],
            hover_color=self.COLORS["bg_hover"],
            command=dialog.destroy
        )
        cancel_btn.pack(side="left", padx=(0, 15))
        
        def save_changes():
            # Validação
            name = name_entry.get().strip()
            description = desc_entry.get().strip()
            args_text = args_entry.get().strip()
            is_express = express_var.get()
            is_cloud_now = source_type.get() == "cloud"
            
            if not name:
                error_label.configure(text="⚠️ Digite o nome do programa")
                return
            
            if not args_text:
                error_label.configure(text="⚠️ Digite os argumentos silenciosos")
                return
            
            if is_cloud_now:
                # Modo nuvem
                url = url_entry.get().strip()
                if not url:
                    error_label.configure(text="⚠️ Digite a URL do instalador")
                    return
                
                if not url.startswith(('http://', 'https://')):
                    error_label.configure(text="⚠️ URL deve começar com http:// ou https://")
                    return
                
                filename = cloud_filename_entry.get().strip()
                if not filename:
                    filename = extract_filename_from_url(url)
                
                # Atualiza o software
                args = args_text.split()
                catalog_manager.update_software(
                    software_id,
                    name=name,
                    filename=filename,
                    url=url,
                    args=args,
                    is_express=is_express,
                    description=description
                )
            else:
                # Modo local
                new_filepath = selected_file_path.get()
                filename = selected_filename.get()
                
                if not filename:
                    error_label.configure(text="⚠️ Nenhum arquivo selecionado")
                    return
                
                # Se selecionou um novo arquivo, copia
                if new_filepath:
                    dest_path = os.path.join(get_installers_path(), os.path.basename(new_filepath))
                    try:
                        if new_filepath != dest_path:
                            shutil.copy2(new_filepath, dest_path)
                        filename = os.path.basename(new_filepath)
                    except Exception as e:
                        error_label.configure(text=f"⚠️ Erro ao copiar: {e}")
                        return
                
                # Atualiza o software
                args = args_text.split()
                catalog_manager.update_software(
                    software_id,
                    name=name,
                    filename=filename,
                    url="",
                    args=args,
                    is_express=is_express,
                    description=description
                )
            
            dialog.destroy()
            self.render_installer_list()
        
        save_btn = ctk.CTkButton(
            btn_frame,
            text="💾  Salvar Alterações",
            font=ctk.CTkFont(size=14, weight="bold"),
            width=150,
            height=42,
            corner_radius=8,
            fg_color=self.COLORS["accent"],
            hover_color=self.COLORS["accent_hover"],
            command=save_changes
        )
        save_btn.pack(side="left")
    
    # ═══════════════════════════════════════════════════════════════════════
    # TELA 4: EXECUÇÃO DA INSTALAÇÃO
    # ═══════════════════════════════════════════════════════════════════════
    
    def show_execution_screen(self, software_list: List[Dict]):
        self.clear_container()
        self.is_installing = True
        
        header_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 20))
        
        title_label = ctk.CTkLabel(
            header_frame,
            text="📦  Instalando Software",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=self.COLORS["text"]
        )
        title_label.pack(side="left")
        
        self.progress_info = ctk.CTkLabel(
            header_frame,
            text=f"0 de {len(software_list)} concluídos",
            font=ctk.CTkFont(size=14),
            text_color=self.COLORS["text_muted"]
        )
        self.progress_info.pack(side="right")
        
        self.progress_bar = ctk.CTkProgressBar(
            self.main_container,
            height=8,
            corner_radius=4,
            fg_color=self.COLORS["bg_card"],
            progress_color=self.COLORS["accent"]
        )
        self.progress_bar.pack(fill="x", pady=(0, 5))
        self.progress_bar.set(0)
        
        self.current_status = ctk.CTkLabel(
            self.main_container,
            text="Iniciando...",
            font=ctk.CTkFont(size=13),
            text_color=self.COLORS["text_muted"]
        )
        self.current_status.pack(anchor="w", pady=(0, 15))
        
        log_label = ctk.CTkLabel(
            self.main_container,
            text="📋 Log de Instalação",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=self.COLORS["text"]
        )
        log_label.pack(anchor="w", pady=(0, 8))
        
        self.log_console = ctk.CTkTextbox(
            self.main_container,
            font=ctk.CTkFont(family="Consolas", size=12),
            fg_color=self.COLORS["bg_card"],
            text_color=self.COLORS["text"],
            corner_radius=10,
            border_width=1,
            border_color=self.COLORS["border"],
            wrap="word"
        )
        self.log_console.pack(fill="both", expand=True, pady=(0, 15))
        
        self.finish_btn = ctk.CTkButton(
            self.main_container,
            text="Aguarde a instalação...",
            font=ctk.CTkFont(size=15, weight="bold"),
            height=48,
            corner_radius=10,
            fg_color=self.COLORS["bg_card"],
            hover_color=self.COLORS["bg_card"],
            state="disabled",
            command=self.show_home_screen
        )
        self.finish_btn.pack(fill="x")
        
        self.log_message("═" * 50, "info")
        self.log_message("AutoSetup Empresarial v1.0", "info")
        self.log_message(f"Iniciando instalação de {len(software_list)} programa(s)", "info")
        self.log_message("═" * 50, "info")
        
        install_thread = threading.Thread(
            target=self.run_installations,
            args=(software_list,),
            daemon=True
        )
        install_thread.start()
    
    def log_message(self, message: str, level: str = "info"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        prefixes = {
            "info": "ℹ️ ",
            "success": "✅ ",
            "error": "❌ ",
            "warning": "⚠️ ",
            "download": "⬇️ "
        }
        prefix = prefixes.get(level, "")
        formatted_message = f"[{timestamp}] {prefix}{message}\n"
        
        self.log_console.configure(state="normal")
        self.log_console.insert("end", formatted_message)
        self.log_console.see("end")
        self.log_console.configure(state="disabled")
    
    def run_installations(self, software_list: List[Dict]):
        total = len(software_list)
        success_count = 0
        error_count = 0
        
        for i, software in enumerate(software_list, 1):
            if not self.is_installing:
                break
            
            software_name = software["name"]
            is_cloud = bool(software.get("url"))
            
            # Atualiza status
            self.after(0, lambda s=software_name: self.current_status.configure(
                text=f"Processando: {s}..."
            ))
            
            installer_path = ""
            
            # Se for da nuvem, faz o download primeiro
            if is_cloud:
                self.after(0, lambda msg=f"\n☁️ Baixando {software_name}...", lvl="download": 
                           self.log_message(msg, lvl))
                
                self.after(0, lambda: self.current_status.configure(
                    text=f"Baixando: {software_name}..."
                ))
                
                download_result = download_file(
                    url=software["url"],
                    filename=software["filename"]
                )
                
                if not download_result.success:
                    error_count += 1
                    self.after(0, lambda msg=f"{software_name}: DOWNLOAD FALHOU - {download_result.message}": 
                               self.log_message(msg, "error"))
                    
                    progress = i / total
                    self.after(0, lambda p=progress: self.progress_bar.set(p))
                    self.after(0, lambda c=i, t=total: self.progress_info.configure(
                        text=f"{c} de {t} concluídos"
                    ))
                    continue
                
                installer_path = download_result.filepath
                self.after(0, lambda msg=f"Download concluído: {software['filename']}": 
                           self.log_message(msg, "success"))
            else:
                installer_path = os.path.join(get_installers_path(), software["filename"])
            
            # Instala
            self.after(0, lambda msg=f"\n🔧 Instalando {software_name}...", lvl="info": 
                       self.log_message(msg, lvl))
            
            self.after(0, lambda s=software_name: self.current_status.configure(
                text=f"Instalando: {s}..."
            ))
            
            result = run_installer(
                filepath=installer_path,
                args=software["args"],
                software_name=software_name
            )
            
            if result.success:
                success_count += 1
                self.after(0, lambda msg=f"{software_name}: {result.message}": 
                           self.log_message(msg, "success"))
            else:
                error_count += 1
                self.after(0, lambda msg=f"{software_name}: FALHOU - {result.message}": 
                           self.log_message(msg, "error"))
            
            # Limpa arquivo temporário se foi da nuvem
            if is_cloud and installer_path and os.path.exists(installer_path):
                try:
                    os.remove(installer_path)
                except:
                    pass
            
            progress = i / total
            self.after(0, lambda p=progress: self.progress_bar.set(p))
            self.after(0, lambda c=i, t=total: self.progress_info.configure(
                text=f"{c} de {t} concluídos"
            ))
        
        self.after(0, lambda: self._finish_installation(success_count, error_count, total))
    
    def _finish_installation(self, success: int, errors: int, total: int):
        self.is_installing = False
        
        self.log_message("═" * 50, "info")
        self.log_message(f"INSTALAÇÃO CONCLUÍDA", "info")
        self.log_message(f"✅ Sucesso: {success}  |  ❌ Erros: {errors}  |  📦 Total: {total}", "info")
        self.log_message("═" * 50, "info")
        
        self.current_status.configure(text="Instalação concluída!")
        
        if errors == 0:
            btn_text = "✅  Concluído - Voltar ao Início"
            btn_color = self.COLORS["success"]
        else:
            btn_text = f"⚠️  Concluído com {errors} erro(s) - Voltar"
            btn_color = self.COLORS["warning"]
        
        self.finish_btn.configure(
            text=btn_text,
            fg_color=btn_color,
            hover_color=btn_color,
            state="normal"
        )
    
    # ═══════════════════════════════════════════════════════════════════════
    # MÉTODOS UTILITÁRIOS
    # ═══════════════════════════════════════════════════════════════════════
    
    def open_installers_folder(self):
        """Abre a pasta de instaladores no explorador de arquivos"""
        folder_path = get_installers_path()
        try:
            os.startfile(folder_path)
        except Exception as e:
            self.show_error_dialog(f"Erro ao abrir pasta: {e}")
    
    # ═══════════════════════════════════════════════════════════════════════
    # TELA DE AJUDA - TUTORIAL PARA USUÁRIOS
    # ═══════════════════════════════════════════════════════════════════════
    
    def show_help_screen(self):
        """Exibe a tela de ajuda com tutorial completo para usuários"""
        dialog = ctk.CTkToplevel(self)
        dialog.title("Como Usar o AutoSetup")
        dialog.geometry("700x600")
        dialog.resizable(False, True)
        dialog.minsize(700, 500)
        dialog.transient(self)
        dialog.grab_set()
        
        dialog.update_idletasks()
        x = self.winfo_x() + (self.winfo_width() - 700) // 2
        y = self.winfo_y() + (self.winfo_height() - 600) // 2
        dialog.geometry(f"+{x}+{y}")
        
        dialog.configure(fg_color=self.COLORS["bg_dark"])
        
        # Título
        header_frame = ctk.CTkFrame(dialog, fg_color=self.COLORS["bg_card"], corner_radius=0)
        header_frame.pack(fill="x")
        
        title_label = ctk.CTkLabel(
            header_frame,
            text="📖  Como Usar o AutoSetup",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color=self.COLORS["text"]
        )
        title_label.pack(pady=20)
        
        # Conteúdo scrollável
        content_scroll = ctk.CTkScrollableFrame(
            dialog,
            fg_color="transparent",
            scrollbar_button_color=self.COLORS["bg_hover"],
            scrollbar_button_hover_color=self.COLORS["accent"]
        )
        content_scroll.pack(fill="both", expand=True, padx=20, pady=10)
        
        # ═══════════════════════════════════════════════════════════════
        # SEÇÃO 1: O QUE É O AUTOSETUP
        # ═══════════════════════════════════════════════════════════════
        
        self._add_help_section(
            content_scroll,
            "🤔  O que é o AutoSetup?",
            "O AutoSetup é um programa que instala vários softwares de uma vez só, "
            "sem você precisar ficar clicando 'Avançar' em cada instalador.\n\n"
            "Ideal para quando você formata o computador e precisa instalar "
            "Chrome, WinRAR, leitor de PDF, etc."
        )
        
        # ═══════════════════════════════════════════════════════════════
        # SEÇÃO 2: INSTALAÇÃO EXPRESSA
        # ═══════════════════════════════════════════════════════════════
        
        self._add_help_section(
            content_scroll,
            "⚡  Instalação Expressa",
            "Use esta opção para instalar rapidamente os programas mais comuns.\n\n"
            "Como usar:\n"
            "1. Clique no botão 'Instalação Expressa'\n"
            "2. Aguarde enquanto os programas são instalados\n"
            "3. Pronto! Todos os programas essenciais estarão instalados\n\n"
            "Dica: Os programas marcados como 'EXPRESS' serão instalados automaticamente."
        )
        
        # ═══════════════════════════════════════════════════════════════
        # SEÇÃO 3: INSTALAÇÃO PERSONALIZADA
        # ═══════════════════════════════════════════════════════════════
        
        self._add_help_section(
            content_scroll,
            "🎯  Instalação Personalizada",
            "Use esta opção para escolher exatamente quais programas instalar.\n\n"
            "Como usar:\n"
            "1. Clique em 'Instalação Personalizada'\n"
            "2. Marque os programas que deseja instalar\n"
            "3. Use 'Selecionar Todos' ou 'Limpar Seleção' para agilizar\n"
            "4. Clique em 'Instalar Selecionados'\n"
            "5. Aguarde a conclusão"
        )
        
        # ═══════════════════════════════════════════════════════════════
        # SEÇÃO 4: GERENCIAR INSTALADORES
        # ═══════════════════════════════════════════════════════════════
        
        self._add_help_section(
            content_scroll,
            "📦  Gerenciar Instaladores",
            "Aqui você adiciona, edita ou remove programas da lista.\n\n"
            "Para adicionar um programa do seu computador:\n"
            "1. Clique em 'Gerenciar Instaladores'\n"
            "2. Clique em '+ Adicionar Novo'\n"
            "3. Escolha 'Arquivo Local'\n"
            "4. Clique em 'Localizar' e selecione o instalador (.exe ou .msi)\n"
            "5. Dê um nome ao programa\n"
            "6. Clique em 'Salvar'\n\n"
            "Para adicionar um programa da internet:\n"
            "1. Escolha 'URL da Nuvem'\n"
            "2. Cole o link direto do instalador\n"
            "3. O programa será baixado automaticamente na hora de instalar"
        )
        
        # ═══════════════════════════════════════════════════════════════
        # SEÇÃO 5: ONDE FICAM OS INSTALADORES
        # ═══════════════════════════════════════════════════════════════
        
        self._add_help_section(
            content_scroll,
            "📁  Onde ficam os instaladores?",
            "MODO PORTÁTIL (PENDRIVE):\n\n"
            "Os instaladores devem estar na pasta 'installers' no MESMO local "
            "onde está o executável do AutoSetup.\n\n"
            "Exemplo de organização no pendrive:\n"
            "   📁 Pendrive (E:)\n"
            "   ├── AutoSetup_Empresarial.exe\n"
            "   └── 📁 installers\n"
            "       ├── ChromeSetup.exe\n"
            "       ├── WinRAR.exe\n"
            "       └── outros instaladores...\n\n"
            "Dica: Use o botão 'Abrir Pasta de Instaladores' para acessar rapidamente!"
        )
        
        # ═══════════════════════════════════════════════════════════════
        # SEÇÃO 6: DICAS IMPORTANTES
        # ═══════════════════════════════════════════════════════════════
        
        self._add_help_section(
            content_scroll,
            "💡  Dicas Importantes",
            "• Execute o programa como Administrador para evitar erros\n\n"
            "• Alguns antivírus podem bloquear instalações silenciosas - "
            "desative temporariamente se necessário\n\n"
            "• Se uma instalação falhar, verifique se o arquivo do instalador "
            "está correto e não está corrompido\n\n"
            "• O código de erro 3010 significa sucesso, mas precisa reiniciar o PC\n\n"
            "• Programas da nuvem precisam de conexão com a internet"
        )
        
        # ═══════════════════════════════════════════════════════════════
        # SEÇÃO 7: SUPORTE
        # ═══════════════════════════════════════════════════════════════
        
        support_frame = ctk.CTkFrame(content_scroll, fg_color=self.COLORS["bg_card"], corner_radius=10)
        support_frame.pack(fill="x", pady=(15, 5))
        
        support_title = ctk.CTkLabel(
            support_frame,
            text="🆘  Precisa de ajuda?",
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color=self.COLORS["accent"]
        )
        support_title.pack(pady=(15, 5), padx=15, anchor="w")
        
        support_text = ctk.CTkLabel(
            support_frame,
            text="Entre em contato com a ELSE SYSTEMS para suporte técnico.",
            font=ctk.CTkFont(size=13),
            text_color=self.COLORS["text_muted"],
            wraplength=600,
            justify="left"
        )
        support_text.pack(pady=(0, 5), padx=15, anchor="w")
        
        support_link = ctk.CTkLabel(
            support_frame,
            text="🌐 elsesystems.com",
            font=ctk.CTkFont(size=13, underline=True),
            text_color=self.COLORS["cloud"],
            cursor="hand2"
        )
        support_link.pack(pady=(0, 15), padx=15, anchor="w")
        support_link.bind("<Button-1>", lambda e: webbrowser.open("https://elsesystems.com"))
        
        # Botão fechar
        close_btn = ctk.CTkButton(
            dialog,
            text="Entendi!",
            font=ctk.CTkFont(size=15, weight="bold"),
            width=150,
            height=45,
            corner_radius=10,
            fg_color=self.COLORS["accent"],
            hover_color=self.COLORS["accent_hover"],
            command=dialog.destroy
        )
        close_btn.pack(pady=20)
    
    def _add_help_section(self, parent, title: str, content: str):
        """Adiciona uma seção de ajuda formatada"""
        frame = ctk.CTkFrame(parent, fg_color=self.COLORS["bg_card"], corner_radius=10)
        frame.pack(fill="x", pady=(0, 15))
        
        title_label = ctk.CTkLabel(
            frame,
            text=title,
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color=self.COLORS["text"]
        )
        title_label.pack(pady=(15, 8), padx=15, anchor="w")
        
        content_label = ctk.CTkLabel(
            frame,
            text=content,
            font=ctk.CTkFont(size=13),
            text_color=self.COLORS["text_muted"],
            wraplength=600,
            justify="left"
        )
        content_label.pack(pady=(0, 15), padx=15, anchor="w")
    
    # ═══════════════════════════════════════════════════════════════════════
    # MÉTODOS DE INICIAÇÃO
    # ═══════════════════════════════════════════════════════════════════════
    
    def start_express_install(self):
        express_software = [s for s in catalog_manager.catalog if s["is_express"]]
        if express_software:
            self.show_execution_screen(express_software)
        else:
            self.show_error_dialog("Nenhum software marcado para instalação expressa.")
    
    def start_custom_install(self):
        selected = [
            s for s in catalog_manager.catalog 
            if self.selected_software.get(s["id"], ctk.BooleanVar()).get()
        ]
        
        if selected:
            self.show_execution_screen(selected)
        else:
            self.show_error_dialog("Selecione pelo menos um programa para instalar.")
    
    def show_error_dialog(self, message: str):
        dialog = ctk.CTkToplevel(self)
        dialog.title("Atenção")
        dialog.geometry("400x150")
        dialog.resizable(False, False)
        dialog.transient(self)
        dialog.grab_set()
        
        dialog.update_idletasks()
        x = self.winfo_x() + (self.winfo_width() - 400) // 2
        y = self.winfo_y() + (self.winfo_height() - 150) // 2
        dialog.geometry(f"+{x}+{y}")
        
        dialog.configure(fg_color=self.COLORS["bg_dark"])
        
        icon_label = ctk.CTkLabel(dialog, text="⚠️", font=ctk.CTkFont(size=36))
        icon_label.pack(pady=(20, 10))
        
        msg_label = ctk.CTkLabel(
            dialog,
            text=message,
            font=ctk.CTkFont(size=14),
            text_color=self.COLORS["text"]
        )
        msg_label.pack()
        
        ok_btn = ctk.CTkButton(
            dialog,
            text="OK",
            width=100,
            height=36,
            corner_radius=8,
            fg_color=self.COLORS["accent"],
            command=dialog.destroy
        )
        ok_btn.pack(pady=15)


# ══════════════════════════════════════════════════════════════════════════════
# PONTO DE ENTRADA
# ══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    app = AutoSetupApp()
    app.mainloop()
