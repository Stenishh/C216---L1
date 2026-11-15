POETRY ?= poetry
HOST ?= 127.0.0.1
PORT ?= 8000
BACKEND_URL ?= http://$(HOST):$(PORT)

.DEFAULT_GOAL := help
.PHONY: help install run health test lint format format-check check-backend

help:
	@echo "make install       - instala dependencias do backend e de desenvolvimento"
	@echo "make run           - inicia a API local com recarregamento"
	@echo "make health        - consulta a saude da API em execucao"
	@echo "make test          - executa Pytest"
	@echo "make lint          - verifica codigo e imports com Ruff"
	@echo "make format        - formata codigo com Ruff"
	@echo "make format-check  - confere formatacao sem alterar arquivos"
	@echo "make check-backend - executa lint, format-check e testes"

install:
	cd backend && $(POETRY) install --with dev

run:
	cd backend && $(POETRY) run uvicorn src.main:app --host $(HOST) --port $(PORT) --reload

health:
	curl --fail --silent --show-error $(BACKEND_URL)/health

test:
	cd backend && $(POETRY) run python -m pytest

lint:
	cd backend && $(POETRY) run ruff check src tests

format:
	cd backend && $(POETRY) run ruff format src tests

format-check:
	cd backend && $(POETRY) run ruff format --check src tests

check-backend: lint format-check test
