import { createContext, useCallback, useContext, useEffect, useMemo, useState, type ReactNode } from "react";
import { http, isAuthed } from "../lib/http";
import { setScopeHeaders } from "../lib/http";

/**
 * The signed-in user's organisational reach.
 *
 * Scope follows who a person is, not what they select: it is resolved by the
 * server from their role assignment and company memberships and delivered by
 * /my/scope. The switcher can only narrow that reach, never widen it — the API
 * applies the same rules to every queryset, so a forged selection changes
 * nothing about what comes back.
 *
 * This context therefore decides what to *render*. It is a convenience, not
 * the access control; that lives on the server.
 */
export type ContentScopeName = "سراسری" | "هلدینگ" | "شرکت";
export type ScopeLevel = "سیستم" | "هلدینگ" | "شرکت" | "گروه";

export type SubCompany = { id: string; name: string };
export type Holding = { id: string; name: string; color: string; companies: SubCompany[] };
export type Company = { id: string; name: string; holdingId: string };

/** The scope stamped on a piece of content. */
export type Scoped = { scope?: ContentScopeName; holdingId?: string; companyId?: string };

type Switchable = { holdingId?: string; companyId?: string; label: string };

type ScopePayload = {
  level: ScopeLevel;
  memberCompanyIds: string[];
  memberHoldingIds: string[];
  canSwitch: boolean;
  switchable: Switchable[];
  publishable: ContentScopeName[];
  role: { id: string; title: string; scope: string; permissions: string[] };
  holdings: Holding[];
  companies: Company[];
};

const EMPTY: ScopePayload = {
  level: "شرکت",
  memberCompanyIds: [],
  memberHoldingIds: [],
  canSwitch: false,
  switchable: [],
  publishable: ["شرکت"],
  role: { id: "", title: "—", scope: "tenant", permissions: [] },
  holdings: [],
  companies: [],
};

type TenancyValue = {
  ready: boolean;
  level: ScopeLevel;
  role: ScopePayload["role"];
  holdings: Holding[];
  companies: Company[];
  companiesOf: (holdingId: string) => Company[];
  holdingOf: (companyId?: string) => Holding | undefined;

  session: { level: ScopeLevel; memberCompanyIds: string[]; memberHoldingIds: string[]; canSwitch: boolean; switchable: Switchable[] };

  activeHoldingId?: string;
  activeCompanyId?: string;
  setScope: (holdingId?: string, companyId?: string) => void;
  activeScopeLabel: string;
  /** A system administrator looking at one domain rather than the whole install. */
  isViewingAs: boolean;
  allowedPublishScopes: ContentScopeName[];

  hasPermission: (id: string) => boolean;
  canAccessAdmin: boolean;
  canManageHoldings: boolean;
  managedHoldingIds: string[];
  managedCompanyIds: string[];

  visible: (item: Scoped) => boolean;
  filterScoped: <T extends Scoped>(items: T[]) => T[];
  ownerLabel: (item: Scoped) => string;
  defaultScopeForNew: () => Scoped;
  reload: () => Promise<void>;
};

const TenancyContext = createContext<TenancyValue | null>(null);

const ADMIN_PERMS = [
  "users.create", "users.edit", "roles.edit", "roles.create",
  "settings.system", "settings.branding", "settings.modules", "companies.manage",
];

