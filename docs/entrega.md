# Demonstração e entrega do Repara

O vídeo deve mostrar a aplicação real, com narração do aluno. A duração
recomendada é de 5 a 10 minutos; não é necessário mostrar o rosto.

## Preparar a gravação

Abra a raiz do repositório em um terminal com Make, Docker e Poetry no PATH.
Revise o `.env` local sem exibir senhas na gravação. Para iniciar:

```bash
make up-build
make db-upgrade
make db-current
make ps
```

Abra http://127.0.0.1:8080 e http://127.0.0.1:8000/docs. Use dados fictícios.
Para mostrar testes locais, instale as dependências com
`make install frontend-install` e `make e2e-install` (Linux: `make e2e-install-deps`).
Execute `make check-all` antes de gravar; a suíte completa leva alguns minutos.

## Roteiro sugerido

| Tempo aproximado | O que mostrar e explicar |
| --- | --- |
| 0:00–0:45 | Tema: gestão de assistência técnica. Explique o problema e o acompanhamento da ordem desde o recebimento até a entrega. |
| 0:45–1:30 | Estrutura: React consome a API pelo proxy Nginx; FastAPI separa rotas, serviços e repositórios; SQLAlchemy persiste no PostgreSQL e Alembic versiona o schema. |
| 1:30–2:15 | Terminal: inicialização com `make up-build`, aplicação de migrations, revisão `0001 (head)` e os três serviços saudáveis com `make ps`. |
| 2:15–3:30 | Clientes: criar, consultar e editar. Crie também um cliente temporário sem ordens e exclua com confirmação. |
| 3:30–4:30 | Abra uma ordem para o cliente. Mostre consulta e edição dos dados de abertura. Para demonstrar exclusão, crie outra ordem sem andamento e exclua-a. |
| 4:30–6:30 | Na ordem principal: diagnóstico, orçamento, solicitação de aprovação, aprovação, início do reparo, serviço realizado, conclusão e entrega. Mostre histórico e filtros do painel. Explique uma regra, por exemplo a exigência de aprovação antes do reparo. |
| 6:30–7:15 | Recarregue a página da ordem e mostre os dados e o histórico preservados. Explique o banco e seu volume persistente. |
| 7:15–8:30 | Mostre os resultados locais e a aba Checks do PR final. Explique Pytest, testes de interface com HTTP simulado e E2E com os três serviços reais em stack isolada. |

## Conferência final

- Publicar o vídeo com acesso por link e testar o acesso sem estar autenticado.
- Inserir o link real na seção **Vídeo e entrega** do README, substituindo a pendência.
- Enviar a atualização do README para `projeto-final` e aguardar os Checks do PR.
- Manter o PR de `projeto-final` para `main` aberto, sem merge.
- Enviar no Teams os links do PR e do vídeo até 28/11/2026. O PR também dá
  acesso ao repositório e à branch `projeto-final`; o link do repositório pode
  ser incluído adicionalmente, conforme o PDF.
- Garantir acesso do monitor e do professor ao repositório e ao vídeo até o fim da avaliação.

O vídeo e o envio no Teams precisam ser concluídos pelo aluno. Não há exigência
de login JWT, deploy em nuvem, filas, cache ou serviços adicionais.
