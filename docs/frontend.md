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

`src/api/http.js` centraliza fetch, JSON, respostas 204, falhas de rede,
mensagens de conflito/validação e cancelamento. Os componentes não fazem
tratamento HTTP duplicado. `App.jsx` reúne navegação e rotas, com página
desconhecida e link para pular ao conteúdo. Não há autenticação nesta versão.

Vitest usa jsdom e Testing Library; as respostas HTTP são simuladas, sem
acesso ao banco local. E2E com os três serviços reais pertence à atividade 13.
