# Repara — Gestão de assistência técnica

Projeto final de C216 — Sistemas Distribuídos, desenvolvido na branch
`projeto-final` com a stack das práticas do semestre.

O objetivo é acompanhar ordens de serviço de computadores e notebooks, desde o
recebimento até a entrega, relacionando clientes, diagnóstico, orçamento e
histórico do atendimento.

## Estado do projeto

Base do backend implementada: FastAPI, endpoint `/health`, contratos de resposta,
Ruff e comandos Make. A persistência inclui models de clientes, ordens e
histórico, PostgreSQL em Docker e migration inicial com Alembic. Os endpoints
do domínio, a interface e a execução completa dos três serviços ainda serão
implementados nas próximas tarefas.
O escopo da primeira versão foi aprovado em 15/11/2026. Os campos, os fluxos e
as regras estão em [Escopo e regras de negócio](docs/escopo.md).

O desenvolvimento será incremental, conforme o
[GitHub Project](https://github.com/users/Stenishh/projects/1).
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
O teste HTTP usa o TestClient do FastAPI, sem servidor externo ou banco.

## PostgreSQL e migrations

Com Docker e Compose v2 ativos:

```bash
make env-init
make db-up
make db-upgrade
make db-current
make db-check
make test-postgres
```

Revise o `.env` criado antes de iniciar o banco; os valores são exemplos locais.
`db-current` deve mostrar `0001 (head)`. Se a porta 5432 estiver ocupada, ajuste
DB_PORT e a porta de DATABASE_URL no `.env`. `make db-down` preserva o volume.

`make test-postgres` executa os testes de banco em PostgreSQL temporário e
isolado, sem tocar os dados de desenvolvimento. Os testes de banco são pulados
na execução local de `make test` quando TEST_DATABASE_URL não está definida.
Veja o [modelo, as variáveis e os comandos de banco](docs/banco.md).

## Estrutura atual

```text
backend/
  src/
    main.py        # aplicação FastAPI
    routers/       # rotas HTTP
    schemas/       # entrada e saída da API
    services/      # regras de negócio, nas próximas tarefas
    repositories/  # acesso aos dados, nas próximas tarefas
    models/        # clientes, ordens e histórico
    core/          # configuração por ambiente
    database/      # base declarativa, conexão e sessões
  alembic/         # migrations versionadas
  tests/integration/
  tests/unit/
docs/escopo.md     # escopo aprovado e regras planejadas
docs/banco.md      # modelo, configuração e validação do banco
compose.yaml      # PostgreSQL de desenvolvimento
compose.test.yaml # PostgreSQL temporário para testes
scripts/          # runner de testes com banco isolado
Makefile          # instalação, execução e validação
```

Instruções de frontend, Docker da aplicação completa, CI e vídeo serão acrescentadas
conforme essas etapas forem implementadas e verificadas.
