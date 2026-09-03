BACKEND_DIR := backend
POETRY ?= poetry
COMPOSE ?= $(shell docker compose version >/dev/null 2>&1 && echo docker compose || echo docker-compose)
APP ?= src.main:app
HOST ?= 127.0.0.1
PORT ?= 8000
BACKEND_URL ?= http://localhost:$(PORT)
POSTGRES_USER ?= c216
POSTGRES_DB ?= c216

.DEFAULT_GOAL := help

.PHONY: help install run test clean docker-build docker-up docker-down \
	docker-restart docker-logs docker-status db-shell health

help: ## Exibe os comandos disponíveis
	@echo "Comandos disponíveis:"
	@awk 'BEGIN {FS = ":.*## "} /^[a-zA-Z_-]+:.*## / {printf "  %-16s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

install: ## Instala as dependências do backend
	cd $(BACKEND_DIR) && $(POETRY) install

run: ## Inicia a API em modo de desenvolvimento
	cd $(BACKEND_DIR) && $(POETRY) run uvicorn $(APP) --host $(HOST) --port $(PORT) --reload

test: ## Executa os testes do backend
	cd $(BACKEND_DIR) && $(POETRY) run pytest

clean: ## Remove os caches gerados no backend
	find $(BACKEND_DIR) -type d \( -name '__pycache__' -o -name '.pytest_cache' \) -prune -exec rm -rf {} +

docker-build: ## Constrói a imagem do backend
	$(COMPOSE) build backend

docker-up: ## Constrói e inicia todos os serviços em segundo plano
	$(COMPOSE) up --build --detach

docker-down: ## Para e remove os serviços
	$(COMPOSE) down

docker-restart: ## Reinicia o serviço do backend
	$(COMPOSE) restart backend

docker-logs: ## Acompanha os logs dos serviços
	$(COMPOSE) logs --follow --tail=100

docker-status: ## Exibe o estado dos serviços
	$(COMPOSE) ps

db-shell: ## Abre o terminal SQL do PostgreSQL
	$(COMPOSE) exec database psql -U $(POSTGRES_USER) -d $(POSTGRES_DB)

health: ## Verifica o endpoint de saúde do backend
	curl --fail --silent --show-error $(BACKEND_URL)/health
