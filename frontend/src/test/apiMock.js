import { vi } from "vitest";

export const customerFixture = {
  id: 1,
  name: "Ana Silva",
  phone: "35999998888",
  email: "ana@example.com",
  created_at: "2026-11-18T12:00:00Z",
};

export function mockApi(handler) {
  const fetch = vi.fn(async (url, options = {}) => {
    const path = String(url).replace(/^\/api/, "");
    const body = options.body ? JSON.parse(options.body) : undefined;
    const result = await handler(path, options.method || "GET", body, options);
    if (result === undefined)
      throw new Error(
        `Requisição não simulada: ${options.method || "GET"} ${path}`,
      );
    const { status = 200, data = result } = result;
    return new Response(status === 204 ? null : JSON.stringify(data), {
      status,
      headers: { "Content-Type": "application/json" },
    });
  });
  vi.stubGlobal("fetch", fetch);
  return fetch;
}
