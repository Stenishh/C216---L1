# Verificação completa

Requer Python 3.11+, Poetry 2.4+, Node 22.12+, npm, Make e Docker com Compose v2.
Execute `make install frontend-install` e `make e2e-install`. Em Linux/CI,
instale também dependências do Chromium com `make e2e-install-deps`.

`make check-all` executa Ruff (lint e formatação), toda a suíte Pytest em
PostgreSQL temporário, Biome, Vitest, build e Playwright. Os testes Vitest
ficam em `src/**/*.test.{js,jsx}` e usam HTTP simulado. Playwright fica em
`frontend/e2e` e usa frontend Nginx, API e PostgreSQL reais, sem mocks.
Também é possível executar somente `make e2e`.

O runner `scripts/test_e2e.py` cria um projeto Compose com sufixo aleatório,
senha temporária, banco em tmpfs e porta aleatória da interface. Não publica
o banco nem a API. Aplica migrations antes de iniciar Playwright. Em sucesso
ou falha, `finally` executa `down` somente nesse projeto; os dados do tmpfs
são descartados junto com o contêiner. Nenhum volume de desenvolvimento é
referenciado. Interrupção forçada do processo/SO pode exigir remoção manual
do projeto `repara-e2e-*` correspondente, sem usar comandos globais de limpeza.

Os cenários cobrem CRUD de cliente e ordem sem andamento, orçamento zero,
aprovação, reparo, conclusão, entrega, histórico, filtros e reload em URLs
de detalhe para confirmar persistência. Também verificam o bloqueio de
exclusão enquanto há uma ordem em andamento e a remoção do cliente com
ordens entregues e canceladas, incluindo seus históricos. Falhas geram screenshot, trace e
relatório em `frontend/test-results` e `frontend/playwright-report`, ignorados
pelo Git. Para examinar: `make e2e-report`.

O workflow `.github/workflows/checks.yml` executa a mesma verificação em PRs
para `main`, em pushes para `main`/`projeto-final` que alterem backend,
frontend, Compose, scripts, Makefile ou CI, e por disparo manual. PRs não
têm filtro por caminho, evitando checks obrigatórios pendentes em mudanças
somente de documentação. Relatórios E2E são publicados como artefatos em falha.
