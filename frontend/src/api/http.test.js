import { describe, expect, it, vi } from "vitest";
import { request } from "./http";

describe("cliente HTTP", () => {
  it("usa a URL configurada e serializa JSON", async () => {
    vi.stubEnv("VITE_API_URL", "https://api.example.test/");
    const fetch = vi
      .fn()
      .mockResolvedValue(
        new Response(JSON.stringify({ id: 1 }), { status: 201 }),
      );
    vi.stubGlobal("fetch", fetch);
    await expect(
      request("/customers/", { method: "POST", body: { name: "Ana" } }),
    ).resolves.toEqual({ id: 1 });
    expect(fetch).toHaveBeenCalledWith(
      "https://api.example.test/customers/",
      expect.objectContaining({ method: "POST", body: '{"name":"Ana"}' }),
    );
  });
  it("aceita exclusão sem corpo", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(new Response(null, { status: 204 })),
    );
    await expect(
      request("/customers/1", { method: "DELETE" }),
    ).resolves.toBeNull();
  });
  it.each([404, 409])("preserva mensagens HTTP %s", async (status) => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(
        new Response(JSON.stringify({ detail: "Operação bloqueada." }), {
          status,
        }),
      ),
    );
    await expect(request("/orders/1")).rejects.toMatchObject({
      status,
      message: "Operação bloqueada.",
    });
  });
  it("exibe os campos inválidos de uma resposta 422", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(
        new Response(
          JSON.stringify({
            detail: [{ loc: ["body", "phone"], msg: "Telefone inválido" }],
          }),
          { status: 422 },
        ),
      ),
    );
    await expect(request("/customers/")).rejects.toThrow(
      "phone: Telefone inválido",
    );
  });
  it("trata falha de rede", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockRejectedValue(new TypeError("Failed to fetch")),
    );
    await expect(request("/orders/")).rejects.toMatchObject({
      status: 0,
      message: expect.stringContaining("conectar à API"),
    });
  });
  it("preserva cancelamento de requisição", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockRejectedValue(new DOMException("Aborted", "AbortError")),
    );
    await expect(request("/orders/")).rejects.toMatchObject({
      name: "AbortError",
    });
  });
  it.each([200, 500])("trata resposta não JSON em HTTP %s", async (status) => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(new Response("<html>erro</html>", { status })),
    );
    await expect(request("/orders/")).rejects.toMatchObject({ status });
  });
});
