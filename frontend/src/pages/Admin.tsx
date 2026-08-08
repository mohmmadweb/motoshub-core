import { useEffect, useRef, useState } from "react";
import {
  Settings,
  Building2,
  Plug,
  Palette,
  KeyRound,
  LayoutTemplate,
  Users,
  ShieldCheck,
  Network,
  Plus,
  Upload,
  Download,
  Globe2,
  Eye,
  EyeOff,
  AlertTriangle,
  CheckCircle2,
  Ban,
  Webhook,
  Bot,
  Slash,
  UserCog,
  FileWarning,
  Tag,
  SlidersHorizontal,
  HardDrive,
  Pencil,
  Trash2,
  Gauge,
  RotateCcw,
  Activity,
} from "lucide-react";
import { SystemSection, StorageSection } from "./AdminSections";
import { moduleCatalog, adminMenus } from "../data/constants";
import { http, apiMessage } from "../lib/http";
import { me } from "../lib/me";
import { useApiList } from "../lib/useApiList";
import { fromUser, fromIntegration, toIntegration, fromGuestAccount, toGuestAccount } from "../lib/adapters";
import { useTenant } from "../lib/useTenant";
import { useTenancy } from "../context/TenancyContext";

// The RBAC catalog is served by the backend (apps/rbac/catalog.py is the source of
// truth); mapped here into the shape this screen renders.
type PermGroup = { id: string; label: string; actions: { id: string; label: string }[] };
function usePermissionCatalog(): { catalog: PermGroup[]; allIds: string[] } {
  const [catalog, setCatalog] = useState<PermGroup[]>([]);
  useEffect(() => {
    http<{ group: string; label: string; permissions: { id: string; action: string }[] }[]>("/permissions/catalog")
      .then((rows) => setCatalog(rows.map((g) => ({
        id: g.group, label: g.label,
        actions: g.permissions.map((p) => ({ id: p.id, label: p.action })),
      }))))
      .catch(() => setCatalog([]));
  }, []);
  return { catalog, allIds: catalog.flatMap((g) => g.actions.map((a) => a.id)) };
}
import { useApiCollection } from "../lib/useApiCollection";
import { fromRole, toRole } from "../lib/adapters";
import LiveUsagePanel from "../components/LiveUsagePanel";
import BrandingPanel from "../components/BrandingPanel";
import { useSettings, settingsMeta, defaultSettings, type WorkflowSettings } from "../context/SettingsContext";
import { useConfirm } from "../components/ui/ConfirmProvider";
import {type RoleAssignment,
  type ModuleDef,
  type RoleDef,
  type AdminPageDef,
  type Integration,
  type GuestAccount} from "../data/types";
import PageHeader from "../components/ui/PageHeader";
import Badge from "../components/ui/Badge";
import Button from "../components/ui/Button";
import Toggle from "../components/ui/Toggle";
import StatCard from "../components/ui/StatCard";
import Modal from "../components/ui/Modal";
import RowActions from "../components/ui/RowActions";
import { useToast } from "../components/ui/ToastProvider";

type SectionId = "tenants" | "holdings" | "modules" | "branding" | "roles" | "pages" | "users" | "integrations" | "security" | "network" | "workflow" | "monitor" | "system" | "storage";

const sections: { id: SectionId; label: string; icon: typeof Settings }[] = [
  { id: "tenants", label: "هویت سیستم و ورود یکپارچه", icon: KeyRound },
  { id: "holdings", label: "هلدینگ‌ها و شرکت‌ها", icon: Network },
  { id: "branding", label: "برندسازی سازمان", icon: Palette },
  { id: "roles", label: "نقش‌ها و دسترسی", icon: KeyRound },
  { id: "users", label: "کاربران و واردسازی", icon: Users },
  { id: "modules", label: "بازارچه‌ی ماژول‌ها", icon: Plug },
  { id: "pages", label: "صفحات و منوها", icon: LayoutTemplate },
  { id: "integrations", label: "یکپارچه‌سازی و اتوماسیون", icon: Webhook },
  { id: "security", label: "امنیت و انطباق", icon: ShieldCheck },
  { id: "network", label: "تعامل بین‌سازمانی", icon: Network },
  { id: "workflow", label: "پارامترهای گردش کار", icon: Gauge },
  { id: "monitor", label: "پایش زنده سامانه", icon: Activity },
  { id: "system", label: "تنظیمات سیستم", icon: SlidersHorizontal },
  { id: "storage", label: "فضای ذخیره‌سازی", icon: HardDrive },
];

const tenantPalette = ["#1f4f99", "#2a66bd", "#0d9488", "#7c3aed", "#b45309", "#0f172a"];

export default function Admin() {
  const { canAccessAdmin: isAdmin } = useTenancy();
  const [section, setSection] = useState<SectionId>("tenants");
  const realTenant = useTenant();
  // One installation, one customer — the identity itself is edited in the
  // «هویت سیستم» section rather than picked from a list.
  const tenant = realTenant;
  const [enabledModules, setEnabledModules] = useState<string[]>(["social", "knowledge", "projects", "reports"]);
  const [crossTenant, setCrossTenant] = useState(false);
  const [roles, setRoles] = useApiCollection<RoleDef>("/roles", fromRole as any, toRole as any);
  // Console configuration is stored per-tenant (see /settings/workflow).
  const [pages, setPages] = useState<AdminPageDef[]>([]);
  const [extensions, setExtensions] = useState<string[]>([]);
  useEffect(() => {
    http<any>("/settings/workflow")
      .then((cfg) => {
        setPages((cfg.admin_pages ?? []) as AdminPageDef[]);
        setExtensions((cfg.allowed_file_extensions ?? []) as string[]);
      })
      .catch(() => {});
  }, []);
  const [integrations, setIntegrations] = useApiCollection<Integration>("/integrations", fromIntegration as any, toIntegration as any);
  const [guestAccounts, setGuestAccounts] = useApiCollection<GuestAccount>("/guest-accounts", fromGuestAccount as any, toGuestAccount as any);
  const { notify } = useToast();

  // Placed after every hook so the hook order stays stable between renders.
  // The API refuses these operations independently; this only avoids showing a
  // console the member cannot use.
  if (!isAdmin) {
    return (
      <div className="flex flex-col items-center justify-center text-center py-24 px-6">
        <span className="w-14 h-14 rounded-xl bg-amber-50 text-amber-600 flex items-center justify-center mb-4">
          <ShieldCheck size={24} />
        </span>
        <h1 className="text-lg font-bold text-ink-900 mb-2">دسترسی به پنل راهبری ندارید</h1>
        <p className="text-sm text-ink-500 max-w-sm leading-7">
          این بخش مخصوص نقش‌های مدیریتی (مدیر سیستم، مدیر هلدینگ یا مدیر شرکت) است. در صورت نیاز،
          از مدیر مجموعه‌ی خود درخواست دسترسی کنید.
        </p>
      </div>
    );
  }

  const toggleModule = (id: string) => {
    setEnabledModules((prev) => (prev.includes(id) ? prev.filter((x) => x !== id) : [...prev, id]));
  };

  return (
    <div>
      <PageHeader
        title="پنل راهبری"
        description={`مدیریت سازمان «${tenant.name}» — هر تغییر فقط روی این سازمان اعمال می‌شود`}
        icon={<Settings size={18} />}
      />

      <div className="grid grid-cols-1 lg:grid-cols-[220px_1fr] gap-5">
        <div className="card p-2 h-fit">
          {sections.map((s) => (
            <button
              key={s.id}
              onClick={() => setSection(s.id)}
              className={`w-full flex items-center gap-2.5 px-3 py-2.5 rounded-md text-[13px] font-medium text-right ${
                section === s.id ? "bg-navy-900 text-white" : "text-ink-600 hover:bg-ink-50"
              }`}
            >
              <s.icon size={15} />
              {s.label}
            </button>
          ))}
        </div>

        <div className="space-y-5">
          {section === "tenants" && (
            <SystemIdentitySection notify={notify} />
          )}

          {section === "holdings" && <HoldingsSection notify={notify} />}

          {section === "modules" && (
            <ModulesSection enabledModules={enabledModules} toggleModule={toggleModule} />
          )}

          {section === "branding" && <BrandingPanel />}

          {section === "roles" && <RolesSection roles={roles} setRoles={setRoles} notify={notify} />}

          {section === "pages" && <PagesSection pages={pages} setPages={setPages} extensions={extensions} setExtensions={setExtensions} notify={notify} />}

          {section === "users" && <UsersSection tenant={tenant} roles={roles} notify={notify} />}

          {section === "integrations" && <IntegrationsSection integrations={integrations} setIntegrations={setIntegrations} notify={notify} />}

          {section === "security" && <SecuritySection guestAccounts={guestAccounts} setGuestAccounts={setGuestAccounts} notify={notify} />}

          {section === "network" && (
            <NetworkSection crossTenant={crossTenant} setCrossTenant={setCrossTenant} />
          )}

          {section === "workflow" && <WorkflowParamsSection notify={notify} />}

          {section === "monitor" && (
            <div className="space-y-4">
              <LiveUsagePanel />
              <p className="text-[11px] text-ink-400 leading-5">
                این متریک‌ها مربوط به کل سامانه است و فقط برای راهبران نمایش داده می‌شود. جزئیات دیسک در بخش
                «فضای ذخیره‌سازی» و محدودیت نرخ درخواست در «پارامترهای گردش کار» قابل مدیریت است.
              </p>
            </div>
          )}

          {section === "system" && <SystemSection notify={notify} />}

          {section === "storage" && <StorageSection notify={notify} />}
        </div>
      </div>
    </div>
  );
}

