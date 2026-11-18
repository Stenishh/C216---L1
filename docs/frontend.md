# Interface Repara

Frontend próprio em React com JavaScript, Vite, Tailwind CSS e Biome. Node.js
22.12 ou superior (ou 24 LTS) e npm são necessários. Dependências resolvidas
ficam no `frontend/package-lock.json`; use `npm ci` para reproduzir a instalação.

Na raiz, com GNU Make (Git Bash no Windows):

```bash
make frontend-install
make frontend-run
make frontend-check
make frontend-test
make frontend-build
```

Sem Make, execute `npm ci`, `npm run dev`, `npm run check`, `npm test` e
`npm run build` dentro de `frontend/`. Para aplicar formatação, use
`npm run format`. O build é gerado em `frontend/dist/`.

## Conexão com a API

Inicie o banco, aplique migrations e execute `make run`, conforme o README.
O frontend abre em http://127.0.0.1:5173. O Vite encaminha `/api/*` para
http://127.0.0.1:8000, removendo o prefixo. Isso permite desenvolvimento local
na mesma origem sem depender da configuração de CORS da atividade 12.

Copie `frontend/.env.example` para `frontend/.env` somente se precisar mudar
os padrões. `API_PROXY_TARGET` altera o destino do proxy de desenvolvimento.
`VITE_API_URL` define o endereço público usado pelo cliente HTTP e aceita
`/api` ou uma URL absoluta. Variáveis `VITE_*` são públicas no bundle:
**nunca coloque tokens, senhas ou URLs de banco nelas**. Reinicie o Vite após
alterar o ambiente; mudanças de produção exigem um novo build.

O proxy existe apenas no servidor de desenvolvimento. Para servir `dist/`,
configure o servidor web para encaminhar `/api` à API e retornar `index.html`
nas rotas da aplicação; alternativamente, use uma URL absoluta da API com
CORS explícito. Docker e implantação serão tratados na atividade 12.

## Organização e validação

A área **Clientes** permite listar registros paginados, cadastrar, consultar
contatos e data de cadastro, editar os dados (PUT) e excluir com confirmação.
E-mail vazio é enviado como `null`. A API continua sendo a autoridade sobre
as regras de negócio, incluindo exclusão protegida por vínculos.
Erros aparecem junto da operação; o formulário mantém os dados em falhas.
Requisições de leitura são canceladas ao sair da tela e respostas antigas
não substituem a página atual. Durante o salvamento, campos e botões de envio
ficam desabilitados, com bloqueio adicional contra chamadas duplicadas.

A área **Ordens de serviço** permite abrir, listar, consultar, editar e excluir
ordens sem andamento. O seletor de clientes aceita busca por nome e paginação,
mantendo a seleção ao mudar de página. O detalhe apresenta equipamento,
contato do cliente, diagnóstico, orçamento, decisão, serviço e histórico paginado.

As ações acompanham o estado recebido da API: iniciar diagnóstico, salvar
diagnóstico/orçamento, solicitar aprovação, aprovar/rejeitar, iniciar reparo,
salvar serviço, concluir, entregar e cancelar antes do reparo. Solicitação de
aprovação, decisão, conclusão, entrega, cancelamento e exclusão pedem confirmação;
rejeição e cancelamento também exigem motivo. Entrega envia `confirmed: true`
somente após confirmar. Estados finais oferecem apenas consulta.

Salve os textos e o orçamento antes de prosseguir. Valores monetários são
enviados como strings decimais, inclusive zero, sem arredondamento no cliente.
O histórico é recarregado após as transições. Em conflito por alteração em
outra sessão, a mensagem da API aparece e o botão **Atualizar dados da ordem**
permite consultar o estado atual (descartando edições locais não salvas).

Os testes cobrem CRUD de ordens, orçamento zero no fluxo até entrega,
rejeição/cancelamento com motivo, confirmação de exclusão, estados finais,
paginação do histórico, preservação em falha e bloqueio de envio duplicado.
Testes de leitura também verificam cancelamento e respostas fora de ordem.

`src/api/http.js` centraliza fetch, JSON, respostas 204, falhas de rede,
mensagens de conflito/validação e cancelamento. Os componentes não fazem
tratamento HTTP duplicado. `App.jsx` reúne navegação e rotas, com página
desconhecida e link para pular ao conteúdo. Não há autenticação nesta versão.

Vitest usa jsdom e Testing Library; as respostas HTTP são simuladas, sem
acesso ao banco local. E2E com os três serviços reais pertence à atividade 13.

### Dependências de desenvolvimento

Em 18/11/2026, `npm audit` aponta cinco entradas de alta severidade derivadas
de uma única vulnerabilidade ReDoS em `picomatch` (GHSA-fc5q-39xc-vjpf),
dependência transitiva de Vite/Vitest. A versão mais recente publicada,
4.0.7, ainda consta como afetada. O pacote é usado em desenvolvimento/build,
não no bundle de execução. Reavalie com `npm audit` ao atualizar o lockfile;
não aplique `audit fix --force`, que sugere regressões de versões sem resolver
adequadamente a árvore atual.
