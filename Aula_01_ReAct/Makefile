.PHONY: check format run examples

VENV := ../.venv
VENV_PYTHON := $(VENV)/bin/python
RUFF := $(VENV)/bin/ruff
MYPY := $(VENV)/bin/mypy

check:
	$(RUFF) check --config ../pyproject.toml aula_01_react.py
	$(RUFF) format --config ../pyproject.toml --check aula_01_react.py
	$(MYPY) --config-file ../pyproject.toml aula_01_react.py
	$(VENV_PYTHON) -m py_compile aula_01_react.py

format:
	$(RUFF) check --config ../pyproject.toml --fix aula_01_react.py
	$(RUFF) format --config ../pyproject.toml aula_01_react.py

run:
	$(VENV_PYTHON) aula_01_react.py

examples:
	$(VENV_PYTHON) aula_01_react.py --exemplos
