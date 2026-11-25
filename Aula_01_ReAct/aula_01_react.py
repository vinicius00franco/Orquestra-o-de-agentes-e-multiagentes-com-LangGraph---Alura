"""Aula 01 - Agente ReAct com Gemini.

Script Python convertido a partir de `Aula_01_ReAct.ipynb`, seguindo os
princípios KISS, YAGNI, DRY, Clean Code, Early Return e tipagem estrita.
"""

from __future__ import annotations

import argparse
import os
import re
from typing import Any

import google.generativeai as genai
from dotenv import load_dotenv

NOME_MODELO = "gemini-2.5-flash"

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

# Prompt de sistema que instrui o modelo a operar no ciclo ReAct.
PROMPT_REACT = """
Você funciona em um ciclo de Pensamento, Ação, Pausa e Observação.
Ao final do ciclo, você fornece uma Resposta.
Use "Pensamento" para descrever seu raciocínio.
Use "Ação" para executar ferramentas - e então retorne "PAUSA".
A "Observação" será o resultado da ação executada.
Ações disponíveis:
  - consultar_estoque: retorna a quantidade disponível de um item no inventário (ex: "consultar_estoque: teclado")
  - consultar_preco_produto: retorna o preço unitário de um produto (ex: "consultar_preco_produto: mouse gamer")
  - encontrar_produto_mais_caro: retorna o nome e o preço do produto mais caro no inventário (não requer argumentos)
  - calcular_valor_total_lista: calcula o valor total de uma lista de itens de compra. Recebe uma string com itens separados por vírgula (ex: "teclado, mouse gamer, monitor")

Exemplo:
Pergunta: Quantos monitores temos em estoque?
Pensamento: Devo consultar a ação consultar_estoque para saber a quantidade de monitores.
Ação: consultar_estoque: monitor
PAUSA

Observação: Temos 75 monitores em estoque.
Resposta: Há 75 monitores em estoque.

Exemplo:
Pergunta: Qual é o produto mais caro?
Pensamento: Preciso usar a ação encontrar_produto_mais_caro para descobrir qual produto tem o maior preço.
Ação: encontrar_produto_mais_caro
PAUSA

Observação: O produto mais caro é o(a) monitor com preço de R$ 999.90.
Resposta: O produto mais caro é o(a) monitor com preço de R$ 999.90.

Exemplo:
Pergunta: Quanto custa um teclado e um mouse gamer?
Pensamento: O usuário quer saber o valor total de vários itens. Devo usar a ação calcular_valor_total_lista com os itens "teclado, mouse gamer".
Ação: calcular_valor_total_lista: teclado, mouse gamer
PAUSA

Observação: O valor total dos itens encontrados é R$ 249.50.
Resposta: O valor total do teclado e do mouse gamer é R$ 249.50.
""".strip()


def configurar_ambiente() -> None:
    """Carrega variáveis de ambiente e inicializa o cliente do Gemini."""
    load_dotenv()

    # Aceita tanto GEMINI_API_KEY quanto GOOGLE_API_KEY para compatibilidade.
    chave_api = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if not chave_api:
        raise ValueError(
            "Chave de API não encontrada. Defina GEMINI_API_KEY ou GOOGLE_API_KEY no arquivo .env."
        )

    os.environ["GOOGLE_API_KEY"] = chave_api

    chave_tavily = os.getenv("TAVILY_API_KEY")
    if chave_tavily:
        os.environ["TAVILY_API_KEY"] = chave_tavily

    genai.configure(api_key=chave_api)


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


def executar_acao(nome_acao: str, argumento_acao: str) -> str:
    """Despacha a execução de uma ferramenta suportada pelo agente ReAct."""
    if nome_acao == "consultar_estoque":
        return consultar_estoque(argumento_acao)
    if nome_acao == "consultar_preco_produto":
        return consultar_preco_produto(argumento_acao)
    if nome_acao == "encontrar_produto_mais_caro":
        return buscar_produto_mais_caro()
    if nome_acao == "calcular_valor_total_lista":
        return calcular_valor_total_lista(argumento_acao)

    return (
        f"Erro: Ação '{nome_acao}' desconhecida. "
        "Verifique o prompt ou a implementação da ferramenta."
    )


