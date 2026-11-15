# Repara — Gestão de assistência técnica

Projeto final de C216 — Sistemas Distribuídos, desenvolvido na branch
`projeto-final` com a stack das práticas do semestre.

O objetivo é acompanhar ordens de serviço de computadores e notebooks, desde o
recebimento até a entrega, relacionando clientes, diagnóstico, orçamento e
histórico do atendimento.

## Estado do projeto

Base do backend implementada: FastAPI, endpoint `/health`, contratos de resposta,
teste HTTP, Ruff e comandos Make. Clientes, ordens, banco, interface e Docker
ainda serão implementados nas próximas tarefas.
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
sem banco de dados nesta etapa. Para outra porta, use `make run PORT=8002`
e `make health PORT=8002`.

## Verificações disponíveis

```bash
make check-backend
```

Esse comando reúne `make lint`, `make format-check` e `make test`.
`make format` aplica a formatação e `make help` lista os comandos disponíveis.
O teste HTTP usa o TestClient do FastAPI, sem servidor externo ou banco.

## Estrutura atual

```text
backend/
  src/
    main.py        # aplicação FastAPI
    routers/       # rotas HTTP
    schemas/       # entrada e saída da API
    services/      # regras de negócio, nas próximas tarefas
    repositories/  # acesso aos dados, nas próximas tarefas
    models/        # persistência, na tarefa 03
  tests/integration/
docs/escopo.md     # escopo aprovado e regras planejadas
Makefile          # instalação, execução e validação
```

Instruções de migrations, frontend, Docker, CI e vídeo serão acrescentadas
conforme essas etapas forem implementadas e verificadas.
