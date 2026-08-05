import { getUser } from "./http";

/**
 * The signed-in user's effective permission ids, as resolved by the backend
 * from their role assignments in the active tenant. Login stores them on the
 * user record, so no extra request is needed to decide what to render.
 *
 * This is presentation only. Every endpoint enforces the same ids server-side —
 * hiding a control is a courtesy, never the access check.
 */
export function permissions(): string[] {
  const u = getUser() as { permissions?: string[] } | null;
  return Array.isArray(u?.permissions) ? u.permissions : [];
}

export function hasPerm(id: string): boolean {
  return permissions().includes(id);
}

export function hasAnyPerm(...ids: string[]): boolean {
  const mine = permissions();
  return ids.some((id) => mine.includes(id));
}

/**
 * Whether to offer the admin console at all. Mirrors the prototype's
 * `canAccessAdmin`: holding any of the governing permissions is enough, since
 * each section inside the console gates itself further.
 */
export function canAccessAdmin(): boolean {
  return hasAnyPerm(
    "users.create", "users.edit", "roles.edit", "roles.create",
    "settings.system", "settings.branding", "settings.modules", "companies.manage",
  );
}
