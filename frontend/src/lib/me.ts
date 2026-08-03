import { getUser } from "./http";

/** The signed-in user in the prototype's shape (id/name/avatarColor). */
export function me(): { id: string; name: string; avatarColor: string } {
  const u = getUser() as { id?: string; name?: string; avatar_color?: string } | null;
  return { id: u?.id ?? "", name: u?.name ?? "کاربر", avatarColor: u?.avatar_color ?? "#1f4f99" };
}
