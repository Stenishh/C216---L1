import { expect, test } from "@playwright/test";

test.beforeEach(() => {
  if (!process.env.E2E_BASE_URL)
    throw new Error("Use make e2e para criar uma stack isolada.");
});

test("edita e exclui cliente e ordem sem andamento pela interface", async ({
  page,
}) => {
  const name = `CRUD E2E ${Date.now()}`;
  await page.goto("/customers/new");
  await page.getByLabel("Nome", { exact: true }).fill(name);
  await page.getByLabel("Telefone", { exact: true }).fill("35999998888");
  await page.getByRole("button", { name: "Salvar cliente" }).click();
  await expect(page.getByRole("heading", { name })).toBeVisible();
  const customerPath = new URL(page.url()).pathname;
  await page.getByRole("link", { name: "Editar cliente", exact: true }).click();
  await page.getByLabel("Nome", { exact: true }).fill(`${name} atualizado`);
  await page.getByRole("button", { name: "Salvar cliente" }).click();
  await expect(
    page.getByRole("heading", { name: `${name} atualizado` }),
  ).toBeVisible();
  await page.goto("/orders/new");
  await page.getByLabel("Buscar cliente por nome").fill(name);
  const select = page.getByRole("combobox", { name: /^Cliente/ });
  const option = select.locator("option").filter({ hasText: name });
  await expect(option).toHaveCount(1);
  await select.selectOption(await option.getAttribute("value"));
  await page.getByLabel("Marca", { exact: true }).fill("Dell");
  await page.getByLabel("Modelo", { exact: true }).fill("Modelo original");
  await page.getByLabel("Problema relatado").fill("Falha de energia");
  await page.getByRole("button", { name: "Salvar ordem" }).click();
  await page.getByRole("link", { name: "Editar dados de abertura" }).click();
  await page.getByLabel("Modelo", { exact: true }).fill("Modelo atualizado");
  await page.getByRole("button", { name: "Salvar ordem" }).click();
  await expect(
    page.getByText("Dell Modelo atualizado", { exact: true }),
  ).toBeVisible();
  await page
    .getByRole("button", { name: "Excluir ordem", exact: true })
    .click();
  await page
    .getByRole("button", { name: "Confirmar exclusão", exact: true })
    .click();
  await expect(page.getByText("Ordem excluída.")).toBeVisible();
  await page.goto(customerPath);
  await page
    .getByRole("button", { name: "Excluir cliente", exact: true })
    .click();
  await page
    .getByRole("button", { name: "Confirmar exclusão", exact: true })
    .click();
  await expect(page.getByText("Cliente excluído.")).toBeVisible();
  await page.reload();
  await expect(
    page.getByRole("link", { name: `${name} atualizado`, exact: true }),
  ).toHaveCount(0);
});

test("cliente, ordem, atendimento completo, filtros e persistência após reload", async ({
  page,
}) => {
  const name = `Cliente E2E ${Date.now()}`;
  await page.goto("/customers/new");
  await page.getByLabel("Nome", { exact: true }).fill(name);
  await page.getByLabel("Telefone", { exact: true }).fill("35999998888");
  await page.getByRole("button", { name: "Salvar cliente" }).click();
  await expect(page.getByRole("heading", { name })).toBeVisible();
  await page.reload();
  await expect(page.getByRole("heading", { name })).toBeVisible();
  await page.goto("/orders/new");
  await page.getByLabel("Buscar cliente por nome").fill(name);
  const option = page
    .getByRole("combobox", { name: /^Cliente/ })
    .locator("option")
    .filter({ hasText: name });
  await expect(option).toHaveCount(1);
  await page
    .getByRole("combobox", { name: /^Cliente/ })
    .selectOption(await option.getAttribute("value"));
  await page.getByLabel("Marca", { exact: true }).fill("Dell");
  await page.getByLabel("Modelo", { exact: true }).fill("Inspiron E2E");
  await page.getByLabel("Problema relatado").fill("Não liga");
  await page.getByRole("button", { name: "Salvar ordem" }).click();
  await expect(page.getByRole("heading", { name: /^Ordem #/ })).toBeVisible();
  const orderPath = new URL(page.url()).pathname;
  await page
    .getByRole("button", { name: "Iniciar diagnóstico", exact: true })
    .click();
  await page
    .getByLabel("Diagnóstico", { exact: true })
    .fill("Fonte defeituosa");
  await page.getByLabel("Orçamento (R$)").fill("0");
  await page.getByRole("button", { name: /Salvar diagnóstico/ }).click();
  await expect(page.getByText("Diagnóstico e orçamento salvos.")).toBeVisible();
  await page
    .getByRole("button", { name: "Solicitar aprovação", exact: true })
    .click();
  await page
    .getByRole("form", { name: "Confirmação da ação" })
    .getByRole("button", { name: "Solicitar aprovação", exact: true })
    .click();
  await page
    .getByRole("button", { name: "Registrar aprovação", exact: true })
    .click();
  await page
    .getByRole("button", { name: "Confirmar aprovação", exact: true })
    .click();
  await page
    .getByRole("button", { name: "Iniciar reparo", exact: true })
    .click();
  await page
    .getByLabel("Serviço realizado", { exact: true })
    .fill("Fonte substituída");
  await page.getByRole("button", { name: "Salvar serviço realizado" }).click();
  await expect(page.getByText("Serviço realizado salvo.")).toBeVisible();
  await page
    .getByRole("button", { name: "Concluir reparo", exact: true })
    .click();
  await page
    .getByRole("form", { name: "Confirmação da ação" })
    .getByRole("button", { name: "Concluir reparo", exact: true })
    .click();
  await page.getByRole("button", { name: "Registrar entrega" }).click();
  await page.getByRole("button", { name: "Confirmar entrega" }).click();
  await expect(page.getByText("Entrega registrada.")).toBeVisible();
  await page.reload();
  await expect(page.getByText(/Atendimento encerrado/)).toBeVisible();
  await expect(
    page.getByRole("heading", { name: "Equipamento entregue" }),
  ).toBeVisible();
  await page.goto("/orders");
  await page.getByLabel("Nome do cliente").fill(name);
  await page
    .getByRole("combobox", { name: /^Status/ })
    .selectOption("delivered");
  await page.getByRole("button", { name: "Filtrar ordens" }).click();
  await expect(page.locator(`a[href="${orderPath}"]`)).toBeVisible();
  await page.screenshot({
    path: test.info().outputPath("painel.png"),
    fullPage: true,
  });
  await page
    .getByRole("combobox", { name: /^Status/ })
    .selectOption("received");
  await page.getByRole("button", { name: "Filtrar ordens" }).click();
  await expect(page.getByText(/Nenhuma ordem nesta página/)).toBeVisible();
});
