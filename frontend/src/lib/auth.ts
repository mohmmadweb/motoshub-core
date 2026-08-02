import { clearSession, http, setSession } from "./http";

export interface AuthUser { id: string; name: string; username: string; permissions: string[]; [k: string]: unknown; }

export async function login(username: string, password: string): Promise<AuthUser> {
  const data = await http<{ access: string; refresh: string; user: AuthUser }>("/auth/login", {
    method: "POST", body: JSON.stringify({ username, password }),
  });
  setSession(data.access, data.refresh, data.user);
  return data.user;
}
export function logout() { clearSession(); }
export { isAuthed, getUser, getToken } from "./http";