type Notify = (message: string, tone?: "success" | "info" | "warning") => void;

// ---------------------------------------------------------------------------
// پارامترهای گردش کار — اعداد ثابت روندها (یادآوری‌ها، مهلت‌ها، حدنصاب‌ها)
// همگی از اینجا قابل تغییرند و بلافاصله در کل سامانه اعمال می‌شوند.
// ---------------------------------------------------------------------------
function WorkflowParamsSection({ notify }: { notify: Notify }) {
  const { settings, update, reset } = useSettings();
  const [draft, setDraft] = useState<WorkflowSettings>(settings);

  const save = () => {
    update(draft);
    notify("پارامترهای گردش کار ذخیره شد و از این لحظه در همه‌ی روندها اعمال می‌شود.");
  };

  return (
    <div>
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-sm font-bold text-ink-900">پارامترهای گردش کار</h3>
        <div className="flex items-center gap-2">
          <Button
            variant="secondary"
            size="sm"
            icon={<RotateCcw size={13} />}
            onClick={() => {
              reset();
              setDraft(defaultSettings);
              notify("پارامترها به مقادیر پیش‌فرض بازگشت.", "info");
            }}
          >
            بازگشت به پیش‌فرض
          </Button>
          <Button variant="primary" size="sm" onClick={save}>ذخیره‌ی پارامترها</Button>
        </div>
      </div>
      <div className="card p-4 mb-4 bg-brand-50 border-brand-200 flex items-start gap-3">
        <Gauge size={18} className="text-brand-700 shrink-0 mt-0.5" />
        <p className="text-xs text-brand-800 leading-6">
          تمام اعداد ثابت روندها (مثل «۷ روز قبل از سررسید» یا «مهلت ۱۵ روزه بررسی») اینجا تعریف می‌شوند.
          با تغییر هر عدد، متن قواعد، هشدارها و حدنصاب‌های ارزیابی در سراسر سامانه به‌روز می‌شود.
        </p>
      </div>
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
        {settingsMeta.map((m) => (
          <div key={m.key} className="card p-4">
            <div className="flex items-center justify-between gap-3">
              <div className="min-w-0">
                <p className="text-[13px] font-medium text-ink-900">{m.label}</p>
                <p className="text-[11px] text-ink-400 mt-1 leading-5">{m.hint}</p>
              </div>
              <div className="flex items-center gap-1.5 shrink-0">
                <input
                  type="number"
                  min={0}
                  value={draft[m.key]}
                  onChange={(e) => setDraft((prev) => ({ ...prev, [m.key]: Number(e.target.value) }))}
                  className="w-20 text-sm text-center border border-ink-200 rounded-md px-2 py-1.5 outline-none focus:border-brand-400"
                  dir="ltr"
                />
                <span className="text-[11px] text-ink-400 whitespace-nowrap">{m.unit}</span>
              </div>
            </div>
            {draft[m.key] !== settings[m.key] && (
              <p className="text-[10.5px] text-amber-700 mt-2">تغییر ذخیره‌نشده (مقدار فعلی: {settings[m.key].toLocaleString("fa-IR")})</p>
            )}
          </div>
        ))}
      </div>
      <div className="mt-4">
        <Button variant="primary" className="w-full justify-center" onClick={save}>ذخیره‌ی همه‌ی پارامترها</Button>
      </div>
    </div>
  );
}

// ---------------------------------------------------------------------------
// ساختار هلدینگ‌ها و شرکت‌های زیرمجموعه — مبنای تفکیک محتوا و دسترسی شرکتی
// ---------------------------------------------------------------------------
type HoldingRow = { id: string; name: string; color: string; companies: { id: string; name: string }[] };

