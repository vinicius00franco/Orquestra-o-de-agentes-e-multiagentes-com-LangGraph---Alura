"""Aula 01 - Agente ReAct com Gemini.

Script Python convertido a partir de `Aula_01_ReAct.ipynb`, com tipagem estrita
para validação com `mypy` e lint/formatação com `ruff`.
"""

from __future__ import annotations

import argparse
import os
import re
from typing import Any, TypedDict

import google.generativeai as genai
from dotenv import load_dotenv

MODEL_NAME = "gemini-2.5-flash"

ESTOQUE_INVENTARIO: dict[str, int] = {
    "monitor": 75,
    "teclado": 120,
    "mouse gamer": 80,
    "webcam": 40,
    "headset": 60,
    "impressora": 15,
}

PRECOS_INVENTARIO: dict[str, float] = {
    "monitor": 999.90,
    "teclado": 150.00,
    "mouse gamer": 99.50,
    "webcam": 120.00,
    "headset": 180.00,
    "impressora": 750.00,
}

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


class EstadoAgente(TypedDict):
    """Representa o estado do agente ReAct."""

    pergunta: str
    historico: list[str]
    acao_pendente: str
    resposta_final: str


def configurar_ambiente() -> None:
    """Carrega variáveis de ambiente e configura o cliente do Gemini."""
    load_dotenv()

    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError(
            "Chave de API não encontrada. Defina GEMINI_API_KEY ou GOOGLE_API_KEY no arquivo .env."
        )

    os.environ["GOOGLE_API_KEY"] = api_key

    tavily_key = os.getenv("TAVILY_API_KEY")
    if tavily_key:
        os.environ["TAVILY_API_KEY"] = tavily_key

    genai.configure(api_key=api_key)


def consultar_estoque(item: str) -> str:
    """Simula a consulta de estoque de um item no inventário."""
    item_normalizado = item.lower().strip()
    if item_normalizado in ESTOQUE_INVENTARIO:
        quantidade = ESTOQUE_INVENTARIO[item_normalizado]
        return f"Temos {quantidade} {item_normalizado}s em estoque."
    return f"Item '{item_normalizado}' não encontrado no inventário."


def consultar_preco_produto(produto: str) -> str:
    """Simula a consulta do preço unitário de um produto."""
    produto_normalizado = produto.lower().strip()
    if produto_normalizado in PRECOS_INVENTARIO:
        preco = PRECOS_INVENTARIO[produto_normalizado]
        return f"O preço de um(a) {produto_normalizado} é R$ {preco:.2f}."
    return f"Produto '{produto_normalizado}' não encontrado na lista de preços."


def ferramenta_encontrar_produto_mais_caro() -> str:
    """Retorna o nome e o preço do produto mais caro no inventário."""
    if not PRECOS_INVENTARIO:
        return "Nenhum produto encontrado na lista de preços para comparação."

    nome_produto_mais_caro, valor_produto_mais_caro = max(
        PRECOS_INVENTARIO.items(),
        key=lambda item: item[1],
    )
    return (
        f"O produto mais caro é o(a) {nome_produto_mais_caro} "
        f"com preço de R$ {valor_produto_mais_caro:.2f}."
    )


def ferramenta_calcular_valor_total_lista(lista_itens: str) -> str:
    """Calcula o valor total de uma lista de itens separados por vírgula."""
    itens_processados = [item.strip().lower() for item in lista_itens.split(",") if item.strip()]

    valor_total = 0.0
    itens_nao_encontrados: list[str] = []

    for item in itens_processados:
        if item in PRECOS_INVENTARIO:
            valor_total += PRECOS_INVENTARIO[item]
        else:
            itens_nao_encontrados.append(item)

    resposta = f"O valor total dos itens encontrados é R$ {valor_total:.2f}."
    if itens_nao_encontrados:
        resposta += (
            " Os seguintes itens não foram encontrados e não foram incluídos no cálculo: "
            f"{', '.join(itens_nao_encontrados)}."
        )
    return resposta


