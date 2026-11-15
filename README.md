# C216 — Prática 7: integração full-stack

React/Vite → FastAPI → PostgreSQL, com CORS explícito e testes E2E reais.
O cadastro de itens é persistido no banco e continua visível após recarregar.
As rotas `/tasks` das práticas anteriores foram preservadas.

## Executar

Requisitos: Docker Desktop/Engine com Compose v2, Node.js compatível com
`frontend/package.json`, Python 3.11+, Poetry, GNU Make e Bash (Git Bash no Windows).

```bash
cp .env.example .env
make frontend-install
make install
make up-build
make db-upgrade
make db-current
make ps
```

Frontend: http://localhost:5173. Swagger: http://localhost:8000/docs.
`db-current` deve mostrar `0002 (head)`. Após mudar código, execute `make up-build`.
`make down` para os serviços preservando o volume do banco.

## Validar

```bash
cd frontend && npx playwright install chromium && cd ..
make check-all
```

O alvo reúne Ruff, Pytest, Biome, Vitest, build Vite e `make e2e`.
O E2E inicia o projeto Compose `lab-e2e`, aplica migrations e executa Playwright
em desktop e mobile, sem mocks. Usa API 8001, frontend 5174, banco 5433 e volume
próprio. Ao terminar, inclusive em falha, remove os contêineres e **apaga somente
o banco temporário desse projeto**. O volume de desenvolvimento é preservado.
`make frontend-test-e2e` usa uma stack já em execução; `E2E_BASE_URL` tem padrão
`http://localhost:5173`.

Veja [as decisões e o roteiro da prática](docs/pratica-7.md).