function HoldingsSection({ notify }: { notify: Notify }) {
  const confirm = useConfirm();
  const [holdingsList, setHoldingsList] = useState<HoldingRow[]>([]);
  const [holdingOpen, setHoldingOpen] = useState(false);
  const [editingHolding, setEditingHolding] = useState<HoldingRow | null>(null);
  const [holdingForm, setHoldingForm] = useState({ name: "", color: "#0d9488" });
  const [open, setOpen] = useState(false);
  const [editingCompany, setEditingCompany] = useState<{ id: string; name: string } | null>(null);
  const [companyName, setCompanyName] = useState("");
  const [holdingId, setHoldingId] = useState("");

  // Real org tree from /holdings (each holding carries its companies).
  const load = () =>
    http<HoldingRow[]>("/holdings?page_size=100").then((r) => {
      setHoldingsList(r);
      setHoldingId((cur) => cur || (r[0]?.id ?? ""));
    });
  useEffect(() => { load().catch(() => {}); }, []);

  // ── holdings ──────────────────────────────────────────────────────────────
  const openHoldingModal = (h?: HoldingRow) => {
    if (h) {
      setEditingHolding(h);
      setHoldingForm({ name: h.name, color: h.color });
    } else {
      setEditingHolding(null);
      setHoldingForm({ name: "", color: "#0d9488" });
    }
    setHoldingOpen(true);
  };

  const submitHolding = async () => {
    if (!holdingForm.name.trim()) {
      notify("نام هلدینگ الزامی است.", "warning");
      return;
    }
    const body = { name: holdingForm.name.trim(), color: holdingForm.color };
    try {
      if (editingHolding) {
        await http(`/holdings/${editingHolding.id}`, { method: "PATCH", body: JSON.stringify(body) });
        notify(`هلدینگ «${body.name}» ویرایش شد.`);
      } else {
        await http("/holdings", { method: "POST", body: JSON.stringify(body) });
        notify(`هلدینگ «${body.name}» ایجاد شد. حالا می‌توانید شرکت‌های زیرمجموعه‌اش را تعریف کنید.`);
      }
      await load();
      setHoldingOpen(false);
      setEditingHolding(null);
    } catch (err) {
      notify(apiMessage(err, "ثبت هلدینگ ناموفق بود."), "warning");
    }
  };

  const removeHolding = (h: HoldingRow) =>
    confirm({
      title: `حذف هلدینگ «${h.name}»؟`,
      message: `${h.companies.length.toLocaleString("fa-IR")} شرکت زیرمجموعه و همه‌ی محتوای اختصاصی آن‌ها نیز حذف می‌شود.`,
      onConfirm: async () => {
        try {
          await http(`/holdings/${h.id}`, { method: "DELETE" });
          await load();
          notify(`هلدینگ «${h.name}» حذف شد.`, "info");
        } catch (err) {
          notify(apiMessage(err, "حذف هلدینگ ناموفق بود."), "warning");
        }
      },
    });

  // ── companies ─────────────────────────────────────────────────────────────
  const openCompanyModal = (c?: { id: string; name: string }, parent?: string) => {
    setEditingCompany(c ?? null);
    setCompanyName(c?.name ?? "");
    if (parent) setHoldingId(parent);
    setOpen(true);
  };

  const submitCompany = async () => {
    if (!companyName.trim()) {
      notify("نام شرکت و هلدینگ مادر الزامی است.", "warning");
      return;
    }
    if (!holdingId) {
      notify("ابتدا یک هلدینگ انتخاب کنید.", "warning");
      return;
    }
    const clean = companyName.trim();
    try {
      if (editingCompany) {
        await http(`/companies/${editingCompany.id}`, {
          method: "PATCH", body: JSON.stringify({ name: clean, holding: holdingId }),
        });
        notify(`شرکت «${clean}» ویرایش شد.`);
      } else {
        await http("/companies", { method: "POST", body: JSON.stringify({ name: clean, holding: holdingId }) });
        const holdingName = holdingsList.find((h) => h.id === holdingId)?.name ?? "";
        // Announced only after the server accepted it — the previous version
        // reported success while the request was still in flight.
        notify(`شرکت «${clean}» به «${holdingName}» افزوده شد. از این پس محتوای اختصاصی و کاربران این شرکت قابل تعریف است.`);
      }
      await load();
      setOpen(false);
      setEditingCompany(null);
      setCompanyName("");
    } catch (err) {
      notify(apiMessage(err, "ثبت شرکت ناموفق بود — دسترسی لازم را ندارید."), "warning");
    }
  };

  const removeCompany = (c: { id: string; name: string }) =>
    confirm({
      title: `حذف شرکت «${c.name}»؟`,
      message: "کاربران و محتوای اختصاصی این شرکت دیگر در دسترس نخواهد بود.",
      onConfirm: async () => {
        try {
          await http(`/companies/${c.id}`, { method: "DELETE" });
          await load();
          notify(`شرکت «${c.name}» حذف شد.`, "info");
        } catch (err) {
          notify(apiMessage(err, "حذف شرکت ناموفق بود."), "warning");
        }
      },
    });

  return (
    <div>
      <div className="flex items-center justify-between mb-3 gap-2 flex-wrap">
        <h3 className="text-sm font-bold text-ink-900">ساختار هلدینگ‌ها و شرکت‌های زیرمجموعه</h3>
        <div className="flex items-center gap-2">
          <Button variant="secondary" size="sm" icon={<Plus size={14} />} onClick={() => openHoldingModal()}>
            هلدینگ جدید
          </Button>
          <Button variant="primary" size="sm" icon={<Plus size={14} />} onClick={() => openCompanyModal()}>
            افزودن شرکت
          </Button>
        </div>
      </div>

      <div className="card p-4 mb-4 bg-brand-50 border-brand-200 flex items-start gap-3">
        <Network size={18} className="text-brand-700 shrink-0 mt-0.5" />
        <p className="text-xs text-brand-800 leading-6">
          همه‌ی شرکت‌ها زیر یک سامانه‌ی واحد هستند، اما هر محتوا (خبر، سند، رویداد و…) به یک شرکت/هلدینگ مالک
          متصل می‌شود و دامنه‌ی انتشار دارد: «فقط شرکت خودم»، «کل هلدینگ» یا «سراسری». کاربران هر شرکت فقط
          محتوای دامنه‌ی خودشان را می‌بینند (نمونه‌ی زنده در صفحه‌ی «اخبار سازمان»).
        </p>
      </div>

      <div className="card p-4 mb-4 bg-ink-50 border-ink-200 flex items-start gap-3">
        <ShieldCheck size={18} className="text-ink-500 shrink-0 mt-0.5" />
        <div className="text-xs text-ink-600 leading-6">
          <p className="font-bold text-ink-800 mb-1">زنجیره‌ی واگذاری اختیار</p>
          مدیر سیستم هلدینگ‌ها را می‌سازد و مدیر هر هلدینگ را منصوب می‌کند؛
          مدیر هلدینگ شرکت‌های هلدینگ خودش را می‌سازد و مدیر شرکت را تعیین می‌کند؛ مدیر شرکت کاربران همان
          شرکت را اضافه می‌کند. هیچ سطحی نمی‌تواند بیرون از دامنه‌ی خودش چیزی بدهد.
        </div>
      </div>

      {holdingsList.length === 0 && (
        <div className="card p-6 text-center text-xs text-ink-400">در دامنه‌ی شما هلدینگی برای مدیریت وجود ندارد.</div>
      )}

      <div className="space-y-3">
        {holdingsList.map((h) => (
          <div key={h.id} className="card p-4">
            <div className="flex items-center gap-2.5 mb-3">
              <span className="w-7 h-7 rounded-lg shrink-0" style={{ backgroundColor: h.color }} />
              <p className="text-sm font-bold text-ink-900">{h.name}</p>
              <span className="text-xs text-ink-400">{h.companies.length.toLocaleString("fa-IR")} شرکت</span>
              <span className="flex-1" />
              <RowActions onEdit={() => openHoldingModal(h)} onDelete={() => removeHolding(h)} size={13} />
            </div>
            <div className="flex items-center gap-2 flex-wrap">
              {h.companies.length === 0 && (
                <span className="text-xs text-ink-400">این هلدینگ شرکت زیرمجموعه‌ای ندارد.</span>
              )}
              {h.companies.map((c) => (
                <span key={c.id} className="text-xs text-ink-700 bg-ink-50 border border-ink-100 rounded-md px-2.5 py-1.5 flex items-center gap-1.5">
                  <Building2 size={12} className="text-ink-400" /> {c.name}
                  <RowActions onEdit={() => openCompanyModal(c, h.id)} onDelete={() => removeCompany(c)} size={11} />
                </span>
              ))}
            </div>
          </div>
        ))}
      </div>

      <Modal
        open={holdingOpen}
        onClose={() => setHoldingOpen(false)}
        title={editingHolding ? "ویرایش هلدینگ" : "تعریف هلدینگ جدید"}
        description="هلدینگ، لایه‌ی میانی بین سازمان و شرکت‌هاست و دامنه‌ی انتشار محتوا را تعیین می‌کند."
      >
        <div className="space-y-3">
          <div>
            <label className="text-xs font-medium text-ink-600 block mb-1.5">نام هلدینگ <span className="text-rose-500">*</span></label>
            <input value={holdingForm.name} onChange={(e) => setHoldingForm((f) => ({ ...f, name: e.target.value }))} placeholder="مثلاً: هلدینگ ساختمان و مسکن" className="input-field" />
          </div>
          <div>
            <label className="text-xs font-medium text-ink-600 block mb-1.5">رنگ شناسه</label>
            <div className="flex items-center gap-2 flex-wrap">
              {tenantPalette.map((c) => (
                <button
                  key={c}
                  type="button"
                  aria-label={`رنگ ${c}`}
                  onClick={() => setHoldingForm((f) => ({ ...f, color: c }))}
                  className={`w-8 h-8 rounded-lg border-2 transition-colors ${holdingForm.color === c ? "border-ink-900" : "border-transparent"}`}
                  style={{ backgroundColor: c }}
                />
              ))}
            </div>
          </div>
          <div className="flex items-center gap-2 pt-2">
            <Button variant="primary" className="flex-1 justify-center" onClick={submitHolding}>
              {editingHolding ? "ذخیره تغییرات" : "ایجاد هلدینگ"}
            </Button>
            <Button variant="secondary" onClick={() => setHoldingOpen(false)}>انصراف</Button>
          </div>
        </div>
      </Modal>

      <Modal
        open={open}
        onClose={() => setOpen(false)}
        title={editingCompany ? "ویرایش شرکت" : "افزودن شرکت زیرمجموعه"}
        description="شرکت جدید زیر هلدینگ انتخابی قرار می‌گیرد و محتوای اختصاصی خودش را خواهد داشت."
      >
        <div className="space-y-3">
          <div>
            <label className="text-xs font-medium text-ink-600 block mb-1.5">نام شرکت <span className="text-rose-500">*</span></label>
            <input value={companyName} onChange={(e) => setCompanyName(e.target.value)} placeholder="مثلاً: شرکت کشت و صنعت جدید" className="input-field" />
          </div>
          <div>
            <label className="text-xs font-medium text-ink-600 block mb-1.5">هلدینگ مادر</label>
            <select value={holdingId} onChange={(e) => setHoldingId(e.target.value)} className="input-field">
              {holdingsList.map((h) => (
                <option key={h.id} value={h.id}>{h.name}</option>
              ))}
            </select>
          </div>
          <div className="flex items-center gap-2 pt-2">
            <Button variant="primary" className="flex-1 justify-center" onClick={submitCompany}>
              {editingCompany ? "ذخیره تغییرات" : "افزودن شرکت"}
            </Button>
            <Button variant="secondary" onClick={() => setOpen(false)}>انصراف</Button>
          </div>
        </div>
      </Modal>
    </div>
  );
}

type Identity = {
  name: string; short_name: string; domain: string; logo_color: string;
  sso_provider: string; sso_url: string; sso_auto_create: boolean; sso_allow_local: boolean;
};

const SSO_PROVIDERS: { id: string; label: string }[] = [
  { id: "none", label: "بدون SSO" },
  { id: "ldap", label: "LDAP / Active Directory" },
  { id: "saml", label: "SAML 2.0" },
  { id: "oidc", label: "OpenID Connect" },
  { id: "otp", label: "ورود با موبایل (OTP)" },
];
const ssoLabel = (id: string) => SSO_PROVIDERS.find((p) => p.id === id)?.label ?? "بدون SSO";

