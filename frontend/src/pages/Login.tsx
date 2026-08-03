import { useEffect, useState } from "react";
import { login as apiLogin } from "../lib/auth";
import { useNavigate } from "react-router-dom";
import { Building2, Lock, Smartphone, ShieldCheck, ChevronDown, Network } from "lucide-react";
import { http } from "../lib/http";
import Button from "../components/ui/Button";

// فضای کاری = سازمان مشتری (tenant) یا یکی از شرکت‌های زیرمجموعه‌ی آن —
// هماهنگ با «پنل راهبری ← سازمان‌های مشتری» و «هلدینگ‌ها و شرکت‌ها»
type Workspace = { id: string; name: string; domain: string; color: string; parent?: string };

// Loaded from the unauthenticated /public/tenants endpoint (no mock org list).
function usePublicWorkspaces(): Workspace[] {
  const [workspaces, setWorkspaces] = useState<Workspace[]>([]);
  useEffect(() => {
    http<{ id: string; name: string; domain: string; logo_color: string }[]>("/public/tenants")
      .then((rows) => setWorkspaces(rows.map((t) => ({ id: t.id, name: t.name, domain: t.domain, color: t.logo_color }))))
      .catch(() => setWorkspaces([]));
  }, []);
  return workspaces;
}

export default function Login() {
  const navigate = useNavigate();
  const workspaces = usePublicWorkspaces();
  const [tenantId, setTenantId] = useState("");
  const [orgPickerOpen, setOrgPickerOpen] = useState(false);
  const [mode, setMode] = useState<"password" | "otp">("password");
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null); setLoading(true);
    try { await apiLogin(username.trim(), password); navigate("/dashboard"); }
    catch { setError("نام کاربری یا گذرواژه نادرست است."); }
    finally { setLoading(false); }
  };
  // Default to the first org once the list arrives.
  useEffect(() => {
    setTenantId((cur) => cur || (workspaces[0]?.id ?? ""));
  }, [workspaces]);
  const tenant = workspaces.find((t) => t.id === tenantId) ?? { id: "", name: "سازمان", domain: "", color: "#1f4f99" };

  return (
    <div dir="rtl" className="min-h-screen flex items-center justify-center bg-navy-900 px-4">
      <div className="w-full max-w-sm">
        <div className="card p-7">
          <div className="flex flex-col items-center text-center mb-6">
            <span
              className="w-12 h-12 rounded-xl flex items-center justify-center text-white mb-3"
              style={{ backgroundColor: tenant.color }}
            >
              <Building2 size={22} />
            </span>
            {tenant.parent && (
              <p className="text-[11px] text-ink-400 mb-0.5 flex items-center gap-1">
                <Network size={11} /> زیرمجموعه‌ی {tenant.parent}
              </p>
            )}
            <h1 className="font-bold text-base text-ink-900">ورود به فضای کاری {tenant.name}</h1>
            <p className="text-xs text-ink-500 mt-1">{tenant.domain}</p>
          </div>

          {/* Tenant switcher — demonstrates per-organization isolated login */}
          <div className="relative mb-4">
            <button
              onClick={() => setOrgPickerOpen((v) => !v)}
              className="w-full flex items-center justify-between border border-ink-200 rounded-lg px-3 py-2 text-xs text-ink-500 hover:border-ink-300"
            >
              <span>سازمان دیگری دارید؟ تغییر فضای کاری</span>
              <ChevronDown size={14} />
            </button>
            {orgPickerOpen && (
              <div className="absolute z-10 mt-1 w-full bg-white border border-ink-200 rounded-lg shadow-lg py-1 max-h-72 overflow-y-auto">
                <p className="px-3 py-1 text-[10.5px] font-bold text-ink-400">سازمان‌های مشتری</p>
                {workspaces.map((t) => (
                  <button
                    key={t.id}
                    onClick={() => {
                      setTenantId(t.id);
                      setOrgPickerOpen(false);
                    }}
                    className={`w-full flex items-center gap-2 px-3 py-2 text-xs hover:bg-ink-50 text-right ${tenantId === t.id ? "bg-brand-50 font-bold" : ""}`}
                  >
                    <span className="w-5 h-5 rounded shrink-0" style={{ backgroundColor: t.color }} />
                    {t.name}
                  </button>
                ))}
                {workspaces.length === 0 && (
                  <p className="px-3 py-2 text-[11px] text-ink-400">سازمانی در دسترس نیست.</p>
                )}
              </div>
            )}
          </div>

          <div className="flex items-center gap-1 bg-ink-100 rounded-lg p-1 mb-4">
            <button
              onClick={() => setMode("password")}
              className={`flex-1 flex items-center justify-center gap-1.5 py-1.5 rounded-md text-xs font-medium ${
                mode === "password" ? "bg-white shadow text-brand-700" : "text-ink-500"
              }`}
            >
              <Lock size={13} /> نام‌کاربری/گذرواژه
            </button>
            <button
              onClick={() => setMode("otp")}
              className={`flex-1 flex items-center justify-center gap-1.5 py-1.5 rounded-md text-xs font-medium ${
                mode === "otp" ? "bg-white shadow text-brand-700" : "text-ink-500"
              }`}
            >
              <Smartphone size={13} /> رمز یک‌بارمصرف
            </button>
          </div>

          <form className="space-y-3" onSubmit={submit}>
            {mode === "password" ? (
              <>
                <input className="input-field" placeholder="نام کاربری یا ایمیل سازمانی" value={username} onChange={(e) => setUsername(e.target.value)} />
                <input type="password" className="input-field" placeholder="گذرواژه" value={password} onChange={(e) => setPassword(e.target.value)} />
              </>
            ) : (
              <input className="input-field" placeholder="شماره موبایل (مثلاً 0912xxxxxxx)" value={username} onChange={(e) => setUsername(e.target.value)} />
            )}
            {error && <p className="text-[12px] text-red-600">{error}</p>}
            <Button type="submit" variant="primary" className="w-full justify-center" disabled={loading}>
              {loading ? "در حال ورود…" : "ورود به سامانه بنیاد"}
            </Button>
            <p className="text-[11px] text-ink-400 text-center">نمونه: admin / demo1234</p>
          </form>

          <button className="w-full mt-3 flex items-center justify-center gap-1.5 text-xs text-ink-500 hover:text-ink-700 py-2">
            <ShieldCheck size={14} /> ورود از طریق SSO سازمانی
          </button>
        </div>

        <p className="text-[11px] text-navy-300 text-center mt-4">
          هر سازمان، فضای کاری، اعضا و ورود کاملاً مستقل خودش را دارد و از سایر مجموعه‌های بنیاد جدا است.
        </p>
      </div>
    </div>
  );
}
