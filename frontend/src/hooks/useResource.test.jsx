import { act, renderHook, waitFor } from "@testing-library/react";
import { expect, it, vi } from "vitest";
import { customers } from "../api/customers";
import { orders } from "../api/orders";
import { useResource } from "./useResource";

it("cancela leituras antigas e ignora respostas que chegam fora de ordem", async () => {
  const pending = [];
  const fetch = vi.fn(
    (_url, options) =>
      new Promise((resolve) =>
        pending.push({ resolve, signal: options.signal }),
      ),
  );
  vi.stubGlobal("fetch", fetch);
  const { result, rerender, unmount } = renderHook(
    ({ path }) => useResource(orders.get, { id: path }),
    { initialProps: { path: "1" } },
  );
  rerender({ path: "2" });
  expect(pending[0].signal.aborted).toBe(true);
  await act(async () => pending[1].resolve(new Response('{"id":2}')));
  await waitFor(() => expect(result.current.data).toEqual({ id: 2 }));
  await act(async () => pending[0].resolve(new Response('{"id":1}')));
  expect(result.current.data).toEqual({ id: 2 });
  unmount();
  expect(pending[1].signal.aborted).toBe(true);
});

it("uma nova tentativa substitui os dados e limpa o erro anterior", async () => {
  const fetch = vi
    .fn()
    .mockResolvedValueOnce(
      new Response('{"detail":"Indisponível"}', { status: 503 }),
    )
    .mockResolvedValueOnce(new Response("[]"));
  vi.stubGlobal("fetch", fetch);
  const { result } = renderHook(() => useResource(customers.list));
  await waitFor(() => expect(result.current.error).toBe("Indisponível"));
  act(() => result.current.reload());
  expect(result.current.loading).toBe(true);
  await waitFor(() => expect(result.current.data).toEqual([]));
  expect(result.current.error).toBe("");
});

it("troca o serviço mesmo quando os parâmetros são iguais", async () => {
  const pending = [];
  vi.stubGlobal(
    "fetch",
    vi.fn(
      (_url, options) =>
        new Promise((resolve) => {
          pending.push({ resolve, signal: options.signal });
        }),
    ),
  );
  const { result, rerender } = renderHook(
    ({ load }) => useResource(load, { id: 1 }),
    { initialProps: { load: customers.get } },
  );
  rerender({ load: orders.get });
  expect(pending[0].signal.aborted).toBe(true);
  await act(async () =>
    pending[1].resolve(new Response('{"id":1,"model":"Notebook"}')),
  );
  await waitFor(() => expect(result.current.data?.model).toBe("Notebook"));
  await act(async () =>
    pending[0].resolve(new Response('{"id":1,"name":"Ana"}')),
  );
  expect(result.current.data).toEqual({ id: 1, model: "Notebook" });
});