function SystemIdentitySection({ notify }: { notify: Notify }) {
  const { holdings, companies, reload } = useTenancy();
  const [saved, setSaved] = useState<Identity | null>(null);
  const [draft, setDraft] = useState<Identity | null>(null);
  const [busy, setBusy] = useState(false);

  const load = () =>
    http<Identity>("/tenant").then((t) => { setSaved(t); setDraft(t); });
  useEffect(() => { load().catch(() => {}); }, []);

  const dirty = !!draft && !!saved && JSON.stringify(draft) !== JSON.stringify(saved);

  const save = async () => {
    if (!draft) return;
    if (!draft.name.trim() || !draft.domain.trim()) {
      notify("نام سیستم و دامنه الزامی است.", "warning");
      return;
    }
    setBusy(true);
    try {
      await http("/tenant", { method: "PATCH", body: JSON.stringify({
        ...draft, name: draft.name.trim(), domain: draft.domain.trim(),
      }) });
      await load();
      await reload();          // branding and scope both read from the tenant
      notify("هویت سیستم و پیکربندی ورود یکپارچه ذخیره شد.");
    } catch (err) {
      notify(apiMessage(err, "ذخیره تنظیمات ناموفق بود."), "warning");
    } finally {
      setBusy(false);
    }
  };

  // A real reachability check. The prototype reported success unconditionally
  // and said «(نمایشی)»; a test that always passes would let a typo in the URL
  // read as a working directory.
  const testSso = async () => {
    if (!draft) return;
    if (draft.sso_provider === "none") {
      notify("ابتدا یک روش ورود یکپارچه انتخاب کنید.", "warning");
      return;
    }
    setBusy(true);
    try {
      const res = await http<{ ok: boolean; message: string }>("/settings/sso-test", {
        method: "POST",
        body: JSON.stringify({ provider: draft.sso_provider, url: draft.sso_url }),
      });
      notify(res.message, res.ok ? "success" : "warning");
    } catch (err) {
      notify(apiMessage(err, "آزمون اتصال ناموفق بود."), "warning");
    } finally {
      setBusy(false);
    }
  };

  if (!draft) return <div className="card p-6 text-center text-xs text-ink-400">در حال بارگذاری…</div>;

  return (
    <div>
      <div className="card p-4 mb-4 bg-brand-50 border-brand-200 flex items-start gap-3">
        <KeyRound size={18} className="text-brand-700 shrink-0 mt-0.5" />
        <p className="text-xs text-brand-800 leading-6">
          این نصب از محصول متعلق به <b>یک مشتری</b> است. هویت، دامنه و روش ورود در همین صفحه تعیین می‌شود؛
          تفکیک واقعی داده‌ها یک سطح پایین‌تر — در <b>هلدینگ‌ها و شرکت‌ها</b> — انجام می‌شود.
        </p>
      </div>

      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mb-4">
        <StatCard label="هلدینگ‌ها" value={holdings.length.toLocaleString("fa-IR")} tone="brand" icon={<Network size={16} />} />
        <StatCard label="شرکت‌ها" value={companies.length.toLocaleString("fa-IR")} icon={<Building2 size={16} />} />
        <StatCard label="روش ورود" value={ssoLabel(saved?.sso_provider ?? "none")} tone={(saved?.sso_provider ?? "none") === "none" ? "warning" : "success"} />
        <StatCard label="دامنه" value={saved?.domain ?? "—"} />
      </div>

      <div className="card p-4 mb-4">
        <h3 className="text-sm font-bold text-ink-900 mb-3">هویت سیستم</h3>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          <div>
            <label className="text-xs font-medium text-ink-600 block mb-1.5">نام سازمان مشتری <span className="text-rose-500">*</span></label>
            <input value={draft.name} onChange={(e) => setDraft({ ...draft, name: e.target.value })} aria-label="نام سازمان مشتری" className="input-field" />
          </div>
          <div>
            <label className="text-xs font-medium text-ink-600 block mb-1.5">نام کوتاه (در رابط کاربری)</label>
            <input value={draft.short_name} onChange={(e) => setDraft({ ...draft, short_name: e.target.value })} aria-label="نام کوتاه" className="input-field" />
          </div>
          <div>
            <label className="text-xs font-medium text-ink-600 block mb-1.5">دامنه <span className="text-rose-500">*</span></label>
            <input value={draft.domain} onChange={(e) => setDraft({ ...draft, domain: e.target.value })} aria-label="دامنه" className="input-field" dir="ltr" />
          </div>
          <div>
            <label className="text-xs font-medium text-ink-600 block mb-1.5">رنگ برند</label>
            <input type="color" value={draft.logo_color} onChange={(e) => setDraft({ ...draft, logo_color: e.target.value })} aria-label="رنگ برند" className="input-field h-[38px] p-1" />
          </div>
        </div>
      </div>

      <div className="card p-4 mb-4">
        <h3 className="text-sm font-bold text-ink-900 mb-1">ورود یکپارچه (SSO)</h3>
        <p className="text-[11.5px] text-ink-400 mb-3 leading-5">
          منبع هویت سازمان (Active Directory، SAML یا OIDC) این‌جا وصل می‌شود. این بخش به ازای هر مشتری متفاوت است.
        </p>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          <div>
            <label className="text-xs font-medium text-ink-600 block mb-1.5">روش ورود</label>
            <select value={draft.sso_provider} onChange={(e) => setDraft({ ...draft, sso_provider: e.target.value })} className="input-field" aria-label="روش ورود">
              {SSO_PROVIDERS.map((p) => <option key={p.id} value={p.id}>{p.label}</option>)}
            </select>
          </div>
          <div>
            <label className="text-xs font-medium text-ink-600 block mb-1.5">نشانی سرویس هویت</label>
            <input value={draft.sso_url} onChange={(e) => setDraft({ ...draft, sso_url: e.target.value })} className="input-field" dir="ltr" placeholder="ldaps://ad.example.ir:636" aria-label="نشانی سرویس هویت" />
          </div>
        </div>

        <div className="mt-3 space-y-2">
          <label className="flex items-center justify-between gap-2 text-xs">
            <span>
              <b className="text-ink-800">ایجاد خودکار حساب کاربران</b>
              <span className="block text-ink-400 mt-0.5">کاربرِ تاییدشده در منبع هویت، بدون دخالت راهبر ساخته می‌شود.</span>
            </span>
            <Toggle on={draft.sso_auto_create} onChange={() => setDraft({ ...draft, sso_auto_create: !draft.sso_auto_create })} label="ایجاد خودکار حساب کاربران" />
          </label>
          <label className="flex items-center justify-between gap-2 text-xs pt-2 border-t border-ink-100">
            <span>
              <b className="text-ink-800">اجازه‌ی ورود محلی در کنار SSO</b>
              <span className="block text-ink-400 mt-0.5">
                برای پیمانکاران و مهمان‌هایی که در منبع هویت سازمان نیستند. خاموش‌کردن آن با پیکربندی نادرست،
                راه ورود راهبران را هم می‌بندد.
              </span>
            </span>
            <Toggle on={draft.sso_allow_local} onChange={() => setDraft({ ...draft, sso_allow_local: !draft.sso_allow_local })} label="اجازه‌ی ورود محلی" />
          </label>
        </div>

        <div className="flex items-center gap-2 mt-4">
          <Button variant="primary" size="sm" onClick={save} disabled={!dirty || busy}>
            {busy ? "در حال ذخیره…" : dirty ? "ذخیره تغییرات" : "تغییری برای ذخیره وجود ندارد"}
          </Button>
          <Button variant="secondary" size="sm" onClick={testSso} disabled={busy}>تست اتصال</Button>
          {dirty && <Button variant="secondary" size="sm" onClick={() => setDraft(saved)}>بازگردانی</Button>}
        </div>
      </div>
    </div>
  );
}


function ModulesSection({ enabledModules, toggleModule }: { enabledModules: string[]; toggleModule: (id: string) => void }) {
  const categories = Array.from(new Set(moduleCatalog.map((m) => m.category)));
  return (
    <div>
      <div className="card p-4 mb-4 bg-brand-50 border-brand-200 flex items-start gap-3">
        <CheckCircle2 size={18} className="text-brand-700 shrink-0 mt-0.5" />
        <p className="text-xs text-brand-800 leading-6">
          هر ماژول کاملاً مستقل و قابل افزودن/حذف است. غیرفعال‌کردن یک ماژول، داده‌های آن را حذف نمی‌کند و روی
          عملکرد سایر ماژول‌ها تأثیری ندارد — معماری سامانه برای این نوع جداسازی طراحی شده است.
        </p>
      </div>

      {categories.map((cat) => (
        <div key={cat} className="mb-5">
          <h3 className="text-xs font-bold text-ink-500 mb-2">{cat}</h3>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
            {moduleCatalog
              .filter((m) => m.category === cat)
              .map((m: ModuleDef) => {
                const on = enabledModules.includes(m.id) || Boolean(m.core);
                return (
                  <div key={m.id} className={`flex items-center justify-between gap-3 p-3 rounded-lg border ${on ? "border-brand-200 bg-brand-50/50" : "border-ink-200 bg-white"}`}>
                    <div className="min-w-0">
                      <p className="text-[13px] font-medium text-ink-900 flex items-center gap-1.5">
                        {m.name}
                        {m.core && <Badge tone="navy">هسته</Badge>}
                      </p>
                      <p className="text-[11px] text-ink-400 mt-0.5">{m.description}</p>
                    </div>
                    <Toggle on={on} disabled={m.core} onChange={() => toggleModule(m.id)} />
                  </div>
                );
              })}
          </div>
        </div>
      ))}
    </div>
  );
}


