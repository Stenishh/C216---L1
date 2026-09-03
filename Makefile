BACKEND_DIR := backend
POETRY ?= poetry
APP ?= src.main:app
HOST ?= 127.0.0.1
PORT ?= 8000

.DEFAULT_GOAL := help

.PHONY: help install run test clean

help: ## Exibe os comandos disponíveis
	@echo "Comandos disponíveis:"
	@awk 'BEGIN {FS = ":.*## "} /^[a-zA-Z_-]+:.*## / {printf "  %-12s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

install: ## Instala as dependências do backend
	cd $(BACKEND_DIR) && $(POETRY) install

run: ## Inicia a API em modo de desenvolvimento
	cd $(BACKEND_DIR) && $(POETRY) run uvicorn $(APP) --host $(HOST) --port $(PORT) --reload

test: ## Executa os testes do backend
	cd $(BACKEND_DIR) && $(POETRY) run pytest

clean: ## Remove os caches gerados no backend
	find $(BACKEND_DIR) -type d \( -name '__pycache__' -o -name '.pytest_cache' \) -prune -exec rm -rf {} +
