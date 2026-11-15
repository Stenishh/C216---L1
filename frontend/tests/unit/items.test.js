import { afterEach, expect, it, vi } from "vitest";
import { createItem, listItems } from "../../src/services/items";

afterEach(() => vi.unstubAllGlobals());
it("GET retorna JSON e usa barra final", async () => {
  const mock = vi.fn().mockResolvedValue({ ok: true, json: async () => [] });
  vi.stubGlobal("fetch", mock);
  expect(await listItems()).toEqual([]);
  expect(mock).toHaveBeenCalledWith(
    expect.stringMatching(/\/items\/$/),
    undefined,
  );
});
it("POST envia JSON e normaliza descricao vazia", async () => {
  const mock = vi
    .fn()
    .mockResolvedValue({ ok: true, json: async () => ({ id: 1 }) });
  vi.stubGlobal("fetch", mock);
  await createItem({ name: "Item", description: "" });
  expect(mock).toHaveBeenCalledWith(expect.any(String), {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name: "Item", description: null }),
  });
});
it.each([{ detail: [] }, {}, null])(
  "erro sem detail textual: %j",
  async (body) => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({ ok: false, json: async () => body }),
    );
    await expect(listItems()).rejects.toThrow("Erro ao carregar os itens.");
  },
);
it("erro nao JSON", async () => {
  vi.stubGlobal(
    "fetch",
    vi.fn().mockResolvedValue({
      ok: false,
      json: async () => {
        throw new SyntaxError();
      },
    }),
  );
  await expect(createItem({ name: "Item" })).rejects.toThrow(
    "Erro ao cadastrar o item.",
  );
});
it("falha de rede", async () => {
  vi.stubGlobal("fetch", vi.fn().mockRejectedValue(new TypeError()));
  await expect(listItems()).rejects.toThrow("API");
});