def executar_agente_react_com_historico(
    pergunta: str,
    limite_iteracoes: int = 5,
    nome_modelo: str = NOME_MODELO,
) -> tuple[str, list[Any]]:
    """Executa o ciclo ReAct para uma pergunta e retorna a resposta final e o histórico."""
    modelo = genai.GenerativeModel(nome_modelo)
    conversa = modelo.start_chat(history=[])

    # Envia as instruções do ciclo ReAct antes da primeira pergunta do usuário.
    conversa.send_message(PROMPT_REACT)
    prompt_atual = pergunta

    for iteracao in range(1, limite_iteracoes + 1):
        resposta_modelo = conversa.send_message(prompt_atual)
        texto_resposta = str(resposta_modelo.text).strip()

        print(f"\n--- Iteração {iteracao} ---")
        print(f"Modelo pensou/respondeu:\n{texto_resposta}\n")

        # Verifica primeiro se o modelo já produziu a resposta final.
        correspondencia_final = re.search(r"Resposta:\s*(.*)", texto_resposta, re.DOTALL)
        if correspondencia_final:
            return correspondencia_final.group(1).strip(), list(conversa.history)

        # Caso contrário, tenta extrair o nome da ferramenta e o argumento opcional.
        correspondencia_acao = re.search(r"Ação:\s*(\w+)(?::\s*([^\n]*))?", texto_resposta)
        if not correspondencia_acao:
            return (
                f"Erro: O agente não conseguiu extrair uma Ação ou Resposta final "
                f"após {iteracao} iterações. Última resposta do modelo: {texto_resposta}",
                list(conversa.history),
            )

        nome_acao = correspondencia_acao.group(1).strip()
        argumento_bruto = correspondencia_acao.group(2)
        argumento_acao = argumento_bruto.strip() if argumento_bruto is not None else ""

        observacao_acao = executar_acao(nome_acao, argumento_acao)
        prompt_atual = f"Observação: {observacao_acao}"

        print(f"Executou ação: {nome_acao} com argumento '{argumento_acao}'")
        print(f"Observação: {observacao_acao}\n")

    return (
        "Erro: Limite máximo de iterações atingido sem uma resposta final do agente.",
        list(conversa.history),
    )


def executar_agente_react(
    pergunta: str,
    limite_iteracoes: int = 5,
    nome_modelo: str = NOME_MODELO,
) -> str:
    """Executa o ciclo ReAct para uma pergunta e retorna apenas a resposta final."""
    resposta_final, _ = executar_agente_react_com_historico(
        pergunta=pergunta,
        limite_iteracoes=limite_iteracoes,
        nome_modelo=nome_modelo,
    )
    return resposta_final


def executar_exemplos() -> None:
    """Executa o conjunto de perguntas de demonstração da Aula 01."""
    perguntas_exemplo = [
        "Quantos teclados temos em estoque?",
        "Qual o preço de um headset?",
        "Temos cadeiras em estoque?",
        "Qual é o produto mais caro?",
        "Qual o valor de um teclado, uma impressora e uma webcam?",
    ]

    print("--- Começando as Interações com o Agente ReAct ---")
    for indice, pergunta in enumerate(perguntas_exemplo, start=1):
        print(f"\n**Interação {indice}: {pergunta}**")
        resposta = executar_agente_react(pergunta)
        print(f"\n**RESPOSTA FINAL DO AGENTE {indice}:** {resposta}\n")

        if indice < len(perguntas_exemplo):
            print("\n" + "=" * 80 + "\n")

    print("\n--- Fim das Interações ---")


def iniciar_conversacao_com_agente() -> None:
    """Inicia um loop interativo no terminal para conversar com o agente."""
    print("--- Agente de Inventário Interativo ---")
    print("Digite sua pergunta sobre o inventário, ou digite 'sair' para encerrar.")
    print("-" * 50)

    while True:
        pergunta_usuario = input("\nVocê: ")

        if pergunta_usuario.lower().strip() == "sair":
            print("Encerrando a conversa. Até logo!")
            break

        print("\nAgente: Processando...")
        try:
            resposta_agente = executar_agente_react(pergunta_usuario)
            print(f"\nAgente: {resposta_agente}")
        except Exception as erro:
            print(f"\nAgente: Ocorreu um erro ao processar sua pergunta: {erro}")
            print("Por favor, tente novamente ou digite 'sair'.")


def ler_argumentos_cli() -> argparse.Namespace:
    """Analisa os argumentos recebidos via linha de comando."""
    analisador = argparse.ArgumentParser(description="Agente ReAct de inventário (Aula 01).")
    analisador.add_argument(
        "--exemplos",
        action="store_true",
        help="Executa as perguntas de exemplo da aula em vez do modo interativo.",
    )
    return analisador.parse_args()


def principal() -> None:
    """Ponto de entrada principal do script."""
    argumentos = ler_argumentos_cli()
    configurar_ambiente()

    if argumentos.exemplos:
        executar_exemplos()
        return

    iniciar_conversacao_com_agente()


if __name__ == "__main__":
    principal()
