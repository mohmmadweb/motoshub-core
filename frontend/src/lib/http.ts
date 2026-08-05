// Real HTTP client for the /api/v1 backend (replaces the mock api layer).
const API_BASE = (import.meta.env.VITE_API_BASE as string) || "/api/v1";

export const getToken = () => (typeof localStorage !== "undefined" ? localStorage.getItem("ms-access") : null);
export const getRefresh = () => (typeof localStorage !== "undefined" ? localStorage.getItem("ms-refresh") : null);

export function setSession(access: string, refresh: string, user: unknown) {
  localStorage.setItem("ms-access", access);
  localStorage.setItem("ms-refresh", refresh);
  localStorage.setItem("ms-user", JSON.stringify(user));
}
export function clearSession() {
  localStorage.removeItem("ms-access");
  localStorage.removeItem("ms-refresh");
  localStorage.removeItem("ms-user");
}
export const getUser = () => {
  try { return JSON.parse(localStorage.getItem("ms-user") || "null"); } catch { return null; }
};
export const isAuthed = () => !!getToken();

export interface Envelope<T> { data: T; links?: Record<string, string | null>; meta?: { count: number; page: number; pages: number; page_size: number }; }

async function refreshOnce(): Promise<boolean> {
  const refresh = getRefresh();
  if (!refresh) return false;
  const res = await fetch(`${API_BASE}/auth/refresh`, {
    method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ refresh }),
  });
  if (!res.ok) { clearSession(); return false; }
  const body = await res.json();
  if (body?.data?.access) { localStorage.setItem("ms-access", body.data.access); return true; }
  clearSession(); return false;
}

/** Returns the full envelope ({data, links, meta}) or throws {status, error}. */
export async function httpRaw<T = unknown>(path: string, opts: RequestInit = {}, retry = true): Promise<Envelope<T>> {
  const token = getToken();
  const isForm = opts.body instanceof FormData;
  const headers: Record<string, string> = { ...(isForm ? {} : { "Content-Type": "application/json" }), ...(opts.headers as Record<string, string>) };
  if (token) headers.Authorization = `Bearer ${token}`;
  const res = await fetch(`${API_BASE}${path}`, { ...opts, headers });
  if (res.status === 401 && retry && (await refreshOnce())) return httpRaw<T>(path, opts, false);
  const body = res.status === 204 ? { data: null } : await res.json().catch(() => ({}));
  if (!res.ok) throw { status: res.status, error: (body as { error?: unknown }).error };
  return body as Envelope<T>;
}

/** Convenience: returns just the unwrapped `data`. */
export async function http<T = unknown>(path: string, opts: RequestInit = {}): Promise<T> {
  return (await httpRaw<T>(path, opts)).data;
}

/**
 * The Persian message the backend sent, for showing in a toast.
 *
 * Rejections from httpRaw are plain `{status, error}` objects, not Errors, so
 * `err instanceof Error` never matches and a naive handler would discard rules
 * the API states precisely — «امکان ویرایش فقط یک‌بار وجود دارد» and the like.
 * Field errors (422) are joined so the user learns which field is wrong.
 */
export function apiMessage(err: unknown, fallback: string): string {
  const e = (err as { error?: { message?: string; details?: Record<string, string[]> } })?.error;
  if (!e) return fallback;
  const details = e.details
    ? Object.values(e.details).flat().filter(Boolean).join(" · ")
    : "";
  return details || e.message || fallback;
}
