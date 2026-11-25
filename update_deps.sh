#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="/Users/viniciusfrancosilva/Downloads/ESTUDO/orquestrando-agentes-e-multi-agentes"
VENV_PIP="${ROOT_DIR}/.venv/bin/pip"
REQ_FILE="${ROOT_DIR}/requirements.txt"

echo "[$(date '+%Y-%m-%d %H:%M:%S')] Iniciando atualização automática da .venv compartilhada..."
"${VENV_PIP}" install --upgrade pip
"${VENV_PIP}" install --upgrade -e "${ROOT_DIR}[dev]"

if [[ -f "${REQ_FILE}" ]] && grep -qE '^\s*[^#\s]' "${REQ_FILE}"; then
    "${VENV_PIP}" install --upgrade -r "${REQ_FILE}"
fi

echo "[$(date '+%Y-%m-%d %H:%M:%S')] Atualização concluída com sucesso."
