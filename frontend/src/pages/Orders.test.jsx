import { render, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter } from "react-router-dom";
import { describe, expect, it } from "vitest";
import App from "../App";
import { customerFixture, mockApi, orderFixture } from "../test/apiMock";

function open(path = "/orders/7") {
  const user = userEvent.setup();
  render(
    <MemoryRouter initialEntries={[path]}>
      <App />
    </MemoryRouter>,
  );
  return user;
}

function scenario(overrides = {}, intercept) {
  let order = { ...orderFixture, ...overrides };
  let deleted = false;
  const history = [
    {
      id: 1,
      action: "open",
      previous_status: null,
      resulting_status: "received",
      observation: null,
      approved_amount: null,
      created_at: order.created_at,
    },
  ];
  const fetch = mockApi(async (path, method, body) => {
    const custom = await intercept?.(path, method, body);
    if (custom !== undefined) return custom;
    if (path.startsWith("/customers/?")) return [customerFixture];
    if (path === "/customers/1") return customerFixture;
    if (path.startsWith("/orders/7/history")) return history;
    if (path.startsWith("/orders/?")) return deleted ? [] : [order];
    if (path === "/orders/" && method === "POST") {
      order = { ...order, ...body };
      return { status: 201, data: order };
    }
    if (path === "/orders/7") {
      if (method === "DELETE") {
        deleted = true;
        return { status: 204 };
      }
      if (method === "PUT") order = { ...order, ...body };
      return order;
    }
    const action = path.split("/").at(-1);
    const previous = order.status;
    const statusByAction = {
      "begin-diagnosis": "in_diagnosis",
      "request-approval": "awaiting_approval",
      "start-repair": "in_repair",
      "complete-repair": "completed",
      deliver: "delivered",
      cancel: "cancelled",
      "reject-budget": "cancelled",
    };
    order = {
      ...order,
      ...body,
      status: statusByAction[action] || order.status,
    };
    if (action === "diagnosis" && body.budget_amount !== null)
      order.budget_amount = Number(body.budget_amount).toFixed(2);
    if (action === "request-approval") order.budget_decision = "pending";
    if (action === "approve-budget") order.budget_decision = "approved";
    if (action === "reject-budget") order.budget_decision = "rejected";
    if (action === "cancel" || action === "reject-budget")
      order.cancellation_reason = body.reason;
    if (method === "POST")
      history.push({
        id: history.length + 1,
        action: action.replaceAll("-", "_"),
        previous_status: previous,
        resulting_status: order.status,
        observation: body?.reason || null,
        approved_amount:
          action === "approve-budget" ? order.budget_amount : null,
        created_at: order.created_at,
      });
    return order;
  });
  return { fetch, getOrder: () => order };
}

