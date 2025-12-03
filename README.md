# 🚀 AutoSetup Empresarial v1.0

> Assistente de Pós-Formatação Automatizado para Windows

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![CustomTkinter](https://img.shields.io/badge/UI-CustomTkinter-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

<p align="center">
  <img src="https://img.shields.io/badge/⚙️-AutoSetup-6366f1?style=for-the-badge&logoColor=white" alt="AutoSetup Logo"/>
</p>

## 📋 Visão Geral

O **AutoSetup Empresarial** é uma ferramenta que automatiza a instalação de software após uma formatação de sistema. Com uma interface moderna e intuitiva, ele permite:

- ⚡ **Instalação Expressa**: Configure um computador novo em minutos
- 🎯 **Instalação Personalizada**: Escolha exatamente o que instalar
- 📦 **Executável Único**: Todos os instaladores embutidos em um único `.exe`
- 🔇 **Instalação Silenciosa**: Sem pop-ups ou interações manuais

---

## 🛠️ Instalação e Uso

### Pré-requisitos

- Python 3.8 ou superior
- Windows 10/11

### Configuração Rápida

```bash
# 1. Clone o repositório
git clone https://github.com/seu-usuario/autosetup-empresarial.git
cd autosetup-empresarial

# 2. Crie um ambiente virtual (recomendado)
python -m venv venv
venv\Scripts\activate

# 3. Instale as dependências
pip install -r requirements.txt

# 4. Execute o aplicativo
python main.py
```

---

## 📁 Estrutura do Projeto

```
autosetup-empresarial/
├── main.py                        # Código principal da aplicação
├── requirements.txt               # Dependências Python
├── build.bat                      # Script de compilação
├── AutoSetup_Empresarial.spec     # Configuração avançada do PyInstaller
├── installers/                    # 📦 Coloque os instaladores aqui
│   ├── ChromeSetup.exe
│   ├── 7z_installer.exe
│   ├── AcroRdrDC.exe
│   └── ...
└── README.md
```

---

## ➕ Adicionando Novos Programas

### Passo 1: Obtenha o Instalador

Baixe o instalador offline do programa desejado e coloque na pasta `installers/`.

### Passo 2: Descubra os Silent Switches

Os "silent switches" são argumentos que fazem a instalação rodar sem interação do usuário.

#### Métodos para Descobrir:

1. **Execute no CMD:**
   ```bash
   instalador.exe /?
   instalador.exe /help
   instalador.exe --help
   ```

2. **Pesquise no Google:**
   ```
   "nome do programa" silent install switches
   ```

3. **Sites Especializados:**
   - [SilentInstallHQ](https://silentinstallhq.com/)
   - [ITNinja](https://www.itninja.com/software)

#### Switches Comuns por Tipo de Instalador:

| Tipo de Instalador | Switches Típicos |
|-------------------|------------------|
| **MSI** (.msi) | `/qn` `/quiet` `/passive` `/norestart` |
| **NSIS** | `/S` (maiúsculo!) `/D=C:\caminho` |
| **Inno Setup** | `/VERYSILENT` `/SUPPRESSMSGBOXES` `/NORESTART` |
| **InstallShield** | `/s` `/v"/qn"` `/SMS` |

### Passo 3: Adicione ao Catálogo

Edite o `SOFTWARE_CATALOG` no arquivo `main.py`:

```python
SOFTWARE_CATALOG = [
    # ... outros programas ...
    
    {
        "id": "meu_programa",           # ID único (sem espaços)
        "name": "Meu Programa Legal",   # Nome exibido na interface
        "filename": "meu_instalador.exe",  # Nome do arquivo em installers/
        "args": ["/VERYSILENT", "/NORESTART"],  # Argumentos silenciosos
        "is_express": False,            # True = aparece na instalação expressa
        "description": "Descrição do programa"  # Descrição opcional
    },
]
```

---

## 📦 Compilando o Executável

### Método Simples (Recomendado)

Execute o script de build:

```bash
build.bat
```

O executável será criado em `dist/AutoSetup_Empresarial.exe`

### Método Manual

```bash
pyinstaller --onefile --noconsole --add-data "installers;installers" main.py
```

### Método Avançado (Com Spec File)

```bash
pyinstaller AutoSetup_Empresarial.spec
```

---

## 🎨 Interface

O aplicativo possui 3 telas principais:

### Tela 1 - Home
- Botão de **Instalação Expressa** (programas essenciais)
- Botão de **Instalação Personalizada**

### Tela 2 - Seleção
- Lista de checkboxes com todos os programas
- Botões de "Selecionar Todos" e "Limpar Seleção"
- Badge "EXPRESS" nos programas padrão

### Tela 3 - Execução
- Barra de progresso em tempo real
- Console de logs com cores
- Indicadores de sucesso/erro por programa

---

## ⚙️ Catálogo Padrão

| Programa | Arquivo | Express |
|----------|---------|---------|
| Google Chrome | `ChromeSetup.exe` | ✅ |
| Adobe Reader DC | `AcroRdrDC.exe` | ✅ |
| 7-Zip | `7z_installer.exe` | ✅ |
| WinRAR | `winrar.exe` | ❌ |
| Node.js LTS | `node.msi` | ❌ |

---

## 🔧 Dicas Avançadas

### Executar como Administrador

Para instalações que requerem privilégios elevados, execute o programa como Administrador:

```bash
# Ou clique com botão direito > "Executar como administrador"
```

### Personalizar o Ícone

1. Coloque um arquivo `icon.ico` na raiz do projeto
2. Recompile com `build.bat`

### Adicionar Informações de Versão

Crie um arquivo `version_info.txt` seguindo o formato do PyInstaller para incluir metadados no executável.

---

## 🐛 Troubleshooting

### "Arquivo não encontrado"
- Verifique se o instalador está na pasta `installers/`
- Confirme que o `filename` no catálogo corresponde exatamente

### "Instalação falhou (código X)"
- Verifique se os switches estão corretos
- Alguns programas requerem execução como Administrador
- Código 3010 = sucesso com reinicialização pendente

### Interface não abre
- Certifique-se que CustomTkinter está instalado
- Verifique erros no console: `python main.py`

---

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

---

## 🤝 Contribuindo

Contribuições são bem-vindas! Sinta-se à vontade para:

1. Fazer um Fork do projeto
2. Criar uma Branch para sua feature (`git checkout -b feature/NovaFeature`)
3. Commit suas mudanças (`git commit -m 'Adiciona NovaFeature'`)
4. Push para a Branch (`git push origin feature/NovaFeature`)
5. Abrir um Pull Request

---

<p align="center">
  Feito com ❤️ para facilitar a vida do profissional de TI
</p>
