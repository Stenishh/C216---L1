# Prática 6 — Frontend moderno

O diretório `frontend/` contém uma aplicação independente em JavaScript com React,
Vite e Tailwind CSS v4. Não utiliza API, banco, localStorage ou outros mecanismos
de persistência. O backend e o Docker Compose não foram alterados.

## Executar

Pré-requisito: Node.js 22 LTS (22.22.2+), 24.15+ ou 26+ e npm, conforme as
dependências instaladas. Confira `node --version` e
`npm --version`. Na raiz do repositório:

```bash
make frontend-install
make frontend-dev
```

Abra http://localhost:5173. Preencha Nome e, opcionalmente, Descrição; clique em
Adicionar. O nome é obrigatório, aceita até 100 caracteres após remover espaços
nas extremidades e apresenta erros associados ao campo. Ao cadastrar, os campos
são limpos e o item aparece na lista. Atualizar a página apaga os itens.

## Organização e conceitos

- `src/App.jsx`: armazena os itens em `useState`. A função `addItem` será o ponto
  de integração HTTP na Prática 7; nesta prática só altera o estado local.
- `src/components/ItemForm.jsx`: mantém os campos e erros e recebe a função
  `onAdd` por props. Usa validação pura antes de enviar os valores ao pai.
- `src/components/ItemList.jsx`: recebe `items` por props e mostra a lista ou o
  estado vazio. Cada item recebe `crypto.randomUUID()`; a `key` estável permite
  que o React identifique cada elemento entre renderizações.
- `src/validation.js`: valida e normaliza os campos, sem efeitos colaterais.
- `src/index.css`: importa o Tailwind v4; a integração usa o plugin do Vite.

## Qualidade e testes

```bash
make frontend-install
make frontend-lint
make frontend-check
make frontend-test
make frontend-build
cd frontend
npx playwright install chromium
cd ..
make frontend-test-e2e
```

Use `make frontend-format` para aplicar formatação e `npm run test:watch --prefix
frontend` para desenvolver com Vitest. `make check-all` executa Ruff, Pytest,
Biome, Vitest, build e Playwright; as dependências de ambos os projetos e o
Chromium precisam estar instalados antes.

Os testes unitários cobrem normalização, nome vazio, limites de 100/101 caracteres,
callback e limpeza do formulário, mensagens acessíveis e lista com/sem descrição.
Os testes de integração exercitam o App completo, múltiplos cadastros e rejeição
de entradas inválidas. O Playwright executa no Chromium em desktop e celular:
carregamento, erro e correção, cadastro, campos limpos, ausência de requisições
fetch/XHR, ausência de overflow e perda do estado após recarregar.

## CI e entrega

`ci-frontend.yml` instala pelo lockfile, verifica lint, formatação e imports,
executa Vitest, gera build, instala Chromium e executa Playwright. Em falha,
preserva o relatório HTML por sete dias. O workflow roda em PRs e pushes na
`main` que alterem o frontend, seu workflow ou o Makefile compartilhado.
O workflow do backend recebeu filtros equivalentes para seus próprios arquivos.
Como o Makefile é compartilhado, sua alteração dispara ambos os workflows.

A branch `pratica-6` parte de `pratica-5`. A entrega deve ser revisada em PR para
`pratica-5`, com as labels `Frontend`, `Test` e `Prática 6`. O merge fica para
revisão. A integração full-stack e a containerização ficam para a Prática 7.
