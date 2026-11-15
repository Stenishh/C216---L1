# Prática 7 — CORS, persistência e multicontêiner

## Implementação

- `frontend/src/services/items.js`: GET/POST `/items/`, JSON, descrição vazia como
  `null`, erros de rede, mensagens `detail` e fallback para erros sem texto.
- `App`: carrega os dados da API no início e adiciona a resposta do POST à lista.
  O formulário fica disponível após uma listagem bem-sucedida.
- `ItemForm`: valida antes de enviar, aguarda o cadastro, bloqueia envios durante
  o salvamento, limpa apenas no sucesso e preserva campos no erro.
- FastAPI: route → service → repository, schemas de entrada/saída, nome de 1 a
  100 caracteres e restrição única no banco, inclusive para cadastros simultâneos.
  Nomes repetidos retornam 409 com `Já existe um item com esse nome`.
- Migration `0002` adiciona `items` sem modificar a tabela `tasks` existente.
  A branch anterior tinha somente tarefas; foi necessário acrescentar o contrato
  de itens descrito no enunciado. As rotas e testes anteriores continuam válidos.
- `compose.yaml`: `db`, `api` e `frontend`, todos com healthcheck. A API aguarda
  o PostgreSQL e o frontend aguarda a API. Migrations são aplicadas explicitamente.

## Rede e configuração

`CORS_ORIGINS` recebe origens separadas por vírgulas, por padrão localhost e
127.0.0.1 na porta 5173. Somente GET/POST e Content-Type são autorizados, sem
credenciais. CORS é uma regra do navegador e não substitui autenticação.

O React roda no navegador: `VITE_API_URL` aponta para `http://localhost:8000`,
enquanto a API acessa `db:5432` pela rede Docker. Variáveis `VITE_*` são públicas:
nunca devem conter segredos. Use a barra final `/items/` para evitar redirect 307.
As portas são configuráveis por `API_PORT`, `FRONTEND_PORT` e `DB_PORT`.
Ao trocar a porta do frontend, ajuste também `CORS_ORIGINS`.

## Verificação manual

1. Execute `make up-build`, `make db-upgrade`, `make db-current` e `make ps`.
2. Abra a interface e o Swagger nos endereços indicados no README.
3. Cadastre um nome novo e recarregue: o item deve permanecer.
4. Repita o nome: deve aparecer a mensagem de duplicidade, preservando o campo.
5. No DevTools/Network, confira OPTIONS seguido de POST `/items/` e o cabeçalho
   `access-control-allow-origin` com a origem do frontend.
6. Execute `make check-all`; ao final, `docker compose -p lab-e2e ps` deve estar vazio.

## Testes

Vitest cobre carregamento, dados existentes, lista vazia, validação sem POST,
cadastro, erro de conexão, 409 e o contrato HTTP. Pytest cobre validação, persistência,
duplicidade e CORS permitido/negado, além da suíte anterior de tarefas.
O Playwright cadastra um nome único, recarrega a página e confirma a persistência
com API e PostgreSQL reais, depois verifica duplicidade. A execução usa o projeto
isolado `lab-e2e`; o CI do frontend executa esse mesmo alvo.
