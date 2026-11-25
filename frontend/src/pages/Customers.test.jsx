import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter } from "react-router-dom";
import { describe, expect, it } from "vitest";
import App from "../App";
import { customerFixture as customer, mockApi } from "../test/apiMock";

function open(path) {
  const user = userEvent.setup();
  render(
    <MemoryRouter initialEntries={[path]}>
      <App />
    </MemoryRouter>,
  );
  return user;
}

describe("gestão de clientes", () => {
  it("lista e consulta os dados completos de um cliente", async () => {
    const fetch = mockApi((path) =>
      path.startsWith("/customers/?") ? [customer] : customer,
    );
    const user = open("/customers");
    await user.click(await screen.findByRole("link", { name: customer.name }));
    expect(
      await screen.findByRole("heading", { name: customer.name }),
    ).toBeInTheDocument();
    expect(screen.getByText(customer.email)).toBeInTheDocument();
    expect(fetch).toHaveBeenCalledWith("/api/customers/1", expect.anything());
  });

  it("cadastra cliente e informa sucesso", async () => {
    let saved;
    mockApi((path, method, body) => {
      if (method === "POST") {
        saved = body;
        return { ...customer, ...body };
      }
      if (path === "/customers/1") return { ...customer, ...saved };
      return [];
    });
    const user = open("/customers/new");
    await user.type(screen.getByLabelText("Nome"), "Ana Silva");
    await user.type(screen.getByLabelText("Telefone"), "35999998888");
    await user.click(screen.getByRole("button", { name: "Salvar cliente" }));
    expect(await screen.findByText("Cliente cadastrado.")).toBeInTheDocument();
    expect(saved).toEqual({
      name: customer.name,
      phone: customer.phone,
      email: null,
    });
  });

  it("edita cadastro e permite remover e-mail", async () => {
    let saved = customer;
    const fetch = mockApi((_path, method, body) => {
      if (method === "PUT") saved = { ...customer, ...body };
      return saved;
    });
    const user = open("/customers/1/edit");
    await user.clear(await screen.findByLabelText("Nome"));
    await user.type(screen.getByLabelText("Nome"), "Ana Souza");
    await user.clear(screen.getByLabelText("E-mail (opcional)"));
    await user.click(screen.getByRole("button", { name: "Salvar cliente" }));
    expect(await screen.findByText("Cliente atualizado.")).toBeInTheDocument();
    expect(fetch).toHaveBeenCalledWith(
      "/api/customers/1",
      expect.objectContaining({
        method: "PUT",
        body: JSON.stringify({
          name: "Ana Souza",
          phone: customer.phone,
          email: null,
        }),
      }),
    );
  });

  it("preserva formulário após falha e permite tentar de novo", async () => {
    let fail = true;
    mockApi((_path, method, body) => {
      if (method === "POST" && fail)
        return {
          status: 422,
          data: { detail: "Revise o telefone informado." },
        };
      return { ...customer, ...body };
    });
    const user = open("/customers/new");
    await user.type(screen.getByLabelText("Nome"), "Ana Silva");
    await user.type(screen.getByLabelText("Telefone"), "35999998888");
    await user.click(screen.getByRole("button", { name: "Salvar cliente" }));
    expect(await screen.findByRole("alert")).toHaveTextContent(
      "Revise o telefone",
    );
    expect(screen.getByLabelText("Nome")).toHaveValue("Ana Silva");
    fail = false;
    await user.click(screen.getByRole("button", { name: "Salvar cliente" }));
    expect(await screen.findByText("Cliente cadastrado.")).toBeInTheDocument();
  });

  it("exige confirmação e mostra conflito de vínculo sem apagar cadastro", async () => {
    const fetch = mockApi((_path, method) =>
      method === "DELETE"
        ? {
            status: 409,
            data: {
              detail:
                "Não é possível excluir um cliente com ordens não canceladas vinculadas.",
            },
          }
        : customer,
    );
    const user = open("/customers/1");
    await user.click(
      await screen.findByRole("button", { name: "Excluir cliente" }),
    );
    expect(
      fetch.mock.calls.some(([, options]) => options.method === "DELETE"),
    ).toBe(false);
    await user.click(
      screen.getByRole("button", { name: "Confirmar exclusão" }),
    );
    expect(await screen.findByRole("alert")).toHaveTextContent(
      "ordens não canceladas vinculadas",
    );
    expect(
      screen.getByRole("heading", { name: customer.name }),
    ).toBeInTheDocument();
    await user.click(screen.getByRole("button", { name: "Manter cliente" }));
    expect(
      screen.queryByRole("group", { name: "Confirmar exclusão" }),
    ).not.toBeInTheDocument();
  });

  it("exclui e atualiza a listagem", async () => {
    let deleted = false;
    mockApi((path, method) => {
      if (method === "DELETE") {
        deleted = true;
        return { status: 204 };
      }
      return path === "/customers/1" ? customer : [];
    });
    const user = open("/customers/1");
    await user.click(
      await screen.findByRole("button", { name: "Excluir cliente" }),
    );
    await user.click(
      screen.getByRole("button", { name: "Confirmar exclusão" }),
    );
    expect(await screen.findByText("Cliente excluído.")).toBeInTheDocument();
    expect(
      await screen.findByText(/Nenhum cliente nesta página/),
    ).toBeInTheDocument();
    expect(deleted).toBe(true);
  });

  it("bloqueia envio duplicado enquanto aguarda a API", async () => {
    let finish;
    const fetch = mockApi((_path, method) =>
      method === "POST"
        ? new Promise((resolve) => {
            finish = resolve;
          })
        : customer,
    );
    const user = open("/customers/new");
    await user.type(screen.getByLabelText("Nome"), "Ana Silva");
    await user.type(screen.getByLabelText("Telefone"), "35999998888");
    await user.click(screen.getByRole("button", { name: "Salvar cliente" }));
    expect(screen.getByRole("button", { name: "Salvando…" })).toBeDisabled();
    expect(screen.getByLabelText("Nome")).toBeDisabled();
    finish(customer);
    await screen.findByText("Cliente cadastrado.");
    expect(
      fetch.mock.calls.filter(([, options]) => options.method === "POST"),
    ).toHaveLength(1);
  });

  it("trata carregamento, erro e nova tentativa na listagem", async () => {
    let fail = true;
    mockApi(() =>
      fail ? { status: 503, data: { detail: "Serviço indisponível." } } : [],
    );
    const user = open("/customers");
    expect(screen.getByRole("status")).toHaveTextContent("Carregando");
    expect(await screen.findByRole("alert")).toHaveTextContent(
      "Serviço indisponível",
    );
    fail = false;
    await user.click(screen.getByRole("button", { name: "Tentar novamente" }));
    await waitFor(() =>
      expect(
        screen.getByText(/Nenhum cliente nesta página/),
      ).toBeInTheDocument(),
    );
  });

  it("pagina os clientes sem limitar o acesso aos primeiros vinte", async () => {
    const fetch = mockApi((path) =>
      path.includes("offset=20")
        ? []
        : Array.from({ length: 20 }, (_, i) => ({
            ...customer,
            id: i + 1,
            name: `Cliente ${i + 1}`,
          })),
    );
    const user = open("/customers");
    await screen.findByRole("link", { name: "Cliente 20" });
    await user.click(screen.getByRole("button", { name: "Próxima página" }));
    expect(
      await screen.findByText(/Nenhum cliente nesta página/),
    ).toBeInTheDocument();
    expect(fetch).toHaveBeenCalledWith(
      "/api/customers/?offset=20&limit=20",
      expect.anything(),
    );
    expect(
      screen.getByRole("button", { name: "Página anterior" }),
    ).toBeEnabled();
  });
});
