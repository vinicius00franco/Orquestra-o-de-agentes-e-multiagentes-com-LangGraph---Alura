"""Regras de negócio puras do inventário (camada de Domínio).

Não possui dependências externas de frameworks ou provedores de IA.
"""

from __future__ import annotations

# Catálogo simulado de quantidades disponíveis no inventário.
ESTOQUE_INVENTARIO: dict[str, int] = {
    "monitor": 75,
    "teclado": 120,
    "mouse gamer": 80,
    "webcam": 40,
    "headset": 60,
    "impressora": 15,
}

# Catálogo simulado de preços unitários em reais (R$).
PRECOS_INVENTARIO: dict[str, float] = {
    "monitor": 999.90,
    "teclado": 150.00,
    "mouse gamer": 99.50,
    "webcam": 120.00,
    "headset": 180.00,
    "impressora": 750.00,
}


def consultar_estoque(item: str) -> str:
    """Retorna a quantidade disponível de um item no inventário."""
    item_normalizado = item.lower().strip()
    if item_normalizado not in ESTOQUE_INVENTARIO:
        return f"Item '{item_normalizado}' não encontrado no inventário."

    quantidade = ESTOQUE_INVENTARIO[item_normalizado]
    return f"Temos {quantidade} {item_normalizado}s em estoque."


def consultar_preco_produto(produto: str) -> str:
    """Retorna o preço unitário de um produto cadastrado."""
    produto_normalizado = produto.lower().strip()
    if produto_normalizado not in PRECOS_INVENTARIO:
        return f"Produto '{produto_normalizado}' não encontrado na lista de preços."

    preco = PRECOS_INVENTARIO[produto_normalizado]
    return f"O preço de um(a) {produto_normalizado} é R$ {preco:.2f}."


def buscar_produto_mais_caro() -> str:
    """Retorna o nome e o preço do produto mais caro no inventário."""
    if not PRECOS_INVENTARIO:
        return "Nenhum produto encontrado na lista de preços para comparação."

    nome_produto_mais_caro, valor_produto_mais_caro = max(
        PRECOS_INVENTARIO.items(),
        key=lambda par_produto: par_produto[1],
    )
    return (
        f"O produto mais caro é o(a) {nome_produto_mais_caro} "
        f"com preço de R$ {valor_produto_mais_caro:.2f}."
    )


def calcular_valor_total_lista(lista_itens: str) -> str:
    """Calcula o valor total de uma lista de itens separados por vírgula."""
    itens_processados = [item.strip().lower() for item in lista_itens.split(",") if item.strip()]

    valor_total = 0.0
    itens_nao_encontrados: list[str] = []

    for item in itens_processados:
        if item not in PRECOS_INVENTARIO:
            itens_nao_encontrados.append(item)
            continue

        valor_total += PRECOS_INVENTARIO[item]

    resposta = f"O valor total dos itens encontrados é R$ {valor_total:.2f}."
    if not itens_nao_encontrados:
        return resposta

    itens_faltantes = ", ".join(itens_nao_encontrados)
    return (
        f"{resposta} Os seguintes itens não foram encontrados e não foram incluídos "
        f"no cálculo: {itens_faltantes}."
    )