def executar_acao(action_name: str, action_arg: str) -> str:
    """Despacha a execução de uma ferramenta suportada pelo agente ReAct."""
    if action_name == "consultar_estoque":
        return consultar_estoque(action_arg)
    if action_name == "consultar_preco_produto":
        return consultar_preco_produto(action_arg)
    if action_name == "encontrar_produto_mais_caro":
        return ferramenta_encontrar_produto_mais_caro()
    if action_name == "calcular_valor_total_lista":
        return ferramenta_calcular_valor_total_lista(action_arg)
    return (
        f"Erro: Ação '{action_name}' desconhecida. "
        "Verifique o prompt ou a implementação da ferramenta."
    )


def run_react_agent_with_history(
    pergunta: str,
    max_iterations: int = 5,
    model_name: str = MODEL_NAME,
) -> tuple[str, list[Any]]:
    """Executa o ciclo ReAct para uma pergunta e retorna a resposta final e o histórico."""
    model = genai.GenerativeModel(model_name)
    chat = model.start_chat(history=[])
    chat.send_message(PROMPT_REACT)

    current_prompt = pergunta

    for i in range(max_iterations):
        response = chat.send_message(current_prompt)
        response_text = str(response.text).strip()

        print(f"\n--- Iteração {i + 1} ---")
        print(f"Modelo pensou/respondeu:\n{response_text}\n")

        response_match_final = re.search(r"Resposta:\s*(.*)", response_text, re.DOTALL)
        if response_match_final:
            return response_match_final.group(1).strip(), list(chat.history)

        match = re.search(r"Ação:\s*(\w+)(?::\s*([^\n]*))?", response_text)
        if match:
            action_name = match.group(1).strip()
            action_arg = match.group(2).strip() if match.group(2) is not None else ""

            observacao_da_acao = executar_acao(action_name, action_arg)
            current_prompt = f"Observação: {observacao_da_acao}"

            print(f"Executou ação: {action_name} com argumento '{action_arg}'")
            print(f"Observação: {observacao_da_acao}\n")
        else:
            return (
                f"Erro: O agente não conseguiu extrair uma Ação ou Resposta final "
                f"após {i + 1} iterações. Última resposta do modelo: {response_text}",
                list(chat.history),
            )

    return (
        "Erro: Limite máximo de iterações atingido sem uma resposta final do agente.",
        list(chat.history),
    )


def run_react_agent(
    pergunta: str,
    max_iterations: int = 5,
    model_name: str = MODEL_NAME,
) -> str:
    """Executa o ciclo ReAct para uma dada pergunta usando o modelo Gemini."""
    resposta, _ = run_react_agent_with_history(
        pergunta=pergunta,
        max_iterations=max_iterations,
        model_name=model_name,
    )
    return resposta


def executar_exemplos() -> None:
    """Executa o conjunto de perguntas de demonstração da Aula 01."""
    perguntas = [
        "Quantos teclados temos em estoque?",
        "Qual o preço de um headset?",
        "Temos cadeiras em estoque?",
        "Qual é o produto mais caro?",
        "Qual o valor de um teclado, uma impressora e uma webcam?",
    ]

    print("--- Começando as Interações com o Agente ReAct ---")
    for indice, pergunta in enumerate(perguntas, start=1):
        print(f"\n**Interação {indice}: {pergunta}**")
        resposta = run_react_agent(pergunta)
        print(f"\n**RESPOSTA FINAL DO AGENTE {indice}:** {resposta}\n")
        if indice < len(perguntas):
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
            resposta_agente = run_react_agent(pergunta_usuario)
            print(f"\nAgente: {resposta_agente}")
        except Exception as exc:
            print(f"\nAgente: Ocorreu um erro ao processar sua pergunta: {exc}")
            print("Por favor, tente novamente ou digite 'sair'.")


def parse_args() -> argparse.Namespace:
    """Analisa argumentos de linha de comando."""
    parser = argparse.ArgumentParser(description="Agente ReAct de inventário (Aula 01).")
    parser.add_argument(
        "--exemplos",
        action="store_true",
        help="Executa as perguntas de exemplo da aula em vez do modo interativo.",
    )
    return parser.parse_args()


def main() -> None:
    """Ponto de entrada principal do script."""
    args = parse_args()
    configurar_ambiente()

    if args.exemplos:
        executar_exemplos()
    else:
        iniciar_conversacao_com_agente()


if __name__ == "__main__":
    main()
