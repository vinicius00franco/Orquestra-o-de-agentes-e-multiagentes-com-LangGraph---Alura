.PHONY: check format run examples

VENV := ../.venv
VENV_PYTHON := $(VENV)/bin/python
RUFF := $(VENV)/bin/ruff
MYPY := $(VENV)/bin/mypy
TARGETS := aula_01_react.py dominio aplicacao infraestrutura

check:
	$(RUFF) check --config ../pyproject.toml $(TARGETS)
	$(RUFF) format --config ../pyproject.toml --check $(TARGETS)
	$(MYPY) --config-file ../pyproject.toml $(TARGETS)
	$(VENV_PYTHON) -m compileall -q $(TARGETS)

format:
	$(RUFF) check --config ../pyproject.toml --fix $(TARGETS)
	$(RUFF) format --config ../pyproject.toml $(TARGETS)

run:
	$(VENV_PYTHON) aula_01_react.py

examples:
	$(VENV_PYTHON) aula_01_react.py --exemplos
