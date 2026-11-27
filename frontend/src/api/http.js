export class ApiError extends Error {
  constructor(message, status = 0) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

function errorMessage(detail, status) {
  if (typeof detail === "string") return detail;
  if (Array.isArray(detail)) {
    return detail
      .map(
        (issue) =>
          `${issue.loc?.filter((part) => part !== "body").join(" / ") || "Dados"}: ${issue.msg}`,
      )
      .join("; ");
  }
  return `Não foi possível concluir a operação (HTTP ${status}). Tente novamente.`;
}

export async function request(path, { body, headers, ...options } = {}) {
  const base = (import.meta.env.VITE_API_URL || "/api").replace(/\/$/, "");
  let response;
  try {
    response = await fetch(`${base}${path}`, {
      ...options,
      headers: {
        Accept: "application/json",
        ...(body !== undefined ? { "Content-Type": "application/json" } : {}),
        ...headers,
      },
      ...(body !== undefined ? { body: JSON.stringify(body) } : {}),
    });
  } catch (error) {
    if (error.name === "AbortError") throw error;
    throw new ApiError(
      "Não foi possível conectar à API. Verifique a conexão e tente novamente.",
    );
  }
  if (response.status === 204) return null;
  const data = await response.json().catch(() => null);
  if (!response.ok)
    throw new ApiError(
      errorMessage(data?.detail, response.status),
      response.status,
    );
  if (data === null)
    throw new ApiError(
      "A API retornou uma resposta inválida. Tente novamente.",
      response.status,
    );
  return data;
}
