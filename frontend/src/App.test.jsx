import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter } from "react-router-dom";
import { expect, it } from "vitest";
import App from "./App";

it("navega entre as áreas de atendimento", async () => {
  const user = userEvent.setup();
  render(
    <MemoryRouter>
      <App />
    </MemoryRouter>,
  );
  expect(
    screen.getByRole("heading", { name: "Ordens de serviço" }),
  ).toBeInTheDocument();
  await user.click(screen.getByRole("link", { name: "Clientes" }));
  expect(screen.getByRole("heading", { name: "Clientes" })).toBeInTheDocument();
});
