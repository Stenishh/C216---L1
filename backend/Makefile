PYTHON := python
POETRY := $(PYTHON) -m poetry
APP := src.main:app
HOST := 127.0.0.1
PORT := 8000

.PHONY: help install run test clean

help: ## Exibe os comandos disponiveis
	@echo "Comandos disponiveis:"
	@$(PYTHON) -c "import re; from pathlib import Path; text = Path('Makefile').read_text(); [print(f'  {name:<12} {description}') for name, description in re.findall(r'^([a-zA-Z_-]+):.*?## (.*)$$', text, re.MULTILINE)]"

install: ## Instala as dependencias do projeto
	$(POETRY) install

run: ## Inicia a API em modo de desenvolvimento
	$(POETRY) run uvicorn $(APP) --host $(HOST) --port $(PORT) --reload

test: ## Executa os testes
	$(POETRY) run pytest

clean: ## Remove caches gerados pelo Python e pelo pytest
	$(PYTHON) -c "import shutil; from pathlib import Path; [shutil.rmtree(path, ignore_errors=True) for pattern in ('__pycache__', '.pytest_cache') for path in Path('.').rglob(pattern)]"