describe("ordens e atendimento", () => {
  it("lista e abre o detalhe com cliente e histórico", async () => {
    scenario();
    const user = open("/orders");
    await user.click(await screen.findByRole("link", { name: "#7" }));
    expect(
      await screen.findByRole("heading", { name: "Ordem #7" }),
    ).toBeInTheDocument();
    expect(
      await screen.findByRole("link", { name: "Ana Silva" }),
    ).toBeInTheDocument();
    expect(
      await screen.findByRole("heading", { name: "Ordem aberta" }),
    ).toBeInTheDocument();
  });

  it("abre ordem com cliente selecionado e valores normalizados", async () => {
    const { fetch } = scenario();
    const user = open("/orders/new");
    await screen.findByRole("option", { name: /Ana Silva/ });
    await user.selectOptions(screen.getByLabelText("Cliente"), "1");
    await user.type(screen.getByLabelText("Marca"), "Dell");
    await user.type(screen.getByLabelText("Modelo"), "Inspiron");
    await user.type(screen.getByLabelText("Problema relatado"), "Não liga");
    await user.click(screen.getByRole("button", { name: "Salvar ordem" }));
    expect(await screen.findByText("Ordem aberta.")).toBeInTheDocument();
    expect(fetch).toHaveBeenCalledWith(
      "/api/orders/",
      expect.objectContaining({
        method: "POST",
        body: JSON.stringify({
          customer_id: 1,
          equipment_type: "notebook",
          brand: "Dell",
          model: "Inspiron",
          serial_number: null,
          reported_problem: "Não liga",
        }),
      }),
    );
  });

  it("edita dados de abertura enquanto Recebida", async () => {
    const { getOrder } = scenario();
    const user = open("/orders/7/edit");
    await user.type(
      await screen.findByLabelText("Número de série (opcional)"),
      "ABC123",
    );
    await user.click(screen.getByRole("button", { name: "Salvar ordem" }));
    expect(await screen.findByText("Ordem atualizada.")).toBeInTheDocument();
    expect(getOrder().serial_number).toBe("ABC123");
  });

  it("bloqueia rota de edição depois do recebimento", async () => {
    scenario({ status: "in_repair", budget_decision: "approved" });
    open("/orders/7/edit");
    expect(
      await screen.findByRole("heading", { name: "Edição indisponível" }),
    ).toBeInTheDocument();
    expect(
      screen.queryByRole("button", { name: "Salvar ordem" }),
    ).not.toBeInTheDocument();
  });

  it("executa o fluxo completo até entrega com orçamento zero e histórico atualizado", async () => {
    const { fetch, getOrder } = scenario();
    const user = open();
    await user.click(
      await screen.findByRole("button", { name: "Iniciar diagnóstico" }),
    );
    await user.type(
      await screen.findByLabelText("Diagnóstico"),
      "Conector solto",
    );
    await user.type(screen.getByLabelText("Orçamento (R$)"), "0");
    expect(
      screen.getByRole("button", { name: "Solicitar aprovação" }),
    ).toBeDisabled();
    await user.click(
      screen.getByRole("button", { name: "Salvar diagnóstico e orçamento" }),
    );
    await waitFor(() =>
      expect(
        screen.getByRole("button", { name: "Solicitar aprovação" }),
      ).toBeEnabled(),
    );
    await user.click(
      screen.getByRole("button", { name: "Solicitar aprovação" }),
    );
    await user.click(
      within(
        screen.getByRole("form", { name: "Confirmação da ação" }),
      ).getByRole("button", { name: "Solicitar aprovação" }),
    );
    await user.click(
      await screen.findByRole("button", { name: "Registrar aprovação" }),
    );
    await user.click(
      screen.getByRole("button", { name: "Confirmar aprovação" }),
    );
    await user.click(
      await screen.findByRole("button", { name: "Iniciar reparo" }),
    );
    await user.type(
      await screen.findByLabelText("Serviço realizado"),
      "Conector fixado",
    );
    expect(
      screen.getByRole("button", { name: "Concluir reparo" }),
    ).toBeDisabled();
    await user.click(
      screen.getByRole("button", { name: "Salvar serviço realizado" }),
    );
    await waitFor(() =>
      expect(
        screen.getByRole("button", { name: "Concluir reparo" }),
      ).toBeEnabled(),
    );
    await user.click(screen.getByRole("button", { name: "Concluir reparo" }));
    await user.click(
      within(
        screen.getByRole("form", { name: "Confirmação da ação" }),
      ).getByRole("button", { name: "Concluir reparo" }),
    );
    await user.click(
      await screen.findByRole("button", { name: "Registrar entrega" }),
    );
    expect(getOrder().status).toBe("completed");
    await user.click(screen.getByRole("button", { name: "Confirmar entrega" }));
    expect(await screen.findByText("Entrega registrada.")).toBeInTheDocument();
    expect(
      await screen.findByRole("heading", { name: "Equipamento entregue" }),
    ).toBeInTheDocument();
    expect(screen.getByText(/Atendimento encerrado/)).toBeInTheDocument();
    expect(fetch).toHaveBeenCalledWith(
      "/api/orders/7/deliver",
      expect.objectContaining({ method: "POST", body: '{"confirmed":true}' }),
    );
    expect(fetch).toHaveBeenCalledWith(
      "/api/orders/7/diagnosis",
      expect.objectContaining({
        method: "PATCH",
        body: '{"diagnosis":"Conector solto","budget_amount":"0"}',
      }),
    );
    expect(getOrder().status).toBe("delivered");
  }, 20000);

  it("rejeita orçamento somente após motivo e confirmação", async () => {
    const { getOrder } = scenario({
      status: "awaiting_approval",
      budget_decision: "pending",
      diagnosis: "Fonte defeituosa",
      budget_amount: "150.90",
    });
    const user = open();
    await user.click(
      await screen.findByRole("button", { name: "Rejeitar orçamento" }),
    );
    await user.click(
      screen.getByRole("button", { name: "Confirmar rejeição" }),
    );
    expect(getOrder().status).toBe("awaiting_approval");
    await user.type(
      screen.getByLabelText("Motivo"),
      "Cliente não aprovou o custo",
    );
    await user.click(
      screen.getByRole("button", { name: "Confirmar rejeição" }),
    );
    expect(
      await screen.findByText(/Atendimento encerrado/),
    ).toBeInTheDocument();
    expect(getOrder().budget_decision).toBe("rejected");
    expect(getOrder().cancellation_reason).toBe("Cliente não aprovou o custo");
  });

  it("cancela com motivo sem excluir a ordem", async () => {
    const { getOrder, fetch } = scenario();
    const user = open();
    await user.click(
      await screen.findByRole("button", { name: "Cancelar ordem" }),
    );
    await user.type(screen.getByLabelText("Motivo"), "Cliente desistiu");
    await user.click(
      screen.getByRole("button", { name: "Confirmar cancelamento" }),
    );
    expect(
      await screen.findByRole("heading", { name: "Ordem cancelada" }),
    ).toBeInTheDocument();
    expect(getOrder().cancellation_reason).toBe("Cliente desistiu");
    expect(
      fetch.mock.calls.some(([, options]) => options.method === "DELETE"),
    ).toBe(false);
  });

  it("exige confirmação para exclusão sem andamento", async () => {
    const { fetch } = scenario();
    const user = open();
    await user.click(
      await screen.findByRole("button", { name: "Excluir ordem" }),
    );
    await user.click(
      screen.getByRole("button", { name: "Voltar sem confirmar" }),
    );
    expect(
      fetch.mock.calls.some(([, options]) => options.method === "DELETE"),
    ).toBe(false);
    await user.click(screen.getByRole("button", { name: "Excluir ordem" }));
    await user.click(
      screen.getByRole("button", { name: "Confirmar exclusão" }),
    );
    expect(await screen.findByText("Ordem excluída.")).toBeInTheDocument();
    expect(
      await screen.findByText(/Nenhuma ordem nesta página/),
    ).toBeInTheDocument();
  });

  it("mantém diagnóstico digitado em conflito e permite atualizar estado", async () => {
    scenario({ status: "in_diagnosis" }, (path, method) =>
      method === "PATCH" && path.endsWith("/diagnosis")
        ? {
            status: 409,
            data: { detail: "Diagnóstico bloqueado pelo andamento da ordem." },
          }
        : undefined,
    );
    const user = open();
    await user.type(
      await screen.findByLabelText("Diagnóstico"),
      "Fonte defeituosa",
    );
    await user.type(screen.getByLabelText("Orçamento (R$)"), "150.90");
    await user.click(
      screen.getByRole("button", { name: "Salvar diagnóstico e orçamento" }),
    );
    expect(await screen.findByRole("alert")).toHaveTextContent(
      "Diagnóstico bloqueado",
    );
    expect(screen.getByLabelText("Diagnóstico")).toHaveValue(
      "Fonte defeituosa",
    );
    expect(
      screen.getByRole("button", { name: "Atualizar dados da ordem" }),
    ).toBeEnabled();
  });

  it("desabilita ações durante envio para impedir requisições duplicadas", async () => {
    let finish;
    const { fetch } = scenario({}, (path) =>
      path.endsWith("/begin-diagnosis")
        ? new Promise((resolve) => {
            finish = resolve;
          })
        : undefined,
    );
    const user = open();
    await user.click(
      await screen.findByRole("button", { name: "Iniciar diagnóstico" }),
    );
    expect(
      screen.getByRole("button", { name: "Iniciar diagnóstico" }),
    ).toBeDisabled();
    expect(
      screen.getByRole("button", { name: "Cancelar ordem" }),
    ).toBeDisabled();
    finish({ ...orderFixture, status: "in_diagnosis" });
    await screen.findByLabelText("Diagnóstico");
    expect(
      fetch.mock.calls.filter(([url]) => url.endsWith("/begin-diagnosis")),
    ).toHaveLength(1);
  });

  it.each(["in_repair", "completed", "delivered", "cancelled"])(
    "não oferece cancelamento ou exclusão em %s",
    async (status) => {
      scenario({ status, budget_decision: "approved" });
      open();
      await screen.findByRole("heading", { name: "Ordem #7" });
      expect(
        screen.queryByRole("button", { name: "Cancelar ordem" }),
      ).not.toBeInTheDocument();
      expect(
        screen.queryByRole("button", { name: "Excluir ordem" }),
      ).not.toBeInTheDocument();
      expect(
        screen.queryByRole("link", { name: "Editar dados de abertura" }),
      ).not.toBeInTheDocument();
    },
  );

  it("pagina o histórico de leitura", async () => {
    const { fetch } = scenario({}, (path) =>
      path.startsWith("/orders/7/history")
        ? path.includes("offset=20")
          ? []
          : Array.from({ length: 20 }, (_, i) => ({
              id: i + 1,
              action: "open",
              previous_status: null,
              resulting_status: "received",
              created_at: orderFixture.created_at,
            }))
        : undefined,
    );
    const user = open();
    const history = await screen.findByRole("region", {
      name: "Histórico de atendimento",
    });
    await within(history).findAllByRole("heading", { name: "Ordem aberta" });
    await user.click(
      within(history).getByRole("button", { name: "Próxima página" }),
    );
    expect(
      await within(history).findByText("Nenhum evento nesta página."),
    ).toBeInTheDocument();
    expect(fetch).toHaveBeenCalledWith(
      "/api/orders/7/history?offset=20&limit=20",
      expect.anything(),
    );
  });

  it("preserva os dados de abertura quando a API rejeita o cliente", async () => {
    scenario({}, (path, method) =>
      path === "/orders/" && method === "POST"
        ? { status: 404, data: { detail: "Cliente não encontrado." } }
        : undefined,
    );
    const user = open("/orders/new");
    await screen.findByRole("option", { name: /Ana Silva/ });
    await user.selectOptions(screen.getByLabelText("Cliente"), "1");
    await user.type(screen.getByLabelText("Marca"), "Dell");
    await user.type(screen.getByLabelText("Modelo"), "Inspiron");
    await user.type(screen.getByLabelText("Problema relatado"), "Não liga");
    await user.click(screen.getByRole("button", { name: "Salvar ordem" }));
    expect(await screen.findByRole("alert")).toHaveTextContent(
      "Cliente não encontrado",
    );
    expect(screen.getByLabelText("Problema relatado")).toHaveValue("Não liga");
    expect(screen.getByLabelText("Cliente")).toHaveValue("1");
  });
});