function RolesSection({ roles, setRoles, notify }: { roles: RoleDef[]; setRoles: (fn: (prev: RoleDef[]) => RoleDef[]) => void; notify: Notify }) {
  const [editing, setEditing] = useState<RoleDef | "new" | null>(null);
  const confirm = useConfirm();
  const { hasPermission } = useTenancy();

  // A preset role is read-only, and a custom role can only be edited by someone
  // who already holds everything it grants. The API refuses either way; showing
  // the reason here means the refusal is not a surprise.
  const editableBy = (r: RoleDef) => !r.system && r.permissions.every(hasPermission);

  if (editing !== null) {
    return (
      <RoleEditor
        role={editing === "new" ? null : editing}
        onCancel={() => setEditing(null)}
        onSave={(saved) => {
          if (editing === "new") {
            setRoles((prev) => [...prev, saved]);
            notify(`نقش سفارشی «${saved.title}» با ${saved.permissions.length.toLocaleString("fa-IR")} دسترسی ایجاد شد. اکنون می‌توانید آن را از بخش «کاربران» به اعضای زیرمجموعه‌ی خود تخصیص دهید.`);
          } else {
            setRoles((prev) => prev.map((r) => (r.id === saved.id ? saved : r)));
            notify(`دسترسی‌های نقش «${saved.title}» به‌روزرسانی شد.`);
          }
          setEditing(null);
        }}
      />
    );
  }

  const removeRole = (role: RoleDef) =>
    confirm({
      title: `حذف نقش «${role.title}»؟`,
      message: `${role.members.toLocaleString("fa-IR")} کاربر این نقش به «عضو عادی» منتقل می‌شوند.`,
      onConfirm: () => {
        setRoles((prev) => prev.filter((r) => r.id !== role.id));
        notify(`نقش «${role.title}» حذف شد. کاربران آن به نقش «عضو عادی» منتقل می‌شوند.`, "info");
      },
    });

  return (
    <div>
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-sm font-bold text-ink-900">نقش‌ها و سطوح دسترسی</h3>
        <Button variant="primary" size="sm" icon={<Plus size={14} />} onClick={() => setEditing("new")}>
          نقش جدید
        </Button>
      </div>
      <div className="card p-4 mb-4 bg-brand-50 border-brand-200 flex items-start gap-3">
        <KeyRound size={18} className="text-brand-700 shrink-0 mt-0.5" />
        <p className="text-xs text-brand-800 leading-6">
          علاوه بر نقش‌های پایه‌ی سامانه، می‌توانید نقش کاملاً سفارشی تعریف کنید و تک‌تک دسترسی‌های هر ماژول را
          تیک بزنید، سپس از بخش «کاربران» آن را تخصیص دهید.
          <br />
          <b>قاعده‌ی واگذاری:</b> شما فقط برای زیرمجموعه‌ی خود نقش تعریف/ویرایش می‌کنید و تنها می‌توانید
          دسترسی‌هایی را بدهید که خودتان دارید. نقش‌های پایه‌ی سامانه فقط قابل مشاهده‌اند.
        </p>
      </div>
      <div className="card divide-y divide-ink-100">
        {roles.map((r) => (
          <div key={r.id} className="p-3.5 flex items-center justify-between gap-3">
            <div className="min-w-0">
              <p className="text-sm font-medium text-ink-900 flex items-center gap-2 flex-wrap">
                {r.title} <Badge tone={r.scope === "پلتفرم" ? "navy" : r.scope === "سازمان" ? "brand" : "neutral"}>{r.scope}</Badge>
                {!r.system && <Badge tone="warning">سفارشی</Badge>}
              </p>
              <p className="text-xs text-ink-400 mt-0.5">{r.description}</p>
            </div>
            <div className="flex items-center gap-3 shrink-0">
              <span className="text-xs text-ink-400 hidden sm:block">{r.permissions.length.toLocaleString("fa-IR")} دسترسی</span>
              <span className="text-xs text-ink-400 hidden sm:block">{r.members.toLocaleString("fa-IR")} نفر</span>
              <Button
                variant="secondary"
                size="sm"
                icon={<Pencil size={13} />}
                onClick={() => setEditing(r)}
                title={
                  r.system ? "این نقشِ پایه‌ی سامانه است و فقط برای مشاهده در دسترس شماست."
                  : editableBy(r) ? undefined
                  : "این نقش دسترسی‌هایی دارد که خودتان ندارید (خارج از اختیار شما)."
                }
              >
                {editableBy(r) ? "ویرایش دسترسی‌ها" : "مشاهده‌ی دسترسی‌ها"}
              </Button>
              {!r.system && editableBy(r) && (
                <button onClick={() => removeRole(r)} className="text-rose-500 hover:text-rose-700 p-1" title="حذف نقش">
                  <Trash2 size={15} />
                </button>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

function RoleEditor({ role, onSave, onCancel }: { role: RoleDef | null; onSave: (r: RoleDef) => void; onCancel: () => void }) {
  const [title, setTitle] = useState(role?.title ?? "");
  const [scope, setScope] = useState<RoleDef["scope"]>(role?.scope ?? "سازمان");
  const [description, setDescription] = useState(role?.description ?? "");
  const [selected, setSelected] = useState<Set<string>>(new Set(role?.permissions ?? []));
  const [error, setError] = useState<string | null>(null);

  const toggle = (id: string) =>
    setSelected((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });

  const { catalog: fullCatalog, allIds: allPermissionIds } = usePermissionCatalog();
  const { hasPermission } = useTenancy();

  // Only what the author already holds can be delegated. Offering the rest and
  // letting the API refuse on save would waste the operator's time and read as
  // a bug rather than a rule. Permissions the role already carries stay visible
  // so an inherited role can be inspected rather than silently truncated.
  const grantable = (id: string) => hasPermission(id) || (role?.permissions ?? []).includes(id);
  const permissionCatalog = fullCatalog
    .map((g) => ({ ...g, actions: g.actions.filter((a) => grantable(a.id)) }))
    .filter((g) => g.actions.length > 0);
  const grantableIds = permissionCatalog.flatMap((g) => g.actions).map((a) => a.id);
  const withheld = allPermissionIds.length - grantableIds.length;

  const toggleGroup = (group: PermGroup) => {
    const ids = group.actions.map((a) => a.id);
    const allOn = ids.every((id) => selected.has(id));
    setSelected((prev) => {
      const next = new Set(prev);
      ids.forEach((id) => (allOn ? next.delete(id) : next.add(id)));
      return next;
    });
  };

  const submit = () => {
    if (!title.trim()) {
      setError("عنوان نقش الزامی است.");
      return;
    }
    if (selected.size === 0) {
      setError("دست‌کم یک دسترسی برای این نقش انتخاب کنید.");
      return;
    }
    onSave({
      id: role?.id ?? `role-${Date.now()}`,
      title: title.trim(),
      scope,
      description: description.trim() || "بدون توضیحات",
      members: role?.members ?? 0,
      permissions: Array.from(selected),
      system: role?.system,
    });
  };

  return (
    <div className="space-y-5">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-bold text-ink-900 flex items-center gap-2">
          <KeyRound size={15} className="text-brand-600" />
          {role ? `ویرایش نقش «${role.title}»` : "تعریف نقش سفارشی جدید"}
        </h3>
        <Button variant="secondary" size="sm" onClick={onCancel}>بازگشت به فهرست نقش‌ها</Button>
      </div>

      <div className="card p-5">
        <h4 className="text-xs font-bold text-ink-900 mb-4">مشخصات نقش</h4>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          <div>
            <label className="text-xs font-medium text-ink-600 block mb-1.5">عنوان نقش</label>
            <input value={title} onChange={(e) => setTitle(e.target.value)} placeholder="مثلاً: ناظر مالی پروژه" className="input-field" />
          </div>
          <div>
            <label className="text-xs font-medium text-ink-600 block mb-1.5">دامنه‌ی اعمال</label>
            <select value={scope} onChange={(e) => setScope(e.target.value as RoleDef["scope"])} className="input-field">
              <option value="پلتفرم">پلتفرم</option>
              <option value="سازمان">سازمان</option>
              <option value="گروه">گروه</option>
            </select>
          </div>
          <div className="sm:col-span-2">
            <label className="text-xs font-medium text-ink-600 block mb-1.5">توضیحات نقش</label>
            <textarea value={description} onChange={(e) => setDescription(e.target.value)} placeholder="این نقش برای چه کسانی و با چه هدفی تعریف می‌شود؟" className="input-field min-h-16" />
          </div>
        </div>
      </div>

      <div className="card p-5">
        <div className="flex items-center justify-between mb-4 flex-wrap gap-2">
          <h4 className="text-xs font-bold text-ink-900">دسترسی‌ها</h4>
          <div className="flex items-center gap-3 text-xs">
            <span className="text-ink-400">
              {selected.size.toLocaleString("fa-IR")} از {grantableIds.length.toLocaleString("fa-IR")} دسترسی انتخاب شده
              {withheld > 0 && (
                <span title="این دسترسی‌ها را خودتان ندارید، پس نمی‌توانید واگذارشان کنید.">
                  {" "}· {withheld.toLocaleString("fa-IR")} مورد خارج از اختیار شما
                </span>
              )}
            </span>
            <button onClick={() => setSelected(new Set(grantableIds))} className="text-brand-600 font-medium hover:text-brand-700">
              انتخاب همه
            </button>
            <button onClick={() => setSelected(new Set())} className="text-ink-500 font-medium hover:text-ink-700">
              حذف همه
            </button>
          </div>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-3">
          {permissionCatalog.map((group) => {
            const groupIds = group.actions.map((a) => a.id);
            const onCount = groupIds.filter((id) => selected.has(id)).length;
            const allOn = onCount === groupIds.length;
            return (
              <div key={group.id} className={`rounded-lg border p-3 ${onCount > 0 ? "border-brand-200 bg-brand-50/40" : "border-ink-200 bg-white"}`}>
                <label className="flex items-center justify-between gap-2 cursor-pointer pb-2 mb-2 border-b border-ink-100">
                  <span className="text-[12.5px] font-bold text-ink-900">{group.label}</span>
                  <span className="flex items-center gap-1.5 text-[11px] text-ink-400">
                    {onCount.toLocaleString("fa-IR")}/{groupIds.length.toLocaleString("fa-IR")}
                    <input
                      type="checkbox"
                      checked={allOn}
                      ref={(el) => {
                        if (el) el.indeterminate = onCount > 0 && !allOn;
                      }}
                      onChange={() => toggleGroup(group)}
                      className="w-3.5 h-3.5 accent-brand-600"
                    />
                  </span>
                </label>
                <div className="space-y-1.5">
                  {group.actions.map((a) => (
                    <label key={a.id} className="flex items-center gap-2 cursor-pointer text-[12px] text-ink-700 hover:text-ink-900">
                      <input
                        type="checkbox"
                        checked={selected.has(a.id)}
                        onChange={() => toggle(a.id)}
                        className="w-3.5 h-3.5 accent-brand-600 shrink-0"
                      />
                      {a.label}
                    </label>
                  ))}
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {error && (
        <div className="p-3 rounded-lg bg-amber-50 border border-amber-200 text-xs text-amber-800 flex items-center gap-2">
          <AlertTriangle size={14} className="shrink-0" /> {error}
        </div>
      )}

      <div className="flex items-center gap-2">
        <Button variant="primary" className="flex-1 justify-center" onClick={submit}>
          {role ? "ذخیره‌ی تغییرات نقش" : "افزودن نقش"}
        </Button>
        <Button variant="secondary" onClick={onCancel}>انصراف</Button>
      </div>
    </div>
  );
}

function PagesSection({
  pages,
  setPages,
  extensions,
  setExtensions,
  notify,
}: {
  pages: AdminPageDef[];
  setPages: (fn: (prev: AdminPageDef[]) => AdminPageDef[]) => void;
  extensions: string[];
  setExtensions: (fn: (prev: string[]) => string[]) => void;
  notify: Notify;
}) {
  const [open, setOpen] = useState(false);
  const [title, setTitle] = useState("");
  const [slug, setSlug] = useState("");
  const [extInput, setExtInput] = useState("");

  const submitPage = () => {
    if (!title.trim() || !slug.trim()) {
      notify("عنوان و آدرس صفحه الزامی است.", "warning");
      return;
    }
    setPages((prev) => [...prev, { id: `page-${Date.now()}`, title: title.trim(), slug: slug.trim(), visible: true }]);
    notify(`صفحه‌ی سفارشی «${title.trim()}» ایجاد شد.`);
    setOpen(false);
    setTitle("");
    setSlug("");
  };

  const togglePageVisibility = (id: string) =>
    setPages((prev) => prev.map((p) => (p.id === id ? { ...p, visible: !p.visible } : p)));

  const addExtension = () => {
    const clean = extInput.trim().replace(/^\./, "").toLowerCase();
    if (!clean) return;
    if (extensions.includes(clean)) {
      notify("این پسوند از قبل در فهرست مجاز است.", "warning");
      return;
    }
    setExtensions((prev) => [...prev, clean]);
    notify(`پسوند «.${clean}» به فهرست فایل‌های مجاز افزوده شد.`);
    setExtInput("");
  };

  return (
    <div className="space-y-5">
      <div>
        <div className="flex items-center justify-between mb-2">
          <h3 className="text-sm font-bold text-ink-900">صفحات سفارشی</h3>
          <Button variant="secondary" size="sm" icon={<Plus size={13} />} onClick={() => setOpen(true)}>صفحه جدید</Button>
        </div>
        <div className="card divide-y divide-ink-100">
          {pages.map((p) => (
            <button key={p.id} onClick={() => togglePageVisibility(p.id)} className="w-full p-3 flex items-center justify-between text-right hover:bg-ink-50">
              <div>
                <p className="text-sm font-medium text-ink-900">{p.title}</p>
                <p className="text-xs text-ink-400">{p.slug}</p>
              </div>
              {p.visible ? <Eye size={15} className="text-emerald-600" /> : <EyeOff size={15} className="text-ink-300" />}
            </button>
          ))}
        </div>
      </div>

      <div>
        <h3 className="text-sm font-bold text-ink-900 mb-2">منوهای ناوبری</h3>
        <div className="card divide-y divide-ink-100">
          {adminMenus.map((m) => (
            <div key={m.id} className="p-3 flex items-center justify-between">
              <span className="text-sm text-ink-800">{m.order}. {m.title}</span>
              {m.visible ? <Eye size={15} className="text-emerald-600" /> : <EyeOff size={15} className="text-ink-300" />}
            </div>
          ))}
        </div>
      </div>

      <div>
        <h3 className="text-sm font-bold text-ink-900 mb-2">پسوندهای مجاز فایل</h3>
        <div className="card p-3 flex items-center gap-2 flex-wrap">
          {extensions.map((ext) => (
            <Badge key={ext} tone="neutral">.{ext}</Badge>
          ))}
          <input
            value={extInput}
            onChange={(e) => setExtInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && addExtension()}
            placeholder="docx"
            className="w-20 text-xs border border-ink-200 rounded-md px-2 py-1 outline-none focus:border-brand-400"
          />
          <button onClick={addExtension} className="text-xs text-brand-600 font-medium px-2">+ افزودن پسوند</button>
        </div>
      </div>

      <Modal open={open} onClose={() => setOpen(false)} title="ایجاد صفحه‌ی سفارشی جدید">
        <div className="space-y-3">
          <div>
            <label className="text-xs font-medium text-ink-600 block mb-1.5">عنوان صفحه</label>
            <input value={title} onChange={(e) => setTitle(e.target.value)} placeholder="مثلاً: درباره‌ی ما" className="input-field" />
          </div>
          <div>
            <label className="text-xs font-medium text-ink-600 block mb-1.5">آدرس صفحه (slug)</label>
            <input value={slug} onChange={(e) => setSlug(e.target.value)} placeholder="/about" className="input-field" />
          </div>
          <div className="flex items-center gap-2 pt-2">
            <Button variant="primary" className="flex-1 justify-center" onClick={submitPage}>ایجاد صفحه</Button>
            <Button variant="secondary" onClick={() => setOpen(false)}>انصراف</Button>
          </div>
        </div>
      </Modal>
    </div>
  );
}

function UsersSection({ tenant, roles, notify }: { tenant: { name: string; users: number }; roles: RoleDef[]; notify: Notify }) {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const orgUsers = useApiList<{ id: string; name: string; role: string; org: string; company?: string; avatarColor: string }>(
    "/users", fromUser as any);
  // Role assignments come from each user's role_ids on /users.
  const [assignments, setAssignments] = useState<RoleAssignment>({});
  useEffect(() => {
    http<any[]>("/users?page_size=100")
      .then((rows) => setAssignments(Object.fromEntries(rows.map((u) => [u.id, (u.role_ids ?? [])[0] ?? ""])) as RoleAssignment))
      .catch(() => {});
  }, []);

  const assignRole = (userId: string, roleId: string) => {
    setAssignments((prev) => ({ ...prev, [userId]: roleId }));
    const user = orgUsers.find((u) => u.id === userId);
    const role = roles.find((r) => r.id === roleId);
    if (user && role) {
      notify(`نقش «${role.title}» با ${role.permissions.length.toLocaleString("fa-IR")} دسترسی به «${user.name}» تخصیص یافت.`);
    }
  };

  // Reads the file the operator actually chose and reports what is in it.
  // The old version divided the byte count by eighty and announced that many
  // users had been imported — a number invented from the file's size, for an
  // import that never ran.
  const handleImport = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    e.target.value = "";
    try {
      const text = await file.text();
      const rows = text.split(/\r?\n/).map((l) => l.trim()).filter(Boolean).slice(1);
      if (rows.length === 0) {
        notify("فایل خالی است یا فقط سرستون دارد.", "warning");
        return;
      }
      const created: string[] = [];
      const failed: string[] = [];
      for (const row of rows) {
        const [name, phone, title] = row.split(",").map((c) => c.trim());
        if (!name) continue;
        try {
          await http("/users", { method: "POST", body: JSON.stringify({ name, phone, title }) });
          created.push(name);
        } catch {
          failed.push(name);
        }
      }
      notify(
        `فایل «${file.name}»: ${created.length.toLocaleString("fa-IR")} کاربر ساخته شد` +
          (failed.length ? ` · ${failed.length.toLocaleString("fa-IR")} مورد ناموفق.` : "."),
        failed.length ? "warning" : "success",
      );
    } catch (err) {
      notify(apiMessage(err, "خواندن فایل ناموفق بود."), "warning");
    }
  };

  const downloadSample = () => {
    const csv = "نام و نام خانوادگی,شماره موبایل,سمت سازمانی\nکاربر نمونه یک,09121234567,کارشناس روابط‌عمومی\nکاربر نمونه دو,09351234567,کارشناس منابع انسانی\n";
    const blob = new Blob(["﻿" + csv], { type: "text/csv;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "نمونه-واردسازی-کاربران.csv";
    a.click();
    URL.revokeObjectURL(url);
    notify("فایل نمونه دانلود شد.", "info");
  };

  return (
    <div className="space-y-4">
      <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
        <StatCard label="کل کاربران" value={tenant.users.toLocaleString("fa-IR")} icon={<Users size={16} />} tone="brand" />
        <StatCard label="کاربران فعال این هفته" value="۸۶۴" tone="success" />
        <StatCard label="در انتظار تایید" value="۱۲" tone="warning" />
      </div>

      <div className="card p-5">
        <div className="flex items-center justify-between mb-1">
          <h3 className="text-sm font-bold text-ink-900 flex items-center gap-1.5">
            <UserCog size={15} className="text-ink-500" /> تخصیص نقش به کاربران
          </h3>
          <span className="text-[11px] text-ink-400">نقش‌های سفارشی را از بخش «نقش‌ها و دسترسی» تعریف کنید</span>
        </div>
        <p className="text-xs text-ink-400 mb-3">
          هر کاربر دقیقاً به اندازه‌ی دسترسی‌های تیک‌خورده‌ی نقشِ تخصیص‌یافته، به بخش‌های سامانه دسترسی خواهد داشت.
          <br />
          <b>دامنه‌ی سازمانی کاربران:</b> کاربر عضویتش را انتخاب نمی‌کند — دامنه‌ی دیدش خودکار از روی عضویت
          محاسبه می‌شود؛ فقط اگر عضو بیش از یک شرکت باشد، سوییچر بالای صفحه برایش ظاهر می‌شود.
          شما فقط کاربران زیرمجموعه‌ی خودتان را می‌بینید.
        </p>
        <div className="divide-y divide-ink-100 border border-ink-100 rounded-lg">
          {orgUsers.map((u) => {
            const assigned = roles.find((r) => r.id === assignments[u.id]) ?? roles.find((r) => r.id === "r4");
            return (
              <div key={u.id} className="p-3 flex items-center justify-between gap-3 flex-wrap">
                <div className="flex items-center gap-3 min-w-0">
                  <span className="w-8 h-8 rounded-full shrink-0 flex items-center justify-center text-white text-xs font-bold" style={{ backgroundColor: u.avatarColor }}>
                    {u.name.slice(0, 1)}
                  </span>
                  <div className="min-w-0">
                    <p className="text-sm font-medium text-ink-900 truncate">{u.name}</p>
                    <p className="text-[11px] text-ink-400 truncate">
                      {u.role} · {u.org}
                      {u.company && <> · <span className="text-ink-500">دامنه‌ی دسترسی: {u.company}</span></>}
                    </p>
                  </div>
                </div>
                <div className="flex items-center gap-2 shrink-0">
                  {assigned && (
                    <span className="text-[11px] text-ink-400 hidden md:block">
                      {assigned.permissions.length.toLocaleString("fa-IR")} دسترسی
                    </span>
                  )}
                  <select
                    value={assignments[u.id] ?? "r4"}
                    onChange={(e) => assignRole(u.id, e.target.value)}
                    className="text-xs border border-ink-200 rounded-md px-2 py-1.5 outline-none focus:border-brand-400 bg-white"
                  >
                    {roles.map((r) => (
                      <option key={r.id} value={r.id}>
                        {r.title}{!r.system ? " (سفارشی)" : ""}
                      </option>
                    ))}
                  </select>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      <div className="card p-5">
        <h3 className="text-sm font-bold text-ink-900 mb-1">واردسازی دسته‌ای کاربران</h3>
        <p className="text-xs text-ink-400 mb-3">فایل اکسل حاوی نام، شماره موبایل و سمت سازمانی کاربران را بارگذاری کنید.</p>
        <div className="flex items-center gap-2">
          <input ref={fileInputRef} type="file" accept=".xlsx,.xls,.csv" className="hidden" onChange={handleImport} />
          <Button variant="primary" icon={<Upload size={14} />} onClick={() => fileInputRef.current?.click()}>بارگذاری فایل اکسل</Button>
          <Button variant="secondary" icon={<Download size={14} />} onClick={downloadSample}>دانلود نمونه فایل</Button>
        </div>
      </div>
    </div>
  );
}

function IntegrationsSection({
  integrations,
  setIntegrations,
  notify,
}: {
  integrations: Integration[];
  setIntegrations: (fn: (prev: Integration[]) => Integration[]) => void;
  notify: Notify;
}) {
  const typeIcon = { "وب‌هوک ورودی": Webhook, "وب‌هوک خروجی": Webhook, بات: Bot, "دستور اسلش": Slash } as const;
  const [open, setOpen] = useState(false);
  const [name, setName] = useState("");
  const [type, setType] = useState<Integration["type"]>("وب‌هوک ورودی");
  const [channel, setChannel] = useState("");

  const submit = () => {
    if (!name.trim() || !channel.trim()) {
      notify("نام و کانال هدف الزامی است.", "warning");
      return;
    }
    const newIntegration: Integration = { id: `ig-${Date.now()}`, name: name.trim(), type, channel: channel.trim(), status: "فعال", createdBy: me().name };
    setIntegrations((prev) => [newIntegration, ...prev]);
    notify(`یکپارچه‌سازی «${newIntegration.name}» ایجاد شد و اکنون فعال است.`);
    setOpen(false);
    setName("");
    setChannel("");
    setType("وب‌هوک ورودی");
  };

  return (
    <div className="space-y-4">
      <div className="card p-4 bg-brand-50 border-brand-200 flex items-start gap-3">
        <Webhook size={18} className="text-brand-700 shrink-0 mt-0.5" />
        <p className="text-xs text-brand-800 leading-6">
          وب‌هوک‌های ورودی/خروجی، بات‌ها و دستورهای اسلش به کانال‌های ارتباطی متصل می‌شوند تا ابزارهای دیگر سازمان
          (CI/CD، فرم‌ساز، تیکتینگ و...) بتوانند به‌صورت خودکار در گفتگوها پیام بدهند یا از آن‌ها داده بگیرند.
        </p>
      </div>

      <div className="flex items-center justify-between">
        <h3 className="text-sm font-bold text-ink-900">یکپارچه‌سازی‌های فعال</h3>
        <Button variant="primary" size="sm" icon={<Plus size={14} />} onClick={() => setOpen(true)}>افزودن یکپارچه‌سازی</Button>
      </div>

      <div className="card divide-y divide-ink-100">
        {integrations.map((i) => {
          const Icon = typeIcon[i.type];
          return (
            <div key={i.id} className="p-3.5 flex items-center justify-between gap-3">
              <div className="flex items-center gap-3 min-w-0">
                <span className="w-9 h-9 rounded-lg bg-ink-100 text-ink-500 flex items-center justify-center shrink-0">
                  <Icon size={15} />
                </span>
                <div className="min-w-0">
                  <p className="text-sm font-medium text-ink-900 truncate">{i.name}</p>
                  <p className="text-xs text-ink-400">{i.type} · کانال: {i.channel} · سازنده: {i.createdBy}</p>
                </div>
              </div>
              <Badge tone={i.status === "فعال" ? "success" : "neutral"}>{i.status}</Badge>
            </div>
          );
        })}
      </div>

      <Modal open={open} onClose={() => setOpen(false)} title="افزودن یکپارچه‌سازی جدید">
        <div className="space-y-3">
          <div>
            <label className="text-xs font-medium text-ink-600 block mb-1.5">نام یکپارچه‌سازی</label>
            <input value={name} onChange={(e) => setName(e.target.value)} placeholder="مثلاً: اعلان استقرار نسخه‌ی جدید" className="input-field" />
          </div>
          <div>
            <label className="text-xs font-medium text-ink-600 block mb-1.5">نوع</label>
            <select value={type} onChange={(e) => setType(e.target.value as Integration["type"])} className="input-field">
              <option value="وب‌هوک ورودی">وب‌هوک ورودی</option>
              <option value="وب‌هوک خروجی">وب‌هوک خروجی</option>
              <option value="بات">بات</option>
              <option value="دستور اسلش">دستور اسلش</option>
            </select>
          </div>
          <div>
            <label className="text-xs font-medium text-ink-600 block mb-1.5">کانال هدف</label>
            <input value={channel} onChange={(e) => setChannel(e.target.value)} placeholder="فاز-یک-فنی" className="input-field" />
          </div>
          <div className="flex items-center gap-2 pt-2">
            <Button variant="primary" className="flex-1 justify-center" onClick={submit}>ایجاد</Button>
            <Button variant="secondary" onClick={() => setOpen(false)}>انصراف</Button>
          </div>
        </div>
      </Modal>
    </div>
  );
}

function SecurityToggleCard({ title, description, icon, defaultOn, notify }: { title: string; description: string; icon?: React.ReactNode; defaultOn: boolean; notify: Notify }) {
  const [on, setOn] = useState(defaultOn);
  return (
    <div className="card p-4 flex items-center justify-between">
      <div>
        <p className="text-sm font-medium text-ink-900 flex items-center gap-1.5">{icon}{title}</p>
        <p className="text-xs text-ink-400 mt-0.5">{description}</p>
      </div>
      <Toggle
        on={on}
        onChange={() => {
          setOn((v) => !v);
          notify(`${title}: ${!on ? "فعال" : "غیرفعال"} شد.`, "info");
        }}
      />
    </div>
  );
}

function SecuritySection({
  guestAccounts,
  setGuestAccounts,
  notify,
}: {
  guestAccounts: GuestAccount[];
  setGuestAccounts: (fn: (prev: GuestAccount[]) => GuestAccount[]) => void;
  notify: Notify;
}) {
  const [open, setOpen] = useState(false);
  const [name, setName] = useState("");
  const [org, setOrg] = useState("");
  const [channels, setChannels] = useState("");
  const [expires, setExpires] = useState("");

  const submit = () => {
    if (!name.trim() || !org.trim()) {
      notify("نام و سازمان مهمان الزامی است.", "warning");
      return;
    }
    const newGuest: GuestAccount = {
      id: `gu-${Date.now()}`,
      name: name.trim(),
      org: org.trim(),
      channels: channels.split("،").map((c) => c.trim()).filter(Boolean),
      expires: expires.trim() || "نامشخص",
    };
    setGuestAccounts((prev) => [...prev, newGuest]);
    notify(`دعوت‌نامه‌ی مهمان برای «${newGuest.name}» ارسال شد.`);
    setOpen(false);
    setName("");
    setOrg("");
    setChannels("");
    setExpires("");
  };

  const exportCompliance = () => {
    const report = {
      generatedAt: new Date().toISOString(),
      tenant: "گزارش جامع انطباق و رخدادهای امنیتی",
      events: [
        "۳ تلاش ناموفق ورود از IP ناشناس",
        "اسکن دوره‌ای فایل‌های میزبان با موفقیت انجام شد",
        "درخواست خروجی استعلام‌پذیر (eDiscovery) برای واحد حقوقی ثبت شد",
      ],
    };
    const blob = new Blob([JSON.stringify(report, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "گزارش-انطباق.json";
    a.click();
    URL.revokeObjectURL(url);
    notify("خروجی انطباق آماده و دانلود شد.", "info");
  };

  return (
    <div className="space-y-4">
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
        <SecurityToggleCard title="نمایش کپچا در فرم ورود" description="جلوگیری از ورود ربات‌ها به فرم احراز هویت" defaultOn notify={notify} />
        <SecurityToggleCard title="اسکن ضدویروس پیوست‌ها (ClamAV)" description="عدم ذخیره‌ی فایل‌های آلوده و اطلاع‌رسانی به کاربر" defaultOn notify={notify} />
        <SecurityToggleCard title="محدودسازی نرخ درخواست" description="حداکثر ۶۰ درخواست در دقیقه به ازای هر کاربر" defaultOn notify={notify} />
        <SecurityToggleCard title="ثبت کامل رخدادها (Audit Log)" description="آماده برای ارائه به نهادهای نظارتی مانند افتا" defaultOn notify={notify} />
        <SecurityToggleCard
          title="برچسب طبقه‌بندی پیام (Classification Banner)"
          description="نمایش نوار «محرمانه / عمومی / ویژه» بالای کانال‌های حساس"
          icon={<Tag size={13} className="text-ink-400" />}
          defaultOn={false}
          notify={notify}
        />
        <SecurityToggleCard title="پیام خودسوز (Burn-on-Read)" description="حذف خودکار پیام‌های بسیار حساس پس از مشاهده" defaultOn={false} notify={notify} />
      </div>

      <div className="card p-4">
        <div className="flex items-center justify-between mb-3">
          <h3 className="text-sm font-bold text-ink-900 flex items-center gap-1.5">
            <UserCog size={15} className="text-ink-500" /> حساب‌های مهمان (Guest Accounts)
          </h3>
          <Button variant="secondary" size="sm" icon={<Plus size={13} />} onClick={() => setOpen(true)}>دعوت مهمان</Button>
        </div>
        <p className="text-xs text-ink-400 mb-3">دسترسی محدود برای افراد خارج از سازمان (مثل ناظر یا مشاور) فقط به کانال‌های مشخص.</p>
        {guestAccounts.length === 0 ? (
          <p className="text-xs text-ink-400">حساب مهمانی ثبت نشده.</p>
        ) : (
          <div className="space-y-2">
            {guestAccounts.map((g) => (
              <div key={g.id} className="flex items-center justify-between text-xs border border-ink-100 rounded-lg p-2.5">
                <div>
                  <p className="font-medium text-ink-800">{g.name}</p>
                  <p className="text-ink-400 mt-0.5">{g.org} · دسترسی: {g.channels.join("، ") || "—"}</p>
                </div>
                <span className="text-ink-400">انقضا {g.expires}</span>
              </div>
            ))}
          </div>
        )}
      </div>

      <div className="card p-4">
        <h3 className="text-sm font-bold text-ink-900 mb-3 flex items-center gap-1.5">
          <Ban size={15} className="text-rose-600" /> کاربران مسدودشده
        </h3>
        <p className="text-xs text-ink-400">در حال حاضر کاربر مسدودشده‌ای وجود ندارد.</p>
      </div>

      <div className="card p-4">
        <div className="flex items-center justify-between mb-3">
          <h3 className="text-sm font-bold text-ink-900">آخرین رخدادهای امنیتی</h3>
          <Button variant="secondary" size="sm" icon={<Download size={13} />} onClick={exportCompliance}>خروجی انطباق (Compliance Export)</Button>
        </div>
        <ul className="space-y-2 text-xs text-ink-500">
          <li className="flex items-center gap-2"><AlertTriangle size={13} className="text-amber-500" /> ۳ تلاش ناموفق ورود از IP ناشناس — ۲ ساعت پیش</li>
          <li className="flex items-center gap-2"><CheckCircle2 size={13} className="text-emerald-500" /> اسکن دوره‌ای فایل‌های میزبان با موفقیت انجام شد — امروز ۰۳:۰۰</li>
          <li className="flex items-center gap-2"><FileWarning size={13} className="text-ink-400" /> درخواست خروجی استعلام‌پذیر (eDiscovery) برای واحد حقوقی ثبت شد — دیروز</li>
        </ul>
      </div>

      <Modal open={open} onClose={() => setOpen(false)} title="دعوت حساب مهمان جدید" description="حساب مهمان فقط به کانال‌های مشخص‌شده دسترسی دارد و به سایر اطلاعات سازمان دسترسی ندارد.">
        <div className="space-y-3">
          <div>
            <label className="text-xs font-medium text-ink-600 block mb-1.5">نام و نام خانوادگی</label>
            <input value={name} onChange={(e) => setName(e.target.value)} placeholder="مثلاً: مهندس ناظر طرح" className="input-field" />
          </div>
          <div>
            <label className="text-xs font-medium text-ink-600 block mb-1.5">سازمان مهمان</label>
            <input value={org} onChange={(e) => setOrg(e.target.value)} placeholder="مثلاً: شرکت مشاور فنی" className="input-field" />
          </div>
          <div>
            <label className="text-xs font-medium text-ink-600 block mb-1.5">کانال‌های قابل دسترس (با «،» جدا کنید)</label>
            <input value={channels} onChange={(e) => setChannels(e.target.value)} placeholder="فاز-یک-فنی" className="input-field" />
          </div>
          <div>
            <label className="text-xs font-medium text-ink-600 block mb-1.5">تاریخ انقضا</label>
            <input value={expires} onChange={(e) => setExpires(e.target.value)} placeholder="۱۴۰۵/۰۶/۰۱" className="input-field" />
          </div>
          <div className="flex items-center gap-2 pt-2">
            <Button variant="primary" className="flex-1 justify-center" onClick={submit}>ارسال دعوت‌نامه</Button>
            <Button variant="secondary" onClick={() => setOpen(false)}>انصراف</Button>
          </div>
        </div>
      </Modal>
    </div>
  );
}

function NetworkSection({ crossTenant, setCrossTenant }: { crossTenant: boolean; setCrossTenant: (v: boolean) => void }) {
  return (
    <div className="card p-5">
      <div className="flex items-start gap-3">
        <span className="w-10 h-10 rounded-lg bg-navy-900 text-white flex items-center justify-center shrink-0">
          <Globe2 size={18} />
        </span>
        <div className="flex-1">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-bold text-ink-900">تعامل بین اعضای مجموعه‌های مختلف بنیاد</h3>
            <Toggle on={crossTenant} onChange={() => setCrossTenant(!crossTenant)} />
          </div>
          <p className="text-xs text-ink-500 mt-2 leading-6">
            با فعال‌سازی این گزینه، اعضای این سازمان می‌توانند با اعضای سایر مجموعه‌هایی که از این سامانه استفاده
            می‌کنند، در فضاهای مشترک (مثلاً گروه‌های بین‌سازمانی عمومی) تعامل داشته باشند — بدون اینکه به داده‌های
            داخلی و خصوصی هیچ سازمانی دسترسی پیدا کنند. این قابلیت به‌صورت پیش‌فرض غیرفعال است.
          </p>
          {crossTenant && (
            <div className="mt-3 p-3 rounded-lg bg-amber-50 border border-amber-200 text-xs text-amber-800 flex items-start gap-2">
              <AlertTriangle size={14} className="shrink-0 mt-0.5" />
              فعال‌سازی این قابلیت نیازمند تأیید مدیر پلتفرم و تعریف فضای اشتراکی بین‌سازمانی است.
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
