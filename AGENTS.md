# Diretrizes para Agentes (AGENTS.md)

Este documento define os padrões de codificação, arquitetura e organização que devem ser seguidos por todos os agentes e colaboradores neste repositório.

## 1. Princípios de Engenharia

- **KISS (Keep It Simple, Stupid):** Prefira a solução mais simples, legível e direta que resolve o problema. Evite abstrações desnecessárias ou complexidade acidental.
- **YAGNI (You Aren't Gonna Need It):** Implemente apenas o que é necessário agora. Não crie código, parâmetros, camadas ou generalizações especulativas para "uso futuro".
- **DRY (Don't Repeat Yourself):** Evite duplicação de lógica, constantes e regras de negócio. Centralize comportamentos repetidos em funções ou constantes reutilizáveis.
- **Clean Code:** Funções pequenas e coesas com responsabilidade única, fluxo de leitura linear, sem código morto e sem efeitos colaterais ocultos.

## 2. Estilo e Fluxo de Controle

- **Sem `if / else` — use Early Return (Guard Clauses):**
  - Sempre valide condições de saída, erro ou casos especiais primeiro e retorne cedo.
  - Evite blocos `else` após `return`, `continue`, `break` ou `raise` para reduzir indentação e manter o "caminho feliz" no nível principal.

```python
# Ruim
def consultar_estoque(item: str) -> str:
    if item in ESTOQUE:
        return f"Temos {ESTOQUE[item]} unidades."
    else:
        return "Item não encontrado."

# Bom (Early Return)
def consultar_estoque(item: str) -> str:
    if item not in ESTOQUE:
        return "Item não encontrado."

    return f"Temos {ESTOQUE[item]} unidades."
```

## 3. Nomenclatura em Português

- **Variáveis, funções, parâmetros, constantes e classes** devem ter nomes **claros, descritivos e lógicos em português**.
- Evite abreviações crípticas (`tmp`, `res`, `x`, `fn`) ou mistura desnecessária de inglês e português.
- Exemplos:
  - Funções: `configurar_ambiente`, `executar_agente_react`, `calcular_valor_total_lista`, `buscar_produto_mais_caro`.
  - Variáveis: `item_normalizado`, `lista_itens`, `resposta_final`, `limite_iteracoes`.
  - Constantes: `ESTOQUE_INVENTARIO`, `PRECOS_INVENTARIO`, `NOME_MODELO`.

## 4. Comentários e Documentação

- Escreva **docstrings** objetivas em módulos, classes e funções.
- Adicione **comentários ao longo do código** explicando etapas importantes do fluxo, decisões de negócio e o *porquê* de regras não óbvias (sem repetir literalmente o que a linha de código já diz).

## 5. Ambiente, Tipagem e Qualidade

- **Ambiente virtual compartilhado:** Use sempre a `.venv` da raiz do repositório (compartilhada entre todas as pastas de aulas).
- **Dependências:** Adicione novas bibliotecas em `pyproject.toml` ou `requirements.txt` na raiz (o `launchd` atualiza a `.venv` automaticamente).
- **Validação obrigatória antes de concluir qualquer alteração:**
  - `ruff check` (lint)
  - `ruff format --check` (formatação)
  - `mypy` em modo `strict` (tipagem estática)
  - `python -m py_compile` (verificação de compilação)
- **Commits:** Utilize **Conventional Commits** em commits pequenos e atômicos (`feat`, `fix`, `refactor`, `build`, `ci`, `docs`, `chore`).
