/**
 * Minimal API client: attaches the JWT, refreshes it once on 401,
 * and throws ApiError with the server's message otherwise.
 */

const BASE = "/api";

export class ApiError extends Error {
  status: number;
  constructor(status: number, message: string) {
    super(message);
    this.status = status;
  }
}

export function getToken() {
  return localStorage.getItem("access");
}

export function setTokens(access: string, refresh?: string) {
  localStorage.setItem("access", access);
  if (refresh) localStorage.setItem("refresh", refresh);
}

export function clearTokens() {
  localStorage.removeItem("access");
  localStorage.removeItem("refresh");
}

async function tryRefresh(): Promise<boolean> {
  const refresh = localStorage.getItem("refresh");
  if (!refresh) return false;
  const res = await fetch(`${BASE}/auth/refresh/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ refresh }),
  });
  if (!res.ok) return false;
  const data = await res.json();
  setTokens(data.access);
  return true;
}

async function request<T>(
  path: string,
  options: RequestInit = {},
  retried = false
): Promise<T> {
  const headers = new Headers(options.headers);
  const token = getToken();
  if (token) headers.set("Authorization", `Bearer ${token}`);
  if (options.body && !(options.body instanceof FormData)) {
    headers.set("Content-Type", "application/json");
  }

  const res = await fetch(`${BASE}${path}`, { ...options, headers });

  if (res.status === 401 && !retried && (await tryRefresh())) {
    return request<T>(path, options, true);
  }
  if (!res.ok) {
    let message = `خطأ (${res.status})`;
    try {
      const data = await res.json();
      message = data.detail || JSON.stringify(data);
    } catch {
      /* keep default */
    }
    throw new ApiError(res.status, message);
  }
  if (res.status === 204) return undefined as T;
  return res.json();
}

export const api = {
  get: <T>(path: string) => request<T>(path),
  post: <T>(path: string, body?: unknown) =>
    request<T>(path, {
      method: "POST",
      body: body instanceof FormData ? body : JSON.stringify(body ?? {}),
    }),
  patch: <T>(path: string, body: unknown) =>
    request<T>(path, {
      method: "PATCH",
      body: body instanceof FormData ? body : JSON.stringify(body),
    }),
  delete: <T>(path: string) => request<T>(path, { method: "DELETE" }),
};

/** Builds the WebSocket URL with the JWT query parameter. */
export function wsUrl(path: string) {
  const proto = location.protocol === "https:" ? "wss" : "ws";
  return `${proto}://${location.host}${path}?token=${getToken()}`;
}
