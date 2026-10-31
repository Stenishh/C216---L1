BACKEND_DIR := backend
FRONTEND_DIR := frontend
POETRY ?= poetry
COMPOSE ?= $(shell docker compose version >/dev/null 2>&1 && echo docker compose || echo docker-compose)
APP ?= src.main:app
HOST ?= 127.0.0.1
PORT ?= 8000
BACKEND_URL ?= http://localhost:$(PORT)
POSTGRES_USER ?= c216
POSTGRES_DB ?= c216

.DEFAULT_GOAL := help

.PHONY: help install run test test-unit test-integration test-all lint format format-check clean docker-build docker-up docker-down \
	docker-restart docker-logs docker-status db-shell health

help: ## Exibe os comandos disponíveis
	@echo "Comandos disponíveis:"
	@awk 'BEGIN {FS = ":.*## "} /^[a-zA-Z_-]+:.*## / {printf "  %-16s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

install: ## Instala as dependências do backend e de desenvolvimento
	cd $(BACKEND_DIR) && $(POETRY) install --with dev

run: ## Inicia a API em modo de desenvolvimento
	cd $(BACKEND_DIR) && $(POETRY) run uvicorn $(APP) --host $(HOST) --port $(PORT) --reload

test: test-unit test-integration ## Executa todas as suites do backend

test-unit: ## Executa os testes unitarios
	cd $(BACKEND_DIR) && $(POETRY) run python -m pytest tests/unit

test-integration: ## Executa os testes de integracao HTTP
	cd $(BACKEND_DIR) && $(POETRY) run python -m pytest tests/integration

test-all: ## Executa todos os testes em uma chamada
	cd $(BACKEND_DIR) && $(POETRY) run python -m pytest tests

lint: ## Verifica o código e os imports com Ruff
	cd $(BACKEND_DIR) && $(POETRY) run ruff check src tests alembic

format: ## Formata o código com Ruff
	cd $(BACKEND_DIR) && $(POETRY) run ruff format src tests alembic

format-check: ## Verifica a formatação sem alterar arquivos
	cd $(BACKEND_DIR) && $(POETRY) run ruff format --check src tests alembic

clean: ## Remove os caches gerados no backend
	find $(BACKEND_DIR) -type d \( -name '__pycache__' -o -name '.pytest_cache' -o -name '.ruff_cache' \) -prune -exec rm -rf {} +

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

.PHONY: up-build logs-api db-upgrade db-migration db-current
up-build: docker-up ## Constrói e inicia API e PostgreSQL

logs-api: ## Acompanha os logs da API
	$(COMPOSE) logs --follow --tail=100 backend

db-upgrade: ## Aplica migrations no PostgreSQL do Compose
	$(COMPOSE) run --rm backend alembic upgrade head

db-migration: ## Gera migration (make db-migration msg="alteracao")
	@test -n "$(msg)" || (echo 'Informe msg="descricao"'; exit 1)
	cd $(BACKEND_DIR) && $(POETRY) run alembic revision --autogenerate -m "$(msg)"

db-current: ## Mostra a revisão do banco no Compose
	$(COMPOSE) run --rm backend alembic current

.PHONY: frontend-install frontend-dev frontend-lint frontend-format frontend-check frontend-test frontend-test-e2e frontend-build check-all

frontend-install: ## Instala dependências do frontend com o lockfile
	npm ci --prefix $(FRONTEND_DIR)

frontend-dev: ## Inicia o Vite
	npm run dev --prefix $(FRONTEND_DIR)

frontend-lint: ## Verifica o lint do frontend
	npm run lint --prefix $(FRONTEND_DIR)

frontend-format: ## Formata o frontend com Biome
	npm run format --prefix $(FRONTEND_DIR)

frontend-check: ## Verifica lint, formatação e imports do frontend
	npm run check --prefix $(FRONTEND_DIR)

frontend-test: ## Executa Vitest (unitários e integração)
	npm run test --prefix $(FRONTEND_DIR)

frontend-test-e2e: ## Executa Playwright (inicia Vite automaticamente)
	npm run test:e2e --prefix $(FRONTEND_DIR)

frontend-build: ## Gera o build de produção
	npm run build --prefix $(FRONTEND_DIR)

check-all: lint format-check test frontend-check frontend-test frontend-build frontend-test-e2e ## Valida backend e frontend
