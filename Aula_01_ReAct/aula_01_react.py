"""Ponto de entrada CLI do Agente ReAct (Aula 01).

Conecta as camadas de Infraestrutura, Aplicação e Domínio seguindo
Clean Architecture com simplicidade (KISS).
"""

from __future__ import annotations

import argparse

from aplicacao.agente_react import executar_agente_react
from infraestrutura.cliente_gemini import ConversaGemini, configurar_ambiente_gemini


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
        conversa = ConversaGemini()
        resposta = executar_agente_react(pergunta=pergunta, conversa=conversa)
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
            conversa = ConversaGemini()
            resposta_agente = executar_agente_react(
                pergunta=pergunta_usuario,
                conversa=conversa,
            )
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
    configurar_ambiente_gemini()

    if argumentos.exemplos:
        executar_exemplos()
        return

    iniciar_conversacao_com_agente()


if __name__ == "__main__":
    principal()
