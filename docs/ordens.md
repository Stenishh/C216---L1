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
orçamento, decisão e datas, são rejeitados nos corpos de abertura e edição
cadastral. Diagnóstico e orçamento têm operações próprias descritas abaixo.

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
Filtros e indicadores ficam para a tarefa 11. Não há endpoint de escrita livre
de histórico ou status.

## Diagnóstico, orçamento e decisão

As operações abaixo retornam 200 com os dados atualizados da ordem. Ações sem
campos são chamadas sem corpo. Elas exigem ordem existente (404), estado
compatível (409) e dados válidos (422).

| Método | Caminho (após `/orders/{id}`) | Regra |
| --- | --- | --- |
| POST | `/begin-diagnosis` | Recebida → Em diagnóstico |
| PATCH | `/diagnosis` | Edita diagnóstico e/ou orçamento somente Em diagnóstico |
| POST | `/request-approval` | Exige diagnóstico e valor; passa a Aguardando aprovação, decisão pendente |
| POST | `/approve-budget` | Exige decisão pendente; registra aprovação sem iniciar reparo |
| POST | `/reject-budget` | Exige decisão pendente e motivo; cancela a ordem e registra rejeição |
| POST | `/start-repair` | Exige Aguardando aprovação e decisão aprovada; passa a Em reparo |

Exemplo de PATCH `/orders/1/diagnosis`:

```json
{
  "diagnosis": "Fonte defeituosa",
  "budget_amount": "150.90"
}
```

Diagnóstico tem de 1 a 2.000 caracteres quando preenchido. Orçamento aceita de
0 a 999999.99 com até duas casas decimais. Recomenda-se enviar o valor como
string decimal; o backend usa Decimal e PostgreSQL NUMERIC, e a resposta retorna
o valor como string. Zero é um orçamento válido. Valores negativos, não finitos
ou com precisão excedente retornam 422, sem arredondamento silencioso.

O PATCH exige ao menos um campo, preserva os omitidos e permite limpar
diagnóstico ou orçamento com `null` antes da solicitação. A solicitação exige
ambos preenchidos. Após solicitar aprovação, diagnóstico e orçamento ficam
bloqueados; tentativas de revisão retornam 409.

Rejeição recebe `{"reason": "Cliente não aprovou o custo"}`, com motivo de 1 a
500 caracteres após remover espaços das extremidades. O motivo fica na ordem
e no evento. Aprovação registra o valor aprovado no evento e mantém o status
`awaiting_approval`; somente `/start-repair` inicia o reparo.

Repetir uma ação concluída, decidir novamente ou iniciar reparo sem aprovação
retorna 409, sem evento adicional. As ações bloqueiam a linha da ordem durante
a transação e salvam mudança e evento juntos. Edições de diagnóstico/orçamento
não geram eventos textuais.

## Reparo, conclusão, entrega e cancelamento

| Método | Caminho (após `/orders/{id}`) | Regra |
| --- | --- | --- |
| PATCH | `/repair` | Edita serviço realizado somente Em reparo |
| POST | `/complete-repair` | Em reparo → Concluída; exige serviço realizado |
| POST | `/deliver` | Concluída → Entregue; exige confirmação explícita |
| POST | `/cancel` | Recebida, Em diagnóstico ou Aguardando aprovação → Cancelada; exige motivo |
| GET | `/history` | Consulta eventos em ordem de ocorrência, com paginação |

PATCH `/orders/1/repair` recebe `{"service_performed": "Fonte substituída"}`.
O campo é obrigatório no corpo, aceita de 1 a 2.000 caracteres após remover
espaços das extremidades e pode ser limpo com `null` durante o reparo.
Concluir sem serviço preenchido retorna 409. Edição textual não gera evento.
Depois da conclusão, o serviço fica bloqueado.

POST `/orders/1/complete-repair` não recebe corpo. POST `/orders/1/deliver`
recebe `{"confirmed": true}`; ausência, `false`, números e strings retornam 422.
A interface deverá pedir confirmação ao operador antes de enviar a entrega.

POST `/orders/1/cancel` recebe `{"reason": "Cliente desistiu do atendimento"}`,
com motivo de 1 a 500 caracteres após remover espaços das extremidades.
Cancelamento preserva diagnóstico, orçamento, decisão existente e histórico;
não registra rejeição de orçamento. É permitido cancelar mesmo após aprovação,
desde que o reparo ainda não tenha começado. Após o início do reparo retorna 409.

Conclusão, entrega e cancelamento geram evento com status anterior, resultante
e data UTC. Cancelamento registra também o motivo na ordem e no evento.
As alterações e o evento são salvos juntos, com rollback em caso de falha.
Entregue e Cancelada são estados finais, sem reabertura ou exclusão. Concluída
permite apenas a entrega. Ações repetidas retornam 409, sem novo evento.

## Consulta do histórico

GET `/orders/1/history` retorna uma lista de eventos da ordem, do mais antigo
ao mais recente, ordenada por ID. Aceita `offset` (mínimo 0) e `limit` (1 a 100,
padrão 20); offset além do fim retorna lista vazia. Ordem inexistente retorna
404. Cada evento contém:

- `id`, `order_id` e `action`;
- `previous_status` (nulo apenas na abertura) e `resulting_status`;
- `created_at` em UTC;
- `observation` quando aplicável, incluindo motivo de rejeição/cancelamento;
- `approved_amount` para aprovação, serializado como string decimal.

Histórico é somente leitura. POST, PUT, PATCH e DELETE em `/history` retornam
405; não há endpoints de edição ou exclusão individual de eventos.

## Validação

`make check-backend` verifica lint, formatação e testes locais.
`make test-postgres` executa a suíte completa em PostgreSQL temporário isolado,
incluindo CRUD HTTP, persistência em nova conexão, evento inicial, cascata,
rollback, cliente inexistente, validações e bloqueios de edição/exclusão.
Os testes de orçamento cobrem valores limite, fluxo até reparo, rejeição com
motivo, estados inválidos, repetição de ações e rollback quando o evento falha.
Os testes de atendimento cobrem o fluxo até entrega, cancelamento nos estados
permitidos, imutabilidade dos estados finais, confirmação de entrega,
paginação e isolamento do histórico, rollback das novas transições e disputa
simultânea entre cancelamento e início de reparo.
