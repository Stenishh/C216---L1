import { render, screen, within } from "@testing-library/react";
import { expect, it } from "vitest";
import { ItemList } from "../../src/components/ItemList";

it("exibe estado vazio", () => {
  render(<ItemList items={[]} />);
  expect(screen.getByText("Nenhum item cadastrado.")).toBeInTheDocument();
  expect(screen.queryByRole("list")).not.toBeInTheDocument();
});

it("lista itens com e sem descrição", () => {
  render(
    <ItemList
      items={[
        { id: "1", name: "Notebook", description: "14 polegadas" },
        { id: "2", name: "Mouse", description: "" },
      ]}
    />,
  );
  const items = screen.getAllByRole("listitem");
  expect(items).toHaveLength(2);
  expect(within(items[0]).getByText("14 polegadas")).toBeInTheDocument();
  expect(items[1]).toHaveTextContent(/^Mouse$/);
});
