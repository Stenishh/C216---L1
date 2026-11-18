# API de clientes

O CRUD de clientes está disponível no Swagger em `/docs`, no grupo Clientes.
O backend usa rotas HTTP, serviço de negócio, repositório SQLAlchemy e schemas
Pydantic. A interface React em `/customers` permite listar, cadastrar,
consultar, editar e excluir clientes com confirmação. Erros de vínculo são
exibidos sem remover o cadastro; falhas ao salvar preservam o formulário.

## Rotas

| Método | Caminho | Resultado |
| --- | --- | --- |
| POST | `/customers/` | Cria cliente, retorna 201 e cabeçalho Location |
| GET | `/customers/` | Retorna lista, 200; aceita q, offset e limit |
| GET | `/customers/{id}` | Consulta cliente, 200 |
| PUT | `/customers/{id}` | Substitui os dados cadastrais, 200 |
| PATCH | `/customers/{id}` | Atualiza somente os campos informados, 200 |
| DELETE | `/customers/{id}` | Exclui cliente sem ordens vinculadas, 204 sem corpo |

Use a barra final nas rotas de coleção. O ID deve ser inteiro positivo.
Cliente inexistente retorna 404; dados inválidos, 422; exclusão com ordens
vinculadas, 409. Mensagens de conflito não expõem SQL ou detalhes do banco.

## Entrada e saída

Exemplo de cadastro ou substituição completa:

```json
{
  "name": "Ana Silva",
  "phone": "(35) 99999-8888",
  "email": "ana@example.com"
}
```

- Nome obrigatório, de 1 a 100 caracteres, removendo espaços das extremidades.
- Telefone obrigatório, com 10 ou 11 dígitos. Espaços, parênteses e hífen são
  aceitos como máscara e removidos; letras e código internacional não são aceitos.
- E-mail opcional, com formato validado e limite de 254 caracteres. Vazio,
  espaços ou null significam ausência de e-mail. O domínio é normalizado.
- Campos desconhecidos são rejeitados; ID e data de cadastro não são editáveis.
- Contatos e nomes podem se repetir; clientes são identificados pelo ID.

A resposta inclui `id`, `name`, `phone` sem máscara, `email` (ou null) e
`created_at` com fuso horário. O ID e a data de cadastro permanecem iguais
após edição.

PUT exige nome e telefone. Omitir e-mail em PUT remove o e-mail anterior.
PATCH exige pelo menos um campo; campos omitidos permanecem iguais. Enviar
`{"email": null}` remove o e-mail; nome e telefone não aceitam null.

## Busca e paginação

GET `/customers/` aceita:

| Parâmetro | Regra |
| --- | --- |
| q | Parte do nome, até 100 caracteres; ignora maiúsculas/minúsculas e espaços nas extremidades |
| offset | Posição inicial, padrão 0; não pode ser negativa |
| limit | Quantidade máxima, padrão 20; de 1 a 100 |

Retorna uma lista JSON, ordenada pelo ID crescente. Sem correspondências,
retorna `[]`. Os caracteres `%` e `_` da busca são tratados literalmente.
A busca não promete equivalência entre caracteres com e sem acento.

## Exclusão protegida

Qualquer ordem vinculada impede a exclusão do cliente, incluindo ordens
canceladas ou entregues. O serviço verifica o vínculo e a chave estrangeira
do PostgreSQL também protege contra vínculos criados entre a consulta e a
exclusão. O conflito do banco é tratado com rollback e resposta 409:

```json
{
  "detail": "Não é possível excluir um cliente com ordens vinculadas."
}
```

Dados do cliente, ordens e histórico são preservados. O cliente vinculado
continua podendo ter nome e contato editados, conforme o escopo aprovado.

## Execução e testes

Siga a preparação do PostgreSQL em [Banco de dados](banco.md) e inicie a API
com `make run` e a interface com `make frontend-run`. Use a área Clientes ou o
Swagger para executar o CRUD. Não há autenticação nesta versão.

`make frontend-test` verifica os fluxos com HTTP simulado: cadastro, consulta,
edição e remoção de e-mail, confirmação/exclusão, conflito de vínculo,
paginação, preservação após falha, nova tentativa e bloqueio durante envio.

`make check-backend` verifica Ruff e os testes locais, incluindo normalização,
validação dos schemas e regras de serviço. Testes que dependem de PostgreSQL
são pulados quando TEST_DATABASE_URL não está definida.

`make test-postgres` executa **toda a suíte do backend** em banco temporário,
incluindo CRUD HTTP, persistência em nova conexão, PATCH/PUT, erros, busca,
paginação, contatos compartilhados, exclusão protegida por status e recuperação
após conflito de chave estrangeira. Usa o isolamento documentado na tarefa 03,
sem cadastrar dados no banco de desenvolvimento.
