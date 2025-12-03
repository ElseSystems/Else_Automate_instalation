<div align="center">

# ⚙️ AutoSetup Empresarial

### Assistente de Pós-Formatação Automatizado para Windows

[![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![CustomTkinter](https://img.shields.io/badge/UI-CustomTkinter-00D4AA?style=for-the-badge)](https://github.com/TomSchimansky/CustomTkinter)
[![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)](LICENSE)
[![Windows](https://img.shields.io/badge/Windows-10%2F11-0078D6?style=for-the-badge&logo=windows&logoColor=white)](https://www.microsoft.com/windows)

<br>

**Automatize a instalação de softwares após formatar seu computador.**  
*Uma ferramenta profissional para TI que economiza horas de trabalho.*

<br>

[📥 Download](#-instalação) • [📖 Documentação](#-funcionalidades) • [🤝 Contribuir](CONTRIBUTING.md) • [🐛 Reportar Bug](https://github.com/SamuelElse/AutoSetup-Empresarial/issues)

</div>

---

## 📋 Sobre o Projeto

O **AutoSetup Empresarial** é uma ferramenta desktop desenvolvida em Python que automatiza a instalação de softwares em computadores Windows. Ideal para profissionais de TI que precisam configurar múltiplas máquinas após formatação.

### ✨ Destaques

| Recurso | Descrição |
|---------|-----------|
| ⚡ **Instalação Expressa** | Configure um PC novo em minutos com softwares essenciais |
| 🎯 **Instalação Personalizada** | Escolha exatamente quais programas instalar |
| ☁️ **Download da Nuvem** | Baixe instaladores automaticamente de URLs |
| 📦 **Executável Único** | Compile tudo em um único `.exe` portátil |
| 🔇 **Modo Silencioso** | Instalações sem pop-ups ou interação manual |
| 🛡️ **Privilégios Admin** | Solicita elevação automaticamente quando necessário |

---

## 🖥️ Screenshots

<div align="center">

### Tela Inicial
*Interface moderna com opções de instalação expressa ou personalizada*

### Seleção de Programas  
*Lista completa com checkboxes, badges e descrições*

### Console de Instalação
*Log em tempo real com barra de progresso*

</div>

---

## 🚀 Instalação

### Pré-requisitos

- **Python** 3.8 ou superior
- **Windows** 10 ou 11
- **Privilégios de Administrador** (para instalações)

### Opção 1: Executar do Código Fonte

```bash
# 1. Clone o repositório
git clone https://github.com/SamuelElse/AutoSetup-Empresarial.git
cd AutoSetup-Empresarial

# 2. Crie um ambiente virtual (recomendado)
python -m venv venv
venv\Scripts\activate

# 3. Instale as dependências
pip install -r requirements.txt

# 4. Execute o aplicativo
python main.py
```

### Opção 2: Baixar Executável

Acesse a página de [Releases](https://github.com/SamuelElse/AutoSetup-Empresarial/releases) e baixe a versão mais recente do `AutoSetup_Empresarial.exe`.

### Opção 3: Compilar seu Próprio Executável

```bash
# Execute o script de build
python build.py

# Ou com opções
python build.py --clean      # Limpa builds anteriores
python build.py --console    # Mantém console para debug
```

O executável será criado em `dist/AutoSetup_Empresarial.exe`

---

## 📖 Funcionalidades

### ⚡ Instalação Expressa

A instalação expressa executa todos os programas marcados como "essenciais" automaticamente.

**Como usar:**
1. Abra o aplicativo
2. Clique em **"⚡ Instalação Expressa"**
3. Aguarde a conclusão de todas as instalações

**Programas padrão da instalação expressa:**
- Google Chrome (navegador)
- Adobe Acrobat Reader (leitor PDF)
- 7-Zip (compactador)

### 🎯 Instalação Personalizada

Permite selecionar exatamente quais programas você deseja instalar.

**Como usar:**
1. Clique em **"🎯 Instalação Personalizada"**
2. Marque os programas desejados na lista
3. Use os botões "Selecionar Todos" ou "Limpar Seleção" para agilizar
4. Clique em **"🚀 Instalar Selecionados"**

### 📦 Gerenciar Instaladores

Adicione, edite ou remova programas do catálogo de instalação.

**Como adicionar um programa LOCAL:**
1. Clique em **"📦 Gerenciar Instaladores"**
2. Clique em **"➕ Adicionar Novo"**
3. Selecione **"💾 Arquivo Local"**
4. Clique em **"📂 Localizar"** e escolha o arquivo `.exe` ou `.msi`
5. Preencha o nome e descrição
6. Os argumentos silenciosos são detectados automaticamente
7. Marque **"⚡ Incluir na Instalação Expressa"** se desejar
8. Clique em **"💾 Salvar"**

**Como adicionar um programa da NUVEM:**
1. Clique em **"➕ Adicionar Novo"**
2. Selecione **"☁️ URL da Nuvem"**
3. Cole a URL direta do instalador
4. Preencha o nome e descrição
5. Clique em **"💾 Salvar"**

> 💡 **Dica:** O arquivo será baixado automaticamente durante a instalação

### ✏️ Editar Programa

1. Na tela de gerenciamento, clique no ícone **✏️** do programa
2. Modifique as informações desejadas
3. Clique em **"💾 Salvar Alterações"**

### 🗑️ Remover Programa

1. Clique no ícone **🗑️** do programa
2. Confirme a remoção no diálogo

---

## 🔧 Silent Switches (Argumentos Silenciosos)

Os "silent switches" são argumentos que fazem instaladores rodarem sem interação do usuário.

### Como Descobrir os Switches

**Método 1 - Linha de comando:**
```bash
instalador.exe /?
instalador.exe /help
instalador.exe --help
```

**Método 2 - Pesquisa online:**
```
"nome do programa" silent install switches
```

**Método 3 - Sites especializados:**
- [SilentInstallHQ](https://silentinstallhq.com/)
- [ITNinja](https://www.itninja.com/software)

### Tabela de Referência Rápida

| Tipo de Instalador | Switches Comuns | Exemplo |
|-------------------|-----------------|---------|
| **MSI** (.msi) | `/qn /norestart` | `msiexec /i app.msi /qn` |
| **NSIS** | `/S` (maiúsculo!) | `app.exe /S` |
| **Inno Setup** | `/VERYSILENT /SUPPRESSMSGBOXES /NORESTART` | `setup.exe /VERYSILENT` |
| **InstallShield** | `/s /v"/qn"` | `setup.exe /s /v"/qn"` |

### Switches por Programa

| Programa | Switch |
|----------|--------|
| Google Chrome | `/silent /install` |
| Firefox | `-ms` |
| Adobe Reader | `/sAll /rs /msi EULA_ACCEPT=YES` |
| 7-Zip | `/S` |
| WinRAR | `/S` |
| VLC | `/S /L=1046` |
| VS Code | `/VERYSILENT /NORESTART /MERGETASKS=!runcode` |
| Git | `/VERYSILENT /NORESTART` |
| Node.js | `/qn` |
| Python | `/quiet InstallAllUsers=1 PrependPath=1` |
| AnyDesk | `--install` |
| TeamViewer | `/S` |

---

## 📁 Estrutura do Projeto

```
AutoSetup-Empresarial/
├── 📄 main.py                 # Aplicação principal
├── 📄 build.py                # Script de compilação
├── 📄 requirements.txt        # Dependências Python
├── 📄 LICENSE                 # Licença MIT
├── 📄 README.md               # Esta documentação
├── 📄 CONTRIBUTING.md         # Guia de contribuição
├── 📄 .gitignore              # Arquivos ignorados pelo Git
└── 📁 installers/             # Pasta para instaladores locais
    └── .gitkeep               # Mantém a pasta no repositório
```

### Arquivos Gerados em Runtime

| Arquivo | Descrição |
|---------|-----------|
| `software_catalog.json` | Catálogo de programas (persistido localmente) |
| `build/` | Arquivos temporários de compilação |
| `dist/` | Executável compilado |

---

## 🛠️ Tecnologias Utilizadas

- **[Python 3.8+](https://python.org)** - Linguagem de programação
- **[CustomTkinter](https://github.com/TomSchimansky/CustomTkinter)** - Interface gráfica moderna
- **[Pillow](https://pillow.readthedocs.io/)** - Processamento de imagens
- **[PyInstaller](https://pyinstaller.org/)** - Empacotador para executável

---

## 🐛 Solução de Problemas

### "Arquivo não encontrado"
- Verifique se o instalador está na pasta `installers/`
- Confirme que o nome do arquivo no catálogo está correto

### "Instalação falhou (código X)"
- Verifique se os switches silenciosos estão corretos
- Execute como Administrador
- **Código 3010** = Sucesso, mas reinicialização necessária

### "Interface não abre"
- Verifique se CustomTkinter está instalado: `pip install customtkinter`
- Execute pelo terminal para ver erros: `python main.py`

### "Download falhou"
- Verifique se a URL está acessível
- Algumas URLs requerem autenticação ou bloqueiam downloads automatizados
- Tente baixar manualmente e usar como arquivo local

---

## 🤝 Contribuindo

Contribuições são muito bem-vindas! Veja o arquivo [CONTRIBUTING.md](CONTRIBUTING.md) para detalhes sobre como contribuir.

### Formas de Contribuir

- 🐛 Reportar bugs
- 💡 Sugerir novas funcionalidades
- 📝 Melhorar a documentação
- 🔧 Enviar pull requests
- ⭐ Dar uma estrela no repositório

---

## 📄 Licença

Este projeto está licenciado sob a **MIT License** - veja o arquivo [LICENSE](LICENSE) para detalhes.

---

## 👤 Autor

<div align="center">

**Samuel Else**

[![GitHub](https://img.shields.io/badge/GitHub-SamuelElse-181717?style=for-the-badge&logo=github)](https://github.com/SamuelElse)

</div>

---

## 🙏 Agradecimentos

- [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter) pela excelente biblioteca de UI
- [SilentInstallHQ](https://silentinstallhq.com/) pela documentação de switches
- Comunidade open-source por todo o suporte

---

<div align="center">

**⭐ Se este projeto te ajudou, considere dar uma estrela!**

Feito com ❤️ por [Samuel Else](https://github.com/SamuelElse)

</div>
