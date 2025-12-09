<div align="center">

# ⚙️ AutoSetup Empresarial

### Assistente de Pós-Formatação Automatizado para Windows

[![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![CustomTkinter](https://img.shields.io/badge/UI-CustomTkinter-00D4AA?style=for-the-badge)](https://github.com/TomSchimansky/CustomTkinter)
[![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)](LICENSE)
[![Windows](https://img.shields.io/badge/Windows-10%2F11-0078D6?style=for-the-badge&logo=windows&logoColor=white)](https://www.microsoft.com/windows)

<br>

**Automatize a instalação de softwares após formatar seu computador.**  
*Uma ferramenta portátil para TI que economiza horas de trabalho.*

<br>

[📥 Download](#-instalação) • [📖 Como Usar](#-como-usar) • [🤝 Contribuir](CONTRIBUTING.md) • [🐛 Reportar Bug](https://github.com/SamuelElse/AutoSetup-Empresarial/issues)

</div>

---

## 📋 Sobre o Projeto

O **AutoSetup Empresarial** é uma ferramenta desktop desenvolvida em Python que automatiza a instalação de softwares em computadores Windows. 

**100% Portátil** - Coloque em um pendrive com os instaladores e use em qualquer computador!

### ✨ Destaques

| Recurso | Descrição |
|---------|-----------|
| 💾 **Modo Portátil** | Funciona direto do pendrive, sem precisar instalar |
| ⚡ **Instalação Expressa** | Configure um PC novo em minutos com softwares essenciais |
| 🎯 **Instalação Personalizada** | Escolha exatamente quais programas instalar |
| ☁️ **Download da Nuvem** | Baixe instaladores automaticamente de URLs |
| 🔇 **Modo Silencioso** | Instalações sem pop-ups ou interação manual |
| ❓ **Ajuda Integrada** | Tutorial completo para usuários iniciantes |
| 🛡️ **Privilégios Admin** | Solicita elevação automaticamente quando necessário |

---

## 🚀 Instalação

### Opção 1: Baixar Executável (Recomendado)

1. Acesse a página de [Releases](https://github.com/SamuelElse/AutoSetup-Empresarial/releases)
2. Baixe `AutoSetup_Empresarial.exe`
3. Pronto! Não precisa instalar nada

### Opção 2: Executar do Código Fonte

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

### Opção 3: Compilar seu Próprio Executável

```bash
python build.py --clean
```

O executável será criado em `dist/AutoSetup_Empresarial.exe`

---

## 💾 Modo Portátil (Pendrive)

O AutoSetup foi projetado para funcionar de forma **100% portátil**. Basta organizar os arquivos assim:

```
📁 Pendrive (E:) ou qualquer pasta
├── AutoSetup_Empresarial.exe    ← O programa
├── software_catalog.json        ← Criado automaticamente
└── 📁 installers                ← Seus instaladores aqui
    ├── ChromeSetup.exe
    ├── WinRAR.exe
    ├── AdobeReader.exe
    └── outros...
```

> 💡 **Importante:** A pasta `installers` deve estar no **mesmo local** que o executável!

---

## 📖 Como Usar

### Tela Inicial

Ao abrir o programa, você verá 3 opções principais e um botão de ajuda:

| Botão | Função |
|-------|--------|
| **?** (canto superior direito) | Abre o tutorial completo |
| **⚡ Instalação Expressa** | Instala todos os programas marcados como essenciais |
| **🎯 Instalação Personalizada** | Permite escolher quais programas instalar |
| **📦 Gerenciar Instaladores** | Adicionar, editar ou remover programas |

---

### ⚡ Instalação Expressa

Instala automaticamente todos os programas marcados como "EXPRESS".

**Como usar:**
1. Clique em **"⚡ Instalação Expressa"**
2. Aguarde enquanto os programas são instalados
3. Pronto!

---

### 🎯 Instalação Personalizada

Escolha exatamente quais programas instalar.

**Como usar:**
1. Clique em **"🎯 Instalação Personalizada"**
2. Marque os programas desejados
3. Use **"Selecionar Todos"** ou **"Limpar Seleção"** para agilizar
4. Clique em **"🚀 Instalar Selecionados"**

---

### 📦 Gerenciar Instaladores

Adicione, edite ou remova programas do catálogo.

#### Adicionar Programa Local

1. Clique em **"📦 Gerenciar Instaladores"**
2. Clique em **"➕ Adicionar Novo"**
3. Selecione **"💾 Arquivo Local"**
4. Clique em **"📂 Localizar"** e escolha o `.exe` ou `.msi`
5. Dê um nome ao programa
6. Os argumentos silenciosos são detectados automaticamente
7. Marque **"⚡ Incluir na Instalação Expressa"** se desejar
8. Clique em **"💾 Salvar"**

#### Adicionar Programa da Nuvem

1. Escolha **"☁️ URL da Nuvem"**
2. Cole o link direto do instalador
3. Preencha o nome
4. O programa será baixado automaticamente na hora de instalar

#### Abrir Pasta de Instaladores

- Na tela de gerenciamento, clique em **"📂 Abrir Pasta de Instaladores"**
- Isso abre a pasta onde você deve colocar os arquivos `.exe` e `.msi`

---

### ❓ Tela de Ajuda

Clique no botão **"?"** no canto superior direito para ver o tutorial completo com:

- O que é o AutoSetup
- Como usar cada funcionalidade
- Onde colocar os instaladores
- Dicas importantes
- Contato para suporte

---

## 🔧 Silent Switches (Argumentos Silenciosos)

Os "silent switches" fazem instaladores rodarem sem interação do usuário.

### Como Descobrir

```bash
instalador.exe /?
instalador.exe /help
instalador.exe --help
```

Ou pesquise: `"nome do programa" silent install switches`

### Tabela de Referência

| Tipo de Instalador | Switches Comuns |
|-------------------|-----------------|
| **MSI** (.msi) | `/qn /norestart` |
| **NSIS** | `/S` (maiúsculo!) |
| **Inno Setup** | `/VERYSILENT /SUPPRESSMSGBOXES /NORESTART` |
| **InstallShield** | `/s /v"/qn"` |

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
└── 📁 installers/             # Pasta para instaladores
    └── .gitkeep
```

### Arquivos Gerados em Runtime

| Arquivo | Descrição |
|---------|-----------|
| `software_catalog.json` | Catálogo de programas (salvo na mesma pasta do .exe) |

---

## 🛠️ Tecnologias Utilizadas

- **[Python 3.8+](https://python.org)** - Linguagem de programação
- **[CustomTkinter](https://github.com/TomSchimansky/CustomTkinter)** - Interface gráfica moderna
- **[Pillow](https://pillow.readthedocs.io/)** - Processamento de imagens
- **[PyInstaller](https://pyinstaller.org/)** - Empacotador para executável

---

## 🐛 Solução de Problemas

### "Arquivo não encontrado"
- Verifique se a pasta `installers` está no **mesmo local** que o executável
- Confirme que o nome do arquivo no catálogo está correto

### "Instalação falhou (código X)"
- Verifique se os switches silenciosos estão corretos
- Execute como Administrador
- **Código 3010** = Sucesso, mas precisa reiniciar o PC

### "Interface não abre"
- Verifique se está executando como Administrador
- Se rodando do código: `pip install customtkinter pillow`

### "Download falhou"
- Verifique sua conexão com a internet
- Algumas URLs bloqueiam downloads automatizados
- Tente baixar manualmente e usar como arquivo local

---

## 🤝 Contribuindo

Contribuições são muito bem-vindas! Veja o arquivo [CONTRIBUTING.md](CONTRIBUTING.md) para detalhes.

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

## 🏢 Desenvolvido por

<div align="center">

**ELSE SYSTEMS LTDA**

[![Website](https://img.shields.io/badge/Website-elsesystems.com-00D4AA?style=for-the-badge&logo=google-chrome&logoColor=white)](https://elsesystems.com)

*Transformando Negócios com Tecnologia*

</div>

---

## 🙏 Agradecimentos

- [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter) pela excelente biblioteca de UI
- [SilentInstallHQ](https://silentinstallhq.com/) pela documentação de switches
- Comunidade open-source por todo o suporte

---

<div align="center">

**⭐ Se este projeto te ajudou, considere dar uma estrela!**

Feito com ❤️ por [Samuel Else](https://github.com/SamuelElse) | [ELSE SYSTEMS](https://elsesystems.com)

</div>
