# Repara — Gestão de assistência técnica

Projeto final de C216 — Sistemas Distribuídos, desenvolvido na branch
`projeto-final` com a stack das práticas do semestre.

O objetivo é acompanhar ordens de serviço de computadores e notebooks, desde o
recebimento até a entrega, relacionando clientes, diagnóstico, orçamento e
histórico do atendimento.

## Estado do projeto

Backend com FastAPI, endpoint `/health`, CRUD de clientes e ordens, validação de dados,
Ruff e comandos Make. A persistência inclui models de clientes, ordens e
histórico, PostgreSQL em Docker e migration inicial com Alembic. O atendimento
permite diagnóstico, orçamento, aprovação/rejeição, reparo, conclusão, entrega,
cancelamento e consulta do histórico. A base da interface usa React, Vite,
Tailwind e Biome, com navegação, cliente HTTP, CRUD de clientes e ordens e
fluxo completo de atendimento com histórico e confirmações. A execução completa
dos três serviços em Docker está em [Execução com Docker](docs/docker.md).
O escopo da primeira versão foi aprovado em 15/11/2026. Os campos, os fluxos e
as regras estão em [Escopo e regras de negócio](docs/escopo.md).

O histórico de desenvolvimento está organizado no
[GitHub Project](https://github.com/users/Stenishh/projects/1).

## Executar a aplicação completa

Com Docker Desktop/Engine e Compose v2, Python, Poetry e Make disponíveis:

```bash
make install
make env-init
make up-build
make db-upgrade
make db-current
make ps
```

No PowerShell, se `make` não for reconhecido, execute os comandos equivalentes
diretamente com Docker Compose (sem precisar de Make, Python ou Poetry no host):

```powershell
if (!(Test-Path .env)) { Copy-Item .env.example .env }
# Revise o .env antes de continuar.
docker compose up --build --detach --wait
docker compose exec -T api alembic upgrade head
docker compose exec -T api alembic current
docker compose ps
```

Para encerrar os serviços pelo PowerShell, use `docker compose down`.

Revise o `.env` antes de iniciar os contêineres. Acesse a interface em
http://127.0.0.1:8080 e a API em http://127.0.0.1:8000/docs.
`db-current` deve mostrar `0001 (head)`. As migrations são um passo explícito:
aplique-as antes de usar as telas. `make down` encerra os serviços preservando
os dados. Portas, proxy e variáveis estão em [Docker](docs/docker.md).

## Tecnologias

Backend Python com FastAPI, Poetry, Ruff, SQLAlchemy e Alembic; banco
PostgreSQL; frontend JavaScript com React, Vite, Tailwind e Biome.
Testes com Pytest, Vitest/Testing Library e Playwright. Execução integrada
com Docker Compose e verificação automática com GitHub Actions.

## Pré-requisitos e execução local do backend

Python 3.11 ou superior, Poetry 2.4 ou superior e GNU Make. No Windows, use
Git Bash com Make e Poetry disponíveis no PATH. O Poetry cria o ambiente local
em `backend/.venv`; as versões resolvidas estão em `backend/poetry.lock`.

Na raiz do repositório:

```bash
make install
make run
```

A API inicia em http://127.0.0.1:8000. A documentação interativa fica em
http://127.0.0.1:8000/docs. Em outro terminal, `make health` deve retornar
`{"status":"ok","service":"repara"}`. Esse endpoint verifica somente a API,
sem testar a conexão com o banco. Para outra porta, use `make run PORT=8002`
e `make health PORT=8002`.

## Verificações disponíveis

```bash
make check-backend
```

Esse comando reúne `make lint`, `make format-check` e `make test`.
`make format` aplica a formatação e `make help` lista os comandos disponíveis.
Os testes HTTP usam o TestClient do FastAPI, sem servidor externo. O teste de
saúde e os testes unitários não precisam de banco; os testes HTTP de clientes e ordens
usam PostgreSQL na execução isolada descrita abaixo.

## PostgreSQL e migrations

Com Docker e Compose v2 ativos:

```bash
make env-init
make db-up
make db-upgrade-local
make db-current-local
make db-check
make test-postgres
```

Revise o `.env` criado antes de iniciar o banco; os valores são exemplos locais.
`db-current-local` deve mostrar `0001 (head)`. Se a porta 5432 estiver ocupada, ajuste
DB_PORT e a porta de DATABASE_URL no `.env`. `make db-down` preserva o volume.

`make test-postgres` executa toda a suíte do backend com PostgreSQL temporário e
isolado, sem tocar os dados de desenvolvimento. Os testes que precisam de banco são pulados
na execução local de `make test` quando TEST_DATABASE_URL não está definida.
Veja o [modelo, as variáveis e os comandos de banco](docs/banco.md).

## Clientes

O Swagger em `/docs` permite cadastrar, listar, consultar, editar e excluir
clientes. A listagem aceita busca por nome e paginação. Telefone com máscara é
normalizado e e-mail é opcional e validado. Ordens em andamento impedem a
exclusão do cliente (409). Se todas estiverem entregues ou canceladas, a
confirmação de exclusão remove o cliente, suas ordens e os históricos juntos.

Veja o [contrato e as regras da API de clientes](docs/clientes.md).

## Ordens de serviço

O Swagger permite abrir, listar, consultar, editar (PUT/PATCH) e excluir ordens
sem andamento. A abertura exige cliente existente e registra um evento inicial
na mesma transação. Dados de abertura só podem ser editados no status Recebida;
a exclusão exige apenas o evento inicial e também o remove. A listagem tem
paginação e apresenta as ordens mais recentes primeiro.

Veja o [contrato e as regras da API de ordens](docs/ordens.md).
O atendimento permite iniciar diagnóstico, preencher diagnóstico/orçamento,
solicitar aprovação, registrar aprovação ou rejeição com motivo e iniciar reparo
somente após aprovação. Valor zero é aceito; valores negativos ou com mais de
duas casas decimais são rejeitados. Mudanças e eventos são persistidos juntos.

Durante o reparo, é possível registrar o serviço realizado, obrigatório para
concluir. Entrega exige ordem concluída e confirmação explícita. Cancelamento
exige motivo e só é permitido antes do início do reparo. Estados finais ficam
disponíveis apenas para consulta. O histórico em `/orders/{id}/history` é
somente leitura, com paginação e eventos em ordem de ocorrência.

## Estrutura atual

```text
backend/
  src/
    main.py        # aplicação FastAPI
    routers/       # rotas HTTP
    schemas/       # entrada e saída da API
    services/      # regras de negócio
    repositories/  # acesso aos dados
    models/        # clientes, ordens e histórico
    core/          # configuração por ambiente
    database/      # base declarativa, conexão e sessões
  alembic/         # migrations versionadas
  tests/integration/
  tests/unit/
docs/escopo.md     # escopo aprovado e regras planejadas
frontend/         # React, Vite, Tailwind, cliente HTTP e testes de interface
docs/frontend.md  # execução local, configuração pública e fluxos da interface
docs/banco.md      # modelo, configuração e validação do banco
compose.yaml      # frontend Nginx, API e PostgreSQL com volume persistente
compose.test.yaml # PostgreSQL temporário para testes
compose.e2e.yaml  # três serviços isolados para Playwright
scripts/          # runner de testes com banco isolado
Makefile          # instalação, execução e validação
```

## Frontend

Com Node.js 22.12+ e npm, execute `make frontend-install` e
`make frontend-run`. A interface abre em http://127.0.0.1:5173 e encaminha
`/api` à API local na porta 8000. Valide com `make frontend-check`,
`make frontend-test` e `make frontend-build`.

Veja [configuração, comandos e testes do frontend](docs/frontend.md).
Para a aplicação completa, veja [Docker](docs/docker.md).

`make check-all` valida backend, frontend e E2E real com PostgreSQL isolado.
Veja [preparação, isolamento e CI](docs/testes.md).

## Vídeo e entrega

O vídeo demonstrativo ainda será gravado e seu link será publicado nesta seção
antes da entrega. O [roteiro de demonstração](docs/entrega.md) cobre Docker,
arquitetura, CRUD, atendimento, persistência e testes.

A entrega usa obrigatoriamente a branch `projeto-final` e um PR de
`projeto-final` para `main`, aberto e sem merge durante a avaliação. Os Checks
aplicáveis precisam passar no commit final publicado, incluindo as mudanças
de frontend e backend.

Até 28/11/2026, enviar no Teams os links do PR e do vídeo, conforme o
esclarecimento da aula. O link do repositório pode ser incluído adicionalmente
para contemplar também a lista do PDF. Não enviar ZIP. O vídeo deve mostrar
a aplicação real e ter narração do próprio aluno; o link também deve estar
neste README. Todos os links precisam permanecer acessíveis ao monitor e ao
professor até o fim da avaliação.
