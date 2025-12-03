# 🤝 Guia de Contribuição

Obrigado pelo interesse em contribuir com o **AutoSetup Empresarial**! Este documento fornece diretrizes para contribuir com o projeto.

## 📋 Índice

- [Código de Conduta](#-código-de-conduta)
- [Como Contribuir](#-como-contribuir)
- [Reportando Bugs](#-reportando-bugs)
- [Sugerindo Melhorias](#-sugerindo-melhorias)
- [Pull Requests](#-pull-requests)
- [Padrões de Código](#-padrões-de-código)
- [Estrutura do Projeto](#-estrutura-do-projeto)

---

## 📜 Código de Conduta

Este projeto segue um código de conduta para garantir um ambiente acolhedor para todos. Por favor:

- ✅ Seja respeitoso e inclusivo
- ✅ Aceite críticas construtivas
- ✅ Foque no que é melhor para a comunidade
- ❌ Não use linguagem ofensiva ou discriminatória
- ❌ Não faça ataques pessoais

---

## 🚀 Como Contribuir

### 1. Faça um Fork

Clique no botão "Fork" no topo da página do repositório.

### 2. Clone seu Fork

```bash
git clone https://github.com/SEU_USUARIO/AutoSetup-Empresarial.git
cd AutoSetup-Empresarial
```

### 3. Configure o Upstream

```bash
git remote add upstream https://github.com/SamuelElse/AutoSetup-Empresarial.git
```

### 4. Crie uma Branch

```bash
# Para nova funcionalidade
git checkout -b feature/minha-funcionalidade

# Para correção de bug
git checkout -b fix/descricao-do-bug

# Para documentação
git checkout -b docs/melhoria-documentacao
```

### 5. Faça suas Alterações

Implemente sua contribuição seguindo os [padrões de código](#-padrões-de-código).

### 6. Commit suas Mudanças

```bash
git add .
git commit -m "feat: adiciona funcionalidade X"
```

**Convenção de commits:**
- `feat:` - Nova funcionalidade
- `fix:` - Correção de bug
- `docs:` - Documentação
- `style:` - Formatação (sem alteração de código)
- `refactor:` - Refatoração de código
- `test:` - Adição de testes
- `chore:` - Tarefas de manutenção

### 7. Push para seu Fork

```bash
git push origin feature/minha-funcionalidade
```

### 8. Abra um Pull Request

Vá até o repositório original e clique em "New Pull Request".

---

## 🐛 Reportando Bugs

Encontrou um bug? Abra uma [Issue](https://github.com/SamuelElse/AutoSetup-Empresarial/issues/new) incluindo:

### Template de Bug Report

```markdown
## Descrição do Bug
Uma descrição clara do problema.

## Passos para Reproduzir
1. Vá para '...'
2. Clique em '...'
3. Role até '...'
4. Veja o erro

## Comportamento Esperado
O que deveria acontecer.

## Comportamento Atual
O que realmente acontece.

## Screenshots
Se aplicável, adicione capturas de tela.

## Ambiente
- Windows: [ex: 10, 11]
- Python: [ex: 3.10]
- Versão do App: [ex: 1.0]

## Informações Adicionais
Qualquer outro contexto relevante.
```

---

## 💡 Sugerindo Melhorias

Tem uma ideia? Adoraríamos ouvir! Abra uma Issue com:

### Template de Feature Request

```markdown
## Descrição da Funcionalidade
Uma descrição clara da funcionalidade desejada.

## Problema que Resolve
Qual problema esta funcionalidade resolveria?

## Solução Proposta
Como você imagina a implementação?

## Alternativas Consideradas
Outras soluções que você considerou.

## Contexto Adicional
Screenshots, mockups ou referências.
```

---

## 🔀 Pull Requests

### Checklist antes de submeter

- [ ] Código segue os padrões do projeto
- [ ] Testei localmente e funciona
- [ ] Atualizei a documentação se necessário
- [ ] Commits seguem a convenção
- [ ] Branch está atualizada com a main

### Template de PR

```markdown
## Descrição
Breve descrição das mudanças.

## Tipo de Mudança
- [ ] Bug fix
- [ ] Nova funcionalidade
- [ ] Documentação
- [ ] Refatoração

## Como Testar
Passos para testar as mudanças.

## Screenshots (se aplicável)
Capturas de tela das mudanças visuais.

## Checklist
- [ ] Testei localmente
- [ ] Documentação atualizada
- [ ] Código comentado onde necessário
```

---

## 📝 Padrões de Código

### Python

```python
# Use docstrings para funções e classes
def minha_funcao(parametro: str) -> bool:
    """
    Descrição breve da função.
    
    Args:
        parametro: Descrição do parâmetro
        
    Returns:
        Descrição do retorno
    """
    pass

# Use type hints
def processar_dados(dados: List[Dict]) -> Optional[str]:
    pass

# Constantes em UPPER_CASE
MAX_TENTATIVAS = 3
TIMEOUT_PADRAO = 30

# Classes em PascalCase
class MinhaClasse:
    pass

# Funções e variáveis em snake_case
def minha_funcao():
    minha_variavel = 10
```

### Formatação

- Indentação: 4 espaços
- Linha máxima: 100 caracteres
- Encoding: UTF-8
- Final de linha: LF (Unix)

### Estrutura de Arquivos

```python
#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Descrição do módulo.
"""

# Imports da biblioteca padrão
import os
import sys

# Imports de terceiros
import customtkinter as ctk

# Imports locais
from .utils import helper

# Constantes
CONSTANTE = "valor"

# Classes e funções
class MinhaClasse:
    pass

# Código de execução
if __name__ == "__main__":
    main()
```

---

## 📁 Estrutura do Projeto

```
AutoSetup-Empresarial/
├── main.py              # Aplicação principal
│   ├── Elevação de privilégios
│   ├── Resource paths
│   ├── Download manager
│   ├── Catálogo de software
│   ├── Detecção de argumentos
│   ├── Gerenciador de catálogo
│   ├── Smart runner
│   └── Interface gráfica (CustomTkinter)
│
├── build.py             # Script de compilação
├── requirements.txt     # Dependências
├── README.md            # Documentação principal
├── CONTRIBUTING.md      # Este arquivo
├── LICENSE              # Licença MIT
└── installers/          # Pasta para instaladores
```

### Principais Classes

| Classe | Responsabilidade |
|--------|------------------|
| `AutoSetupApp` | Interface gráfica principal |
| `CatalogManager` | Gerenciamento do catálogo JSON |
| `InstallResult` | Resultado de instalações |
| `DownloadResult` | Resultado de downloads |

### Fluxo do Aplicativo

```
main.py
    ↓
ensure_admin()      → Solicita elevação se necessário
    ↓
AutoSetupApp()      → Inicializa interface
    ↓
show_home_screen()  → Tela inicial
    ↓
[Ação do usuário]
    ↓
Instalação Expressa  →  show_execution_screen()  →  run_installations()
       ou
Personalizada        →  show_selection_screen()  →  show_execution_screen()
       ou
Gerenciar            →  show_manage_screen()     →  add/edit/remove
```

---

## 🧪 Testando suas Alterações

### Teste Manual

```bash
# Execute o aplicativo
python main.py

# Teste o build
python build.py --console
```

### Checklist de Testes

- [ ] Instalação expressa funciona
- [ ] Instalação personalizada funciona
- [ ] Adicionar programa local funciona
- [ ] Adicionar programa da nuvem funciona
- [ ] Editar programa funciona
- [ ] Remover programa funciona
- [ ] Build gera executável válido

---

## 📞 Dúvidas?

Se tiver alguma dúvida, sinta-se à vontade para:

1. Abrir uma [Issue](https://github.com/SamuelElse/AutoSetup-Empresarial/issues)
2. Iniciar uma [Discussion](https://github.com/SamuelElse/AutoSetup-Empresarial/discussions)

---

<div align="center">

**Obrigado por contribuir! 🎉**

</div>
