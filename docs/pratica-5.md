# Prática 5 — Persistência

O CRUD `/tasks` mantém os contratos da Prática 4 (POST, GET, PUT, PATCH e DELETE).
Fluxo: routers → services → repositories → SQLAlchemy → PostgreSQL.
A estrutura existente `backend/src` foi preservada. `models/TaskModel` representa
a tabela; `schemas/Task*` valida os contratos HTTP. Cada requisição recebe uma
sessão que é fechada ao terminar e revertida em caso de erro.

## Executar

```bash
make install
make format
make lint
make test
make up-build
make db-current
```

O Compose inicia PostgreSQL 16 com volume persistente e healthcheck. O backend
executa `alembic upgrade head` antes do Uvicorn. A URL usa o nome do serviço
`database`, com driver `postgresql+psycopg`. Credenciais podem ser configuradas
por `.env` (veja `.env.example`). Não remova o volume para reiniciar a aplicação.

Para executar a API fora do Compose, inicie o banco com
`docker compose up -d database`, exporte `DATABASE_URL` usando `localhost`,
execute `cd backend && poetry run alembic upgrade head` e depois `make run`
na raiz. A aplicação não cria tabelas automaticamente.

## Validar persistência

```bash
curl -i -X POST localhost:8000/tasks -H 'Content-Type: application/json' \
  -d '{"title":"Prática 5","description":"Persistida no PostgreSQL"}'
curl localhost:8000/tasks
make docker-restart
# Aguarde a API iniciar e consulte novamente:
curl localhost:8000/tasks
make db-shell
# No psql: SELECT * FROM tasks;
```

Use o ID retornado para GET, PUT, PATCH e DELETE em `/tasks/{id}`.
A documentação interativa fica em http://localhost:8000/docs.

## Migrations

```bash
make db-upgrade
make db-current
# Após alterar os modelos, com DATABASE_URL local configurada:
make db-migration msg="descricao da alteracao"
# Revise o arquivo em backend/alembic/versions antes de aplicar.
cd backend
poetry run alembic history
poetry run alembic upgrade head
```

A migration `0001` reproduz a estrutura a partir de um banco vazio e tem downgrade.
`db-upgrade` e `db-current` usam o container; `db-migration` roda localmente para
gravar o arquivo no projeto. Reconstrua a imagem após criar novas migrations.

## Testes

`make test` usa SQLite temporário por teste, aplicando as migrations reais. Os
contratos HTTP, CRUD, filtros, paginação e leitura após abrir uma nova conexão
são verificados. Para rodar a mesma suíte contra PostgreSQL, crie um banco
**exclusivo de testes** e execute:

```bash
TEST_DATABASE_URL=postgresql+psycopg://c216:c216@localhost:5432/c216_test make test
```

A suíte aplica upgrade e downgrade a cada teste, removendo suas tabelas no final.
Nunca aponte `TEST_DATABASE_URL` para o banco da aplicação. O CI executa a suíte
contra PostgreSQL em um serviço dedicado.

## Validação realizada

- `make lint` e `make format-check`: aprovados.
- `make test`: 53 testes aprovados com SQLite temporário.
- `TEST_DATABASE_URL=.../c216_test make test`: 53 testes aprovados com PostgreSQL.
- `make up-build`: imagem construída e serviços iniciados.
- `alembic current`: `0001 (head)`; `alembic check`: nenhuma alteração pendente.
- Tarefa criada via HTTP e consultada com sucesso após reiniciar o backend.

O workflow foi configurado para executar os testes com PostgreSQL; o resultado
remoto do GitHub Actions depende do envio das alterações ao repositório.
