# API de ordens de serviço

Os endpoints estão disponíveis no Swagger em `/docs`.

| Método | Caminho | Resultado |
| --- | --- | --- |
| POST | `/orders/` | Abre ordem e registra evento inicial; 201 e header Location |
| GET | `/orders/` | Lista ordens, mais recentes primeiro |
| GET | `/orders/{id}` | Consulta todos os dados da ordem |
| PUT | `/orders/{id}` | Substitui os dados de abertura |
| PATCH | `/orders/{id}` | Altera apenas os dados informados |
| DELETE | `/orders/{id}` | Exclui ordem sem andamento e seu evento; 204 sem corpo |

## Abertura e edição

Exemplo de corpo para POST e PUT (use o ID de um cliente já cadastrado):

```json
{
  "customer_id": 1,
  "equipment_type": "notebook",
  "brand": "Dell",
  "model": "Inspiron",
  "serial_number": "ABC123",
  "reported_problem": "Não liga"
}
```

`equipment_type` aceita `computer` ou `notebook`. Marca e modelo têm de 1 a
100 caracteres; defeito relatado, de 1 a 2.000. Os textos são aparados nas
extremidades e os obrigatórios não aceitam apenas espaços. Número de série é
opcional, até 100 caracteres e pode ser limpo com `null`. PUT exige todos os
campos obrigatórios e limpa o número de série quando omitido. PATCH exige ao
menos um campo, preserva os omitidos e rejeita `null` nos obrigatórios.

Cliente deve existir. Campos extras, incluindo ID, status, diagnóstico,
orçamento, decisão e datas, são rejeitados nos corpos de escrita. Esses dados
de atendimento aparecem na consulta, mas suas operações serão implementadas
nas tarefas 06 e 07.

Novas ordens têm status `received` e decisão `not_requested`. A ordem e seu
evento `open`, com status anterior nulo, são gravados na mesma transação.
Edições de cadastro não criam eventos, conforme o escopo aprovado.

## Regras e erros

Somente ordens `received` permitem alterar os dados de abertura. Exclusão exige
esse status e exatamente um evento inicial válido de abertura; ordens com
andamento são preservadas. A exclusão remove também o evento por cascata.
Edição e exclusão bloqueiam a linha da ordem durante a transação para proteger
a verificação do status contra alterações simultâneas.

- 404: ordem ou cliente inexistente.
- 422: dados, ID ou paginação inválidos.
- 409: edição ou exclusão bloqueada pelo andamento.

A listagem aceita `offset` (mínimo 0) e `limit` (1 a 100, padrão 20).
A ordenação é por criação decrescente e ID decrescente como desempate.
Filtros e indicadores ficam para a tarefa 11. Não há endpoint de escrita de
histórico nem operações de transição de status nesta etapa.

## Validação

`make check-backend` verifica lint, formatação e testes locais.
`make test-postgres` executa a suíte completa em PostgreSQL temporário isolado,
incluindo CRUD HTTP, persistência em nova conexão, evento inicial, cascata,
rollback, cliente inexistente, validações e bloqueios de edição/exclusão.
