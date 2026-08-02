// Real API client for the Motoshub Django backend (replaces the mock api.ts).
// Base + WS can be absolute (cross-origin, CORS-enabled in dev) or relative.
const BASE = (import.meta as any).env?.VITE_API_BASE || "/api/v1";
export const WS_BASE =
  (import.meta as any).env?.VITE_WS_BASE ||
  `${location.protocol === "https:" ? "wss" : "ws"}://${location.host}`;

export const getToken = () => (typeof localStorage !== "undefined" ? localStorage.getItem("ms_token") : null);
export const getRefresh = () => (typeof localStorage !== "undefined" ? localStorage.getItem("ms_refresh") : null);
export const setSession = (access: string, refresh: string, user: unknown) => {
  localStorage.setItem("ms_token", access);
  if (refresh) localStorage.setItem("ms_refresh", refresh);
  if (user) localStorage.setItem("ms_user", JSON.stringify(user));
};
export const clearSession = () => {
  ["ms_token", "ms_refresh", "ms_user"].forEach((k) => localStorage.removeItem(k));
};
export const currentUser = () => {
  try { return JSON.parse(localStorage.getItem("ms_user") || "null"); } catch { return null; }
};

interface Opts { method?: string; body?: unknown; auth?: boolean }

export async function apiFetch<T = any>(path: string, { method = "GET", body, auth = true }: Opts = {}): Promise<T> {
  const headers: Record<string, string> = {};
  const isForm = typeof FormData !== "undefined" && body instanceof FormData;
  if (!isForm && body !== undefined) headers["Content-Type"] = "application/json";
  if (auth) { const t = getToken(); if (t) headers["Authorization"] = `Bearer ${t}`; }
  const res = await fetch(`${BASE}${path}`, {
    method, headers,
    body: isForm ? (body as FormData) : body !== undefined ? JSON.stringify(body) : undefined,
  });
  const json = await res.json().catch(() => null);
  if (!res.ok) throw { status: res.status, body: json };
  return json as T;
}

export const http = {
  get: <T = any>(p: string) => apiFetch<T>(p),
  post: <T = any>(p: string, b?: unknown, o?: Opts) => apiFetch<T>(p, { method: "POST", body: b, ...o }),
  patch: <T = any>(p: string, b?: unknown) => apiFetch<T>(p, { method: "PATCH", body: b }),
  del: <T = any>(p: string) => apiFetch<T>(p, { method: "DELETE" }),
};
