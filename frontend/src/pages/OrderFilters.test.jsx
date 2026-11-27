import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter } from "react-router-dom";
import { expect, it } from "vitest";
import App from "../App";
import { mockApi } from "../test/apiMock";

it("combina filtros, mostra totais e permite limpar a busca vazia", async () => {
  const fetch = mockApi((path) =>
    path === "/orders/summary"
      ? { open: 23, awaiting_approval: 4, ready_for_delivery: 2 }
      : [],
  );
  const user = userEvent.setup();
  render(
    <MemoryRouter initialEntries={["/orders"]}>
      <App />
    </MemoryRouter>,
  );
  expect(await screen.findByText("23")).toBeInTheDocument();
  await user.type(screen.getByLabelText("Número da ordem"), "7");
  await user.type(screen.getByLabelText("Nome do cliente"), "Ana Silva");
  await user.selectOptions(screen.getByLabelText("Status"), "received");
  await user.click(screen.getByRole("button", { name: "Filtrar ordens" }));
  await waitFor(() =>
    expect(
      fetch.mock.calls.some(([url]) =>
        String(url).includes("order_id=7&customer=Ana+Silva&status=received"),
      ),
    ).toBe(true),
  );
  expect(
    await screen.findByText(/Nenhuma ordem nesta página/),
  ).toBeInTheDocument();
  await user.click(screen.getByRole("button", { name: "Limpar filtros" }));
  expect(screen.getByLabelText("Nome do cliente")).toHaveValue("");
  await user.click(screen.getByRole("button", { name: "Atualizar dados" }));
  await waitFor(() =>
    expect(
      fetch.mock.calls.filter(([url]) =>
        String(url).endsWith("/orders/summary"),
      ).length,
    ).toBe(2),
  );
});
