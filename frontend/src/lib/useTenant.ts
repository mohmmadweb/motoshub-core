import { useEffect, useState } from "react";
import { http, httpRaw, isAuthed } from "./http";

export interface TenantInfo {
  id: string;
  name: string;
  domain: string;
  logoColor: string;
  plan: string;
  users: number;
  modules: string[];
}

const PLAN_FA: Record<string, string> = { enterprise: "سازمانی", business: "کسب‌وکار", starter: "پایه" };

const FALLBACK: TenantInfo = {
  id: "", name: "سازمان", domain: "", logoColor: "#1f4f99", plan: "سازمانی", users: 0, modules: [],
};

// One in-flight request shared by every component that needs the tenant.
let cache: TenantInfo | null = null;
let inflight: Promise<TenantInfo> | null = null;

async function load(): Promise<TenantInfo> {
  if (cache) return cache;
  if (!inflight) {
    inflight = (async () => {
      const [t, usersEnv] = await Promise.all([
        http<any>("/tenant"),
        // httpRaw keeps `meta`, which carries the real member count.
        httpRaw<any[]>("/users?page_size=1").catch(() => ({ data: [], meta: { count: 0 } } as any)),
      ]);
      cache = {
        id: t.id, name: t.name, domain: t.domain, logoColor: t.logo_color,
        plan: PLAN_FA[t.plan] ?? t.plan,
        users: usersEnv.meta?.count ?? 0,
        modules: t.enabled_modules ?? [],
      };
      return cache;
    })().catch(() => FALLBACK);
  }
  return inflight;
}

/** The signed-in user's organization (branding, plan, enabled modules). */
export function useTenant(): TenantInfo {
  const [tenant, setTenant] = useState<TenantInfo>(cache ?? FALLBACK);
  useEffect(() => {
    if (!isAuthed()) return;
    let alive = true;
    load().then((t) => { if (alive) setTenant(t); });
    return () => { alive = false; };
  }, []);
  return tenant;
}

/** Clear the cache after branding edits so the shell re-reads it. */
export function invalidateTenant() {
  cache = null;
  inflight = null;
}
