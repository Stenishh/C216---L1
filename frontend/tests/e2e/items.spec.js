import { expect, test } from "@playwright/test";

test("carrega a interface responsiva", async ({ page }) => {
  await page.goto("/");
  await expect(
    page.getByRole("heading", { name: "Gerenciador de Itens" }),
  ).toBeVisible();
  await expect(page.getByText("Nenhum item cadastrado.")).toBeVisible();
  await expect(page.getByRole("button", { name: "Adicionar" })).toBeVisible();
  expect(
    await page.evaluate(
      () => document.documentElement.scrollWidth <= window.innerWidth,
    ),
  ).toBe(true);
});

test("valida nome vazio e permite corrigir o cadastro", async ({ page }) => {
  await page.goto("/");
  await page.getByRole("button", { name: "Adicionar" }).click();
  await expect(page.getByRole("alert")).toHaveText("O nome é obrigatório.");
  await expect(page.getByRole("listitem")).toHaveCount(0);
  await page.getByLabel("Nome", { exact: true }).fill("Mouse");
  await page.getByRole("button", { name: "Adicionar" }).click();
  await expect(page.getByRole("listitem")).toHaveText("Mouse");
  await expect(page.getByRole("alert")).toHaveCount(0);
});

test("cadastra itens em memória sem chamadas à API e limpa ao recarregar", async ({
  page,
}) => {
  const apiRequests = [];
  page.on("request", (request) => {
    if (["fetch", "xhr"].includes(request.resourceType()))
      apiRequests.push(request.url());
  });
  await page.goto("/");
  await page.getByLabel("Nome", { exact: true }).fill(" Notebook ");
  await page.getByLabel("Descrição", { exact: true }).fill("14 polegadas");
  await page.getByRole("button", { name: "Adicionar" }).click();
  await expect(page.getByRole("listitem")).toContainText("Notebook");
  await expect(page.getByRole("listitem")).toContainText("14 polegadas");
  await expect(page.getByText("Nenhum item cadastrado.")).toBeHidden();
  await expect(page.getByLabel("Nome", { exact: true })).toHaveValue("");
  await expect(page.getByLabel("Descrição", { exact: true })).toHaveValue("");
  await page.getByLabel("Nome", { exact: true }).fill("a".repeat(100));
  await page.getByRole("button", { name: "Adicionar" }).click();
  await expect(page.getByRole("listitem")).toHaveCount(2);
  expect(
    await page.evaluate(
      () => document.documentElement.scrollWidth <= window.innerWidth,
    ),
  ).toBe(true);
  await page.reload();
  await expect(page.getByText("Nenhum item cadastrado.")).toBeVisible();
  expect(apiRequests).toEqual([]);
});
