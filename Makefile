POETRY ?= poetry
HOST ?= 127.0.0.1
PORT ?= 8000
BACKEND_URL ?= http://$(HOST):$(PORT)
COMPOSE ?= docker compose
NPM ?= npm

.DEFAULT_GOAL := help
.PHONY: help install run health test lint format format-check check-backend
.PHONY: env-init db-up db-down db-status db-upgrade db-current db-check db-migration test-postgres
.PHONY: frontend-install frontend-run frontend-check frontend-test frontend-build

help:
	@echo "make up-build / ps / down - opera frontend, API e banco em Docker"
	@echo "make db-upgrade-local / db-current-local - migrations pelo Python local"
	@echo "make e2e-install - instala Chromium para testes E2E"
	@echo "make frontend-install - instala dependencias do frontend pelo lockfile"
	@echo "make frontend-run     - inicia interface com proxy local para a API"
	@echo "make frontend-check   - verifica JavaScript, JSX e formatacao com Biome"
	@echo "make frontend-test    - executa Vitest e Testing Library"
	@echo "make frontend-build   - gera build de producao da interface"
	@echo "make install       - instala dependencias do backend e de desenvolvimento"
	@echo "make run           - inicia a API local com recarregamento"
	@echo "make health        - consulta a saude da API em execucao"
	@echo "make test          - executa Pytest"
	@echo "make lint          - verifica codigo e imports com Ruff"
	@echo "make format        - formata codigo com Ruff"
	@echo "make format-check  - confere formatacao sem alterar arquivos"
	@echo "make check-backend - executa lint, format-check e testes"
	@echo "make env-init      - cria .env a partir do exemplo, sem sobrescrever"
	@echo "make db-up         - inicia somente PostgreSQL e aguarda saude"
	@echo "make db-down       - para PostgreSQL preservando o volume"
	@echo "make db-status     - mostra o estado do banco"
	@echo "make db-upgrade    - aplica migrations no banco configurado"
	@echo "make db-current    - mostra a revisao atual"
	@echo "make db-check      - confere models e migrations"
	@echo "make db-migration msg=descricao - gera uma nova migration"
	@echo "make test-postgres - valida migrations e integridade em banco efemero"

install:
	cd backend && $(POETRY) install --with dev

run:
	cd backend && $(POETRY) run uvicorn src.main:app --host $(HOST) --port $(PORT) --reload

health:
	curl --fail --silent --show-error $(BACKEND_URL)/health

test:
	cd backend && $(POETRY) run python -m pytest

lint:
	cd backend && $(POETRY) run ruff check src tests alembic ../scripts

format:
	cd backend && $(POETRY) run ruff format src tests alembic ../scripts

format-check:
	cd backend && $(POETRY) run ruff format --check src tests alembic ../scripts

check-backend: lint format-check test

env-init:
	cd backend && $(POETRY) run python -c "from pathlib import Path; p=Path('../.env'); p.exists() or p.write_bytes(Path('../.env.example').read_bytes())"

db-up:
	$(COMPOSE) up --detach --wait db

db-down:
	$(COMPOSE) down

db-status:
	$(COMPOSE) ps

db-upgrade:
	$(COMPOSE) exec -T api alembic upgrade head

db-current:
	$(COMPOSE) exec -T api alembic current

db-check:
	cd backend && $(POETRY) run alembic check

db-migration:
	$(if $(strip $(msg)),,$(error Informe msg=descricao))
	cd backend && $(POETRY) run alembic revision --autogenerate -m "$(msg)"

test-postgres:
	cd backend && $(POETRY) run python ../scripts/test_database.py

frontend-install:
	cd frontend && $(NPM) ci

frontend-run:
	cd frontend && $(NPM) run dev

frontend-check:
	cd frontend && $(NPM) run check

frontend-test:
	cd frontend && $(NPM) test

frontend-build:
	cd frontend && $(NPM) run build

.PHONY: up-build ps down db-upgrade-local db-current-local e2e-install
up-build:
	$(COMPOSE) up --build --detach --wait

ps:
	$(COMPOSE) ps

down:
	$(COMPOSE) down

db-upgrade-local:
	cd backend && $(POETRY) run alembic upgrade head

db-current-local:
	cd backend && $(POETRY) run alembic current

e2e-install:
	cd frontend && $(NPM) exec playwright install chromium
