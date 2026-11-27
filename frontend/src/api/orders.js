import { request } from "./http";

const change = (id, action, body, method = "POST") =>
  request(`/orders/${id}/${action}`, {
    method,
    ...(body !== undefined ? { body } : {}),
  });

export const orders = {
  list: (params = {}, options) =>
    request(`/orders/?${new URLSearchParams(params)}`, options),
  get: ({ id }, options) => request(`/orders/${id}`, options),
  summary: (_params, options) => request("/orders/summary", options),
  history: ({ id, ...params }, options) =>
    request(`/orders/${id}/history?${new URLSearchParams(params)}`, options),
  create: (body) => request("/orders/", { method: "POST", body }),
  replace: (id, body) => request(`/orders/${id}`, { method: "PUT", body }),
  update: (id, body) => request(`/orders/${id}`, { method: "PATCH", body }),
  remove: (id) => request(`/orders/${id}`, { method: "DELETE" }),
  beginDiagnosis: (id) => change(id, "begin-diagnosis"),
  saveDiagnosis: (id, body) => change(id, "diagnosis", body, "PATCH"),
  requestApproval: (id) => change(id, "request-approval"),
  approveBudget: (id) => change(id, "approve-budget"),
  rejectBudget: (id, body) => change(id, "reject-budget", body),
  startRepair: (id) => change(id, "start-repair"),
  saveRepair: (id, body) => change(id, "repair", body, "PATCH"),
  completeRepair: (id) => change(id, "complete-repair"),
  deliver: (id, body) => change(id, "deliver", body),
  cancel: (id, body) => change(id, "cancel", body),
};

export const orderActions = {
  "begin-diagnosis": orders.beginDiagnosis,
  diagnosis: orders.saveDiagnosis,
  "request-approval": orders.requestApproval,
  "approve-budget": orders.approveBudget,
  "reject-budget": orders.rejectBudget,
  "start-repair": orders.startRepair,
  repair: orders.saveRepair,
  "complete-repair": orders.completeRepair,
  deliver: orders.deliver,
  cancel: orders.cancel,
};
