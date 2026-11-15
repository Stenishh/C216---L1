import { randomUUID } from "node:crypto";
import { expect, test } from "@playwright/test";

test("cadastra, persiste apos reload e rejeita duplicado", async ({ page }) => {
  const name = `Notebook-${Date.now()}-${randomUUID()}`;
  await page.goto("/");
  await expect(page.getByRole("button", { name: "Adicionar" })).toBeEnabled();
  await page.getByRole("button", { name: "Adicionar" }).click();
  await expect(page.getByRole("alert")).toBeVisible();
  await page.getByLabel("Nome", { exact: true }).fill(name);
  const response = page.waitForResponse(
    (r) => r.url().endsWith("/items/") && r.request().method() === "POST",
  );
  await page.getByRole("button", { name: "Adicionar" }).click();
  expect((await response).status()).toBe(201);
  const item = page.getByRole("listitem").filter({ hasText: name });
  await expect(item).toBeVisible();
  await expect(page.getByLabel("Nome", { exact: true })).toHaveValue("");
  await page.reload();
  await expect(item).toBeVisible();
  await page.getByLabel("Nome", { exact: true }).fill(name);
  await page.getByRole("button", { name: "Adicionar" }).click();
  await expect(page.getByRole("alert")).toContainText("esse nome");
  await expect(page.getByLabel("Nome", { exact: true })).toHaveValue(name);
  await expect(item).toHaveCount(1);
  expect(
    await page.evaluate(
      () => document.documentElement.scrollWidth <= window.innerWidth,
    ),
  ).toBe(true);
});
