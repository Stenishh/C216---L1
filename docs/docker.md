# Execução completa com Docker

Requer Docker Desktop/Engine com Compose v2. Na raiz, copie `.env.example`
para `.env` (`make env-init` também faz isso sem sobrescrever). Revise as
credenciais e portas. Senhas usadas na URL devem estar codificadas para URL.

```sh
make up-build
make db-upgrade
make db-current
make ps
```

Abra http://127.0.0.1:8080. A API está em http://127.0.0.1:8000/docs.
`db-current` deve mostrar `0001 (head)`. Aplique migrations antes de usar
as telas; o healthcheck `/health` verifica o processo da API, não o schema.

Frontend Nginx e API executam como usuários sem privilégios. O Nginx encaminha
`/api/` para `api:8000`, mantendo a origem da interface; recarregar URLs de
detalhe funciona pelo fallback da SPA. As dependências de inicialização
aguardam os healthchecks. PostgreSQL usa o volume nomeado `repara-data`.
`make down` encerra os serviços e preserva esse volume. `make up-build`
recria serviços quando necessário, mantendo os cadastros.

`API_PORT`, `WEB_PORT` e `DB_PORT` alteram as portas publicadas no host.
`DATABASE_URL` do `.env` é usada somente pelo Python local; o Compose monta
a URL interna a partir de `POSTGRES_*`, com hostname `db`.
`CORS_ORIGINS` é uma lista de origens separadas por vírgula, sem wildcard;
ao alterar a porta da interface, ajuste também essa lista. CORS permite
GET, POST, PUT, PATCH e DELETE e os headers Content-Type e Accept.

Para executar somente PostgreSQL e Python local, use `make db-up`,
`make db-upgrade-local`, `make db-current-local` e `make run`.
`make db-check` e `make db-migration msg=descricao` continuam locais.
`make test-postgres` sempre usa banco efêmero separado do desenvolvimento.
