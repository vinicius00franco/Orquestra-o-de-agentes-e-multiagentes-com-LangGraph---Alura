"""Adaptador de infraestrutura para o provedor Google Gemini."""

from __future__ import annotations

import os
from typing import Any

import google.generativeai as genai
from dotenv import load_dotenv

NOME_MODELO_PADRAO = "gemini-2.5-flash"


def configurar_ambiente_gemini() -> None:
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


class ConversaGemini:
    """Implementação concreta de conversa usando o SDK do Google Gemini."""

    def __init__(self, nome_modelo: str = NOME_MODELO_PADRAO) -> None:
        """Inicializa uma nova sessão de chat com o modelo informado."""
        modelo = genai.GenerativeModel(nome_modelo)
        self._conversa = modelo.start_chat(history=[])

    def enviar_mensagem(self, mensagem: str) -> str:
        """Envia uma mensagem ao Gemini e retorna o texto da resposta."""
        resposta = self._conversa.send_message(mensagem)
        return str(resposta.text)

    def obter_historico(self) -> list[Any]:
        """Retorna o histórico acumulado da sessão no Gemini."""
        return list(self._conversa.history)
