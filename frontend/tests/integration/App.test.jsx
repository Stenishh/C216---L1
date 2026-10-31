import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { expect, it } from "vitest";
import App from "../../src/App";

it("cadastra vários itens mantendo a lista e aceita descrição vazia", async () => {
  const user = userEvent.setup();
  render(<App />);
  expect(screen.getByText("Nenhum item cadastrado.")).toBeInTheDocument();
  await user.type(screen.getByLabelText("Nome"), "Notebook");
  await user.type(screen.getByLabelText("Descrição"), "14 polegadas");
  await user.click(screen.getByRole("button", { name: "Adicionar" }));
  expect(screen.getByText("Notebook")).toBeInTheDocument();
  expect(screen.getByText("14 polegadas")).toBeInTheDocument();
  expect(screen.queryByText("Nenhum item cadastrado.")).not.toBeInTheDocument();
  await user.type(screen.getByLabelText("Nome"), "Mouse");
  await user.click(screen.getByRole("button", { name: "Adicionar" }));
  expect(screen.getAllByRole("listitem")).toHaveLength(2);
  expect(screen.getByRole("status")).toHaveTextContent("2 itens cadastrados");
});

it("mantém o estado vazio após tentativa inválida", async () => {
  const user = userEvent.setup();
  render(<App />);
  await user.click(screen.getByRole("button", { name: "Adicionar" }));
  expect(screen.getByRole("alert")).toBeInTheDocument();
  expect(screen.queryByRole("listitem")).not.toBeInTheDocument();
});
