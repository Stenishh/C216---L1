import { request } from "./http";

export const customers = {
  list: (params = {}, options) =>
    request(`/customers/?${new URLSearchParams(params)}`, options),
  get: ({ id }, options) => request(`/customers/${id}`, options),
  create: (body) => request("/customers/", { method: "POST", body }),
  replace: (id, body) => request(`/customers/${id}`, { method: "PUT", body }),
  update: (id, body) => request(`/customers/${id}`, { method: "PATCH", body }),
  remove: (id) => request(`/customers/${id}`, { method: "DELETE" }),
};
