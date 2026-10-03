# Pratica 4 — Arquitetura e API de tarefas

Assinatura: Fernando Puebla Stein — @Stenishh.

## Organizacao e decisoes

`backend/src/main.py` inicializa o FastAPI, conecta o armazenamento e registra
os routers. `routers/` cuida do contrato HTTP, `schemas/` valida entradas e
respostas com Pydantic, `services/` aplica as operacoes e filtragem, e
`repositories/` guarda tarefas. `dependencies.py` conecta o servico ao estado
da aplicacao e permite substituir o armazenamento nos testes.

Tarefas representam as atividades do laboratorio e possuem `id`, `title`,
`description` e `completed`. Modelos distintos para criacao, substituicao,
alteracao parcial e resposta tornam os contratos explicitos. Campos extras
sao rejeitados; titulo e descricao possuem limites, e espacos externos sao
removidos. IDs sao positivos e gerados pelo servidor, sem reutilizacao.

O repositorio em memoria evita adicionar dependencias e migrations para um
exercicio de organizacao e HTTP. O PostgreSQL e o Docker das praticas anteriores
continuam disponiveis, mas esta API nao utiliza o banco. Os dados desaparecem
ao reiniciar e cada processo tem seu proprio armazenamento: execute com um
unico worker. Um RLock protege operacoes entre threads do mesmo processo;
modelos imutaveis impedem alteracoes acidentais fora do repositorio.

## Contrato HTTP

| Metodo | Rota | Comportamento |
| --- | --- | --- |
| GET | `/health` | Saude do backend, 200 |
| GET | `/info` | Dados academicos e versao, 200 |
| GET | `/tasks` | Lista, 200; filtros `completed`, `offset` e `limit` |
| POST | `/tasks` | Cria, 201 e header Location |
| GET | `/tasks/{task_id}` | Consulta, 200 |
| PUT | `/tasks/{task_id}` | Substitui todos os campos editaveis, 200 |
| PATCH | `/tasks/{task_id}` | Altera somente os campos enviados, 200 |
| DELETE | `/tasks/{task_id}` | Remove, 204 sem corpo |

PUT exige titulo, descricao e conclusao, sem alterar o ID. PATCH usa
`exclude_unset=True`, preservando campos omitidos e aceitando `false` e texto
vazio para descricao. Um PATCH vazio ou com null e rejeitado com 422.
Recursos inexistentes retornam 404; entradas invalidas retornam 422.
O filtro e aplicado antes da paginacao, com ordem de criacao, offset minimo
zero e limite de 1 a 100 (padrao 20).

Exemplo no Swagger (`http://localhost:8000/docs`): crie uma tarefa com
`{"title":"Entregar pratica 4"}`, consulte `/tasks/1`, envie PATCH com
`{"completed":true}` e remova com DELETE. Use `make run` ou `make docker-up`
para iniciar o backend; o ponto de entrada continua `src.main:app`.

## Testes e CI

`tests/unit/` verifica servico, repositorio e validacao sem HTTP.
`tests/integration/` utiliza TestClient e exercita todos os endpoints,
ciclo CRUD, filtro, paginacao, idempotencia do PUT e erros 404/405/422.
Cada teste HTTP recebe um repositorio novo por dependency override, removido
em um bloco finally, sem depender da ordem dos testes ou de servidor externo.

Execute `make test-unit`, `make test-integration` ou `make test` para ambas.
No Windows sem Make, dentro de backend use
`poetry run python -m pytest tests/unit` e
`poetry run python -m pytest tests/integration`.
O CI valida o lock, lint, formatacao e ambas as suites em passos separados.
As dependencias e comandos das praticas anteriores foram preservados.

Validacao local em Python 3.12.10: 13 testes unitarios e 40 de integracao
aprovados; `poetry check --lock`, Ruff lint e Ruff format --check aprovados.
O CI usa Python 3.14, conforme a pratica anterior.

Referencias: [APIRouter e organizacao](https://fastapi.tiangolo.com/tutorial/bigger-applications/)
e [PUT/PATCH](https://fastapi.tiangolo.com/tutorial/body-updates/).
