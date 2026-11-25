"""Caso de uso do agente ReAct (camada de Aplicação).

Orquestra o ciclo Pensamento -> Ação -> Observação -> Resposta sem depender
diretamente do SDK concreto do modelo de linguagem.
"""

from __future__ import annotations

import re
from typing import Any, Protocol

from dominio.inventario import (
    buscar_produto_mais_caro,
    calcular_valor_total_lista,
    consultar_estoque,
    consultar_preco_produto,
)

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


class ConversaLLM(Protocol):
    """Contrato mínimo de uma sessão de conversa com um modelo de linguagem."""

    def enviar_mensagem(self, mensagem: str) -> str:
        """Envia uma mensagem ao modelo e retorna o texto da resposta."""
        ...

    def obter_historico(self) -> list[Any]:
        """Retorna o histórico acumulado da conversa."""
        ...


def executar_acao(nome_acao: str, argumento_acao: str) -> str:
    """Despacha a execução de uma ferramenta de domínio suportada pelo agente."""
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
    conversa: ConversaLLM,
    limite_iteracoes: int = 5,
) -> tuple[str, list[Any]]:
    """Executa o ciclo ReAct para uma pergunta e retorna a resposta final e o histórico."""
    # Envia as instruções do ciclo ReAct antes da primeira pergunta do usuário.
    conversa.enviar_mensagem(PROMPT_REACT)
    prompt_atual = pergunta

    for iteracao in range(1, limite_iteracoes + 1):
        texto_resposta = conversa.enviar_mensagem(prompt_atual).strip()

        print(f"\n--- Iteração {iteracao} ---")
        print(f"Modelo pensou/respondeu:\n{texto_resposta}\n")

        # Verifica primeiro se o modelo já produziu a resposta final.
        correspondencia_final = re.search(r"Resposta:\s*(.*)", texto_resposta, re.DOTALL)
        if correspondencia_final:
            return correspondencia_final.group(1).strip(), conversa.obter_historico()

        # Caso contrário, tenta extrair o nome da ferramenta e o argumento opcional.
        correspondencia_acao = re.search(r"Ação:\s*(\w+)(?::\s*([^\n]*))?", texto_resposta)
        if not correspondencia_acao:
            return (
                f"Erro: O agente não conseguiu extrair uma Ação ou Resposta final "
                f"após {iteracao} iterações. Última resposta do modelo: {texto_resposta}",
                conversa.obter_historico(),
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
        conversa.obter_historico(),
    )


def executar_agente_react(
    pergunta: str,
    conversa: ConversaLLM,
    limite_iteracoes: int = 5,
) -> str:
    """Executa o ciclo ReAct para uma pergunta e retorna apenas a resposta final."""
    resposta_final, _ = executar_agente_react_com_historico(
        pergunta=pergunta,
        conversa=conversa,
        limite_iteracoes=limite_iteracoes,
    )
    return resposta_final
