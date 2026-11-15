import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, expect, it, vi } from "vitest";
import App from "../../src/App";

const json = (data, ok = true) => ({ ok, json: async () => data });
afterEach(() => vi.unstubAllGlobals());
it("mostra carregamento", () => {
  vi.stubGlobal(
    "fetch",
    vi.fn(() => new Promise(() => {})),
  );
  render(<App />);
  expect(screen.getByText("Carregando itens...")).toBeInTheDocument();
  expect(screen.getByRole("button")).toBeDisabled();
});
it("carrega itens persistidos", async () => {
  vi.stubGlobal(
    "fetch",
    vi.fn().mockResolvedValue(json([{ id: 1, name: "Existente" }])),
  );
  render(<App />);
  expect(await screen.findByText("Existente")).toBeInTheDocument();
});
it("valida e cadastra via POST", async () => {
  const mock = vi
    .fn()
    .mockResolvedValueOnce(json([]))
    .mockResolvedValueOnce(json({ id: 1, name: "Notebook" }));
  vi.stubGlobal("fetch", mock);
  const user = userEvent.setup();
  render(<App />);
  await screen.findByText("Nenhum item cadastrado.");
  await user.click(screen.getByRole("button"));
  expect(mock).toHaveBeenCalledTimes(1);
  await user.type(screen.getByLabelText("Nome"), "Notebook");
  await user.click(screen.getByRole("button"));
  expect(await screen.findByText("Notebook")).toBeInTheDocument();
  expect(mock).toHaveBeenLastCalledWith(
    expect.stringMatching(/\/items\/$/),
    expect.objectContaining({
      method: "POST",
      body: JSON.stringify({ name: "Notebook", description: null }),
    }),
  );
  expect(screen.getByLabelText("Nome")).toHaveValue("");
});
it("exibe erro de rede", async () => {
  vi.stubGlobal("fetch", vi.fn().mockRejectedValue(new TypeError()));
  render(<App />);
  expect(await screen.findByRole("alert")).toHaveTextContent("API");
});
it("preserva campos depois de 409", async () => {
  vi.stubGlobal(
    "fetch",
    vi
      .fn()
      .mockResolvedValueOnce(json([]))
      .mockResolvedValueOnce(json({ detail: "Duplicado" }, false)),
  );
  const user = userEvent.setup();
  render(<App />);
  await screen.findByText("Nenhum item cadastrado.");
  await user.type(screen.getByLabelText("Nome"), "Duplicado");
  await user.click(screen.getByRole("button"));
  expect(await screen.findByRole("alert")).toHaveTextContent("Duplicado");
  expect(screen.getByLabelText("Nome")).toHaveValue("Duplicado");
  expect(screen.getByRole("button")).toBeEnabled();
});