export function TenancyProvider({ children }: { children: ReactNode }) {
  const [data, setData] = useState<ScopePayload>(EMPTY);
  const [ready, setReady] = useState(false);
  const [activeHoldingId, setActiveHoldingId] = useState<string | undefined>();
  const [activeCompanyId, setActiveCompanyId] = useState<string | undefined>();

  const reload = useCallback(async () => {
    if (!isAuthed()) { setReady(true); return; }
    try {
      const res = await http<ScopePayload>("/my/scope");
      setData(res);
      // Land on a sensible domain: system level starts wide, everyone else
      // starts inside their own first membership.
      if (res.level !== "سیستم") {
        const first = res.companies.find((c) => res.memberCompanyIds.includes(c.id));
        setActiveHoldingId(first?.holdingId ?? res.memberHoldingIds[0]);
        setActiveCompanyId(res.level === "هلدینگ" ? undefined : first?.id);
      }
    } catch {
      setData(EMPTY);
    } finally {
      setReady(true);
    }
  }, []);

  useEffect(() => { reload(); }, [reload]);

  // Every request carries the chosen domain so the server narrows its own
  // queries the same way this context narrows the display.
  useEffect(() => {
    setScopeHeaders(activeHoldingId, activeCompanyId);
  }, [activeHoldingId, activeCompanyId]);

  const value = useMemo<TenancyValue>(() => {
    const { holdings, companies, role, level } = data;
    const permissionSet = new Set(role.permissions);
    const hasPermission = (id: string) => permissionSet.has(id);

    const activeHolding = holdings.find((h) => h.id === activeHoldingId);
    const activeCompany = companies.find((c) => c.id === activeCompanyId);
    const activeScopeLabel = activeCompany?.name ?? activeHolding?.name ?? "کل سیستم";

    const managedHoldingIds =
      level === "سیستم" ? holdings.map((h) => h.id)
      : level === "هلدینگ" ? data.memberHoldingIds
      : [];
    const managedCompanyIds =
      level === "سیستم" ? companies.map((c) => c.id)
      : level === "هلدینگ" ? companies.filter((c) => data.memberHoldingIds.includes(c.holdingId)).map((c) => c.id)
      : data.memberCompanyIds;

    /** Mirrors the server's visible_q, so the list does not flicker items the API will withhold. */
    const visible = (item: Scoped) => {
      if (level === "سیستم" && !activeHoldingId && !activeCompanyId) return true;
      if (!item.scope || item.scope === "سراسری") return true;
      if (activeCompanyId) {
        return item.scope === "شرکت"
          ? item.companyId === activeCompanyId
          : item.holdingId === (activeHoldingId ?? companies.find((c) => c.id === activeCompanyId)?.holdingId);
      }
      if (activeHoldingId) return item.holdingId === activeHoldingId;
      if (item.scope === "هلدینگ") return data.memberHoldingIds.includes(item.holdingId ?? "");
      return data.memberCompanyIds.includes(item.companyId ?? "");
    };

    return {
      ready,
      level,
      role,
      holdings,
      companies,
      companiesOf: (holdingId) => companies.filter((c) => c.holdingId === holdingId),
      holdingOf: (companyId) => {
        const c = companies.find((x) => x.id === companyId);
        return c ? holdings.find((h) => h.id === c.holdingId) : undefined;
      },

      session: {
        level,
        memberCompanyIds: data.memberCompanyIds,
        memberHoldingIds: data.memberHoldingIds,
        canSwitch: data.canSwitch,
        switchable: data.switchable,
      },

      activeHoldingId,
      activeCompanyId,
      setScope: (holdingId, companyId) => {
        setActiveHoldingId(holdingId);
        setActiveCompanyId(companyId);
      },
      activeScopeLabel,
      isViewingAs: level === "سیستم" && (!!activeHoldingId || !!activeCompanyId),
      allowedPublishScopes: data.publishable,

      hasPermission,
      canAccessAdmin: ADMIN_PERMS.some(hasPermission),
      canManageHoldings: hasPermission("companies.manage"),
      managedHoldingIds,
      managedCompanyIds,

      visible,
      filterScoped: <T extends Scoped>(items: T[]) => items.filter(visible),
      ownerLabel: (item) => {
        if (!item.scope || item.scope === "سراسری") return "سراسری";
        if (item.scope === "هلدینگ") return holdings.find((h) => h.id === item.holdingId)?.name ?? "هلدینگ";
        return companies.find((c) => c.id === item.companyId)?.name ?? "شرکت";
      },
      defaultScopeForNew: () => {
        const allowed = data.publishable;
        if (activeCompanyId && allowed.includes("شرکت")) {
          const c = companies.find((x) => x.id === activeCompanyId);
          return { scope: "شرکت", holdingId: c?.holdingId, companyId: activeCompanyId };
        }
        if (activeHoldingId && allowed.includes("هلدینگ")) {
          return { scope: "هلدینگ", holdingId: activeHoldingId };
        }
        if (allowed.includes("سراسری")) return { scope: "سراسری" };
        const c = companies.find((x) => x.id === data.memberCompanyIds[0]);
        return { scope: "شرکت", holdingId: c?.holdingId, companyId: c?.id };
      },
      reload,
    };
  }, [data, ready, activeHoldingId, activeCompanyId, reload]);

  return <TenancyContext.Provider value={value}>{children}</TenancyContext.Provider>;
}

// eslint-disable-next-line react-refresh/only-export-components
export function useTenancy() {
  const ctx = useContext(TenancyContext);
  if (!ctx) throw new Error("useTenancy must be used within TenancyProvider");
  return ctx;
}
