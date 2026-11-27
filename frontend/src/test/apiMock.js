import { vi } from "vitest";

export const customerFixture = {
  id: 1,
  name: "Ana Silva",
  phone: "35999998888",
  email: "ana@example.com",
  created_at: "2026-11-18T12:00:00Z",
};

export const orderFixture = {
  id: 7,
  customer_id: 1,
  equipment_type: "notebook",
  brand: "Dell",
  model: "Inspiron",
  serial_number: null,
  reported_problem: "Não liga",
  diagnosis: null,
  budget_amount: null,
  budget_decision: "not_requested",
  service_performed: null,
  cancellation_reason: null,
  status: "received",
  created_at: "2026-11-18T12:00:00Z",
  updated_at: "2026-11-18T12:00:00Z",
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
    const status = typeof result.status === "number" ? result.status : 200;
    const data = typeof result.status === "number" ? result.data : result;
    return new Response(status === 204 ? null : JSON.stringify(data), {
      status,
      headers: { "Content-Type": "application/json" },
    });
  });
  vi.stubGlobal("fetch", fetch);
  return fetch;
}
