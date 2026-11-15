import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { expect, it, vi } from "vitest";
import { ItemForm } from "../../src/components/ItemForm";

it("bloqueia novos envios enquanto salva e mantém campos em erro", async () => {
  let reject;
  const onAdd = vi.fn(
    () =>
      new Promise((_, fail) => {
        reject = fail;
      }),
  );
  const user = userEvent.setup();
  render(<ItemForm onAdd={onAdd} />);
  await user.type(screen.getByLabelText("Nome"), "Notebook");
  await user.click(screen.getByRole("button", { name: "Adicionar" }));
  expect(screen.getByRole("button", { name: "Salvando..." })).toBeDisabled();
  await user.click(screen.getByRole("button"));
  expect(onAdd).toHaveBeenCalledTimes(1);
  reject(new Error("Já existe um item com esse nome"));
  expect(await screen.findByRole("alert")).toHaveTextContent(
    "Já existe um item com esse nome",
  );
  expect(screen.getByLabelText("Nome")).toHaveValue("Notebook");
  expect(screen.getByRole("button", { name: "Adicionar" })).toBeEnabled();
});

it("mostra erro acessível e não adiciona nome vazio", async () => {
  const user = userEvent.setup();
  const onAdd = vi.fn();
  render(<ItemForm onAdd={onAdd} />);
  await user.click(screen.getByRole("button", { name: "Adicionar" }));
  expect(screen.getByRole("alert")).toHaveTextContent("O nome é obrigatório.");
  expect(screen.getByLabelText("Nome")).toHaveAttribute("aria-invalid", "true");
  expect(onAdd).not.toHaveBeenCalled();
});

it("envia valores normalizados, limpa campos e remove erro anterior", async () => {
  const user = userEvent.setup();
  const onAdd = vi.fn();
  render(<ItemForm onAdd={onAdd} />);
  await user.click(screen.getByRole("button", { name: "Adicionar" }));
  await user.type(screen.getByLabelText("Nome"), " Notebook ");
  await user.type(screen.getByLabelText("Descrição"), " 14 polegadas ");
  await user.click(screen.getByRole("button", { name: "Adicionar" }));
  expect(onAdd).toHaveBeenCalledExactlyOnceWith({
    name: "Notebook",
    description: "14 polegadas",
  });
  expect(screen.getByLabelText("Nome")).toHaveValue("");
  expect(screen.getByLabelText("Descrição")).toHaveValue("");
  expect(screen.queryByRole("alert")).not.toBeInTheDocument();
});

it("bloqueia nomes acima de 100 caracteres sem apagar os campos", async () => {
  const user = userEvent.setup();
  const onAdd = vi.fn();
  render(<ItemForm onAdd={onAdd} />);
  await user.type(screen.getByLabelText("Nome"), "a".repeat(101));
  await user.click(screen.getByRole("button", { name: "Adicionar" }));
  expect(screen.getByRole("alert")).toHaveTextContent(
    "no máximo 100 caracteres",
  );
  expect(screen.getByLabelText("Nome")).toHaveValue("a".repeat(101));
  expect(onAdd).not.toHaveBeenCalled();
});
