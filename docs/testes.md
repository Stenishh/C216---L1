# Testes do backend

## Execução local

Requisitos: Python 3.11 ou superior e Poetry 2.4.3. O CI utiliza Python 3.14.
No macOS, o comando `brew install poetry` instala o Poetry e um Python compatível.

Na raiz do repositório, execute:

```sh
make install
make test
```

`make install` instala as dependências do `backend/poetry.lock`, incluindo o grupo
`dev` com Pytest, HTTPX2 e Ruff. O ambiente virtual fica em `backend/.venv`.
`make test` executa `poetry run python -m pytest tests` dentro de `backend`.

Para executar um teste específico:

```sh
cd backend
poetry run python -m pytest tests/test_main.py -k health -v
```

## Qualidade e formatação com Ruff

Na raiz do repositório:

```sh
make lint          # Verifica problemas no código e ordenação dos imports
make format-check  # Verifica a formatação sem modificar arquivos
make format        # Aplica a formatação
```

Para corrigir automaticamente os problemas de lint que permitem correção segura:

```sh
cd backend
poetry run ruff check --fix src tests
```

A configuração em `backend/pyproject.toml` usa Python 3.11 como versão mínima,
linhas de 88 caracteres e aspas duplas. As regras verificam erros básicos,
imports, possíveis bugs e modernizações compatíveis com Python 3.11.
Consulte a [documentação do Ruff](https://docs.astral.sh/ruff/configuration/).

## GitHub Actions

O workflow `.github/workflows/ci-backend.yml` executa em cada `push` e em eventos
de abertura, reabertura e atualização de `pull_request`, sem filtro de branch.
Ele configura Python 3.14, instala Poetry 2.4.3, valida o arquivo de lock,
instala as dependências e executa `make lint`, `make format-check` e `make test`.

Depois do envio da branch ao GitHub, acompanhe os resultados na aba **Actions**
do repositório, no workflow **CI Backend**, ou na aba **Checks** do pull request.
Uma falha de lint, formatação ou teste faz o job falhar.
