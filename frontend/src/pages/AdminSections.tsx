import { useEffect, useState } from "react";
import { http, apiMessage } from "../lib/http";
import {
  SlidersHorizontal,
  RefreshCw,
  HardDrive,
  Database,
  Trash2,
  Archive,
  FolderOpen,
  AlertTriangle,
} from "lucide-react";
import Badge from "../components/ui/Badge";
import Button from "../components/ui/Button";
import Toggle from "../components/ui/Toggle";
import StatCard from "../components/ui/StatCard";

type Notify = (message: string, tone?: "success" | "info" | "warning") => void;

// The panel's field layout. Values are never hardcoded here — each `key` maps
// to a column on the tenant's WorkflowSettings row, loaded and saved over
// /settings/workflow. `upload_max_mb` and `maintenance_mode` are enforced
// server-side, so the switch and the limit do what the labels claim.
const systemFieldGroups: { group: string; items: { key: string; label: string; hint: string }[] }[] = [
  {
    group: "آپلود و فایل",
    items: [
      { key: "upload_max_mb", label: "حداکثر حجم آپلود (مگابایت)", hint: "برای هر فایل؛ سقف سرور ۲۵ مگابایت است و مقدار بزرگ‌تر تا همان محدود می‌شود" },
      { key: "chunk_size_mb", label: "اندازه هر تکه آپلود (مگابایت)", hint: "کوچک‌تر = پایدارتر روی اینترنت ضعیف، بزرگ‌تر = سریع‌تر" },
      { key: "user_quota_gb", label: "سهمیه دیسک هر کاربر (گیگابایت)", hint: "پس از پر شدن، آپلود جدید مسدود می‌شود" },
      { key: "image_max_px", label: "حداکثر ابعاد تصویر (پیکسل)", hint: "تصاویر بزرگ‌تر به این ابعاد کوچک می‌شوند" },
    ],
  },
  {
    group: "نشست و امنیت",
    items: [
      { key: "session_hours", label: "طول عمر نشست (ساعت)", hint: "پس از این مدت کاربر باید دوباره وارد شود" },
      { key: "login_attempts", label: "حداکثر تلاش ناموفق ورود", hint: "پس از آن حساب موقتاً قفل می‌شود" },
      { key: "lock_minutes", label: "مدت قفل حساب (دقیقه)", hint: "" },
      { key: "rate_limit_per_minute", label: "سقف درخواست در دقیقه", hint: "محدودسازی نرخ درخواست هر کاربر" },
    ],
  },
  {
    group: "محتوا و اعلان",
    items: [
      { key: "feed_page_size", label: "تعداد آیتم هر صفحه فید", hint: "" },
      { key: "notif_batch", label: "حداکثر اعلان ارسالی در هر دقیقه", hint: "برای کنترل فشار روی صف اعلان‌ها" },
      { key: "digest_hour", label: "ساعت ارسال خلاصه روزانه", hint: "به وقت سرور" },
    ],
  },
];

type SettingsPayload = Record<string, unknown>;

export function SystemSection({ notify }: { notify: Notify }) {
  const [values, setValues] = useState<Record<string, string>>({});
  const [maintenance, setMaintenance] = useState(false);
  const [dirty, setDirty] = useState(false);
  const [saving, setSaving] = useState(false);

  const load = () =>
    http<SettingsPayload>("/settings/workflow").then((cfg) => {
      const next: Record<string, string> = {};
      systemFieldGroups.forEach((g) => g.items.forEach((it) => { next[it.key] = String(cfg[it.key] ?? ""); }));
      setValues(next);
      setMaintenance(!!cfg.maintenance_mode);
      setDirty(false);
    });
  useEffect(() => { load().catch(() => {}); }, []);

  const updateValue = (key: string, value: string) => {
    setValues((prev) => ({ ...prev, [key]: value }));
    setDirty(true);
  };

  const persist = async (patch: SettingsPayload, message: string) => {
    setSaving(true);
    try {
      await http("/settings/workflow", { method: "PUT", body: JSON.stringify(patch) });
      await load();
      notify(message);
    } catch (err) {
      notify(apiMessage(err, "ذخیره تنظیمات ناموفق بود."), "warning");
      await load().catch(() => {});   // never leave the form showing unsaved values
    } finally {
      setSaving(false);
    }
  };

  const save = () => {
    const patch: SettingsPayload = {};
    Object.entries(values).forEach(([k, v]) => { patch[k] = Number(v) || 0; });
    persist(patch, "تنظیمات سیستم ذخیره شد و بدون نیاز به دیپلوی مجدد اعمال می‌شود.");
  };

  const toggleMaintenance = () => {
    const next = !maintenance;
    persist(
      { maintenance_mode: next },
      next ? "حالت تعمیر فعال شد — فقط راهبران به سامانه دسترسی دارند." : "حالت تعمیر غیرفعال شد.",
    );
  };

  return (
    <div className="space-y-5">
      <div className="card p-4 flex items-start gap-3">
        <span className="w-10 h-10 rounded-lg bg-navy-900 text-white flex items-center justify-center shrink-0">
          <SlidersHorizontal size={18} />
        </span>
        <div className="flex-1">
          <div className="flex items-center justify-between gap-2 flex-wrap">
            <div>
              <h3 className="text-sm font-bold text-ink-900">متغیرهای سیستم</h3>
              <p className="text-xs text-ink-500 mt-1">
                همه‌ی مقادیر ثابت سیستم از اینجا مدیریت می‌شوند — بدون تغییر کد و بدون دیپلوی مجدد.
              </p>
            </div>
            <Button variant="primary" size="sm" onClick={save} disabled={!dirty || saving}>
              {saving ? "در حال ذخیره…" : dirty ? "ذخیره تغییرات" : "تغییری برای ذخیره وجود ندارد"}
            </Button>
          </div>
        </div>
      </div>

      {systemFieldGroups.map((group) => (
        <div key={group.group} className="card p-5">
          <h4 className="text-sm font-bold text-ink-900 mb-4">{group.group}</h4>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {group.items.map((item) => (
              <div key={item.key}>
                <label className="text-xs font-medium text-ink-600 block mb-1.5" htmlFor={`sys-${item.key}`}>{item.label}</label>
                <input
                  id={`sys-${item.key}`}
                  value={values[item.key] ?? ""}
                  onChange={(e) => updateValue(item.key, e.target.value)}
                  className="input-field"
                  dir="ltr"
                  inputMode="numeric"
                />
                {item.hint && <p className="text-[11px] text-ink-400 mt-1">{item.hint}</p>}
              </div>
            ))}
          </div>
        </div>
      ))}

      <div className="card p-4 flex items-start gap-3">
        <span className="w-10 h-10 rounded-lg bg-rose-50 text-rose-600 flex items-center justify-center shrink-0">
          <AlertTriangle size={18} />
        </span>
        <div className="flex-1">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-bold text-ink-900">حالت تعمیر و نگهداری</h3>
            <Toggle on={maintenance} disabled={saving} onChange={toggleMaintenance} label="حالت تعمیر و نگهداری" />
          </div>
          <p className="text-xs text-ink-500 mt-2 leading-6">
            با فعال‌سازی، درخواست‌های کاربران عادی با پاسخ «در حال به‌روزرسانی» رد می‌شوند و فقط
            دارندگان دسترسی «تنظیمات سیستم» می‌توانند کار کنند.
          </p>
        </div>
      </div>
    </div>
  );
}

type StorageCategory = { kind: string; label: string; color: string; sizeGb: number; files: number };
type StorageConsumer = { id: string; name: string; type: string; sizeGb: number; files: number };
type StorageUsage = {
  disk_total_gb: number; disk_used_gb: number; disk_free_gb: number;
  attachments_gb: number; attachments_files: number; database_gb: number;
  categories: StorageCategory[]; top_consumers: StorageConsumer[]; orphan_records: number;
};

type BackupFile = { name: string; size: number; human_size: string; created_at: number };

const EMPTY_USAGE: StorageUsage = {
  disk_total_gb: 0, disk_used_gb: 0, disk_free_gb: 0,
  attachments_gb: 0, attachments_files: 0, database_gb: 0,
  categories: [], top_consumers: [], orphan_records: 0,
};

export function StorageSection({ notify }: { notify: Notify }) {
  const [usage, setUsage] = useState<StorageUsage>(EMPTY_USAGE);
  const [cleaning, setCleaning] = useState(false);
  const [thumbing, setThumbing] = useState(false);
  const [backingUp, setBackingUp] = useState(false);
  const [backups, setBackups] = useState<BackupFile[]>([]);

  const loadBackups = () =>
    http<{ backups: BackupFile[] }>("/settings/backups").then((r) => setBackups(r.backups));
  useEffect(() => { loadBackups().catch(() => setBackups([])); }, []);

  // Rebuilds every image preview. This is what «بازسازی» means after the
  // thumbnail size changes; the routine case is filling gaps, which the API
  // exposes as ?missing=1.
  const rebuildThumbnails = async () => {
    setThumbing(true);
    try {
      const res = await http<{ built: number; failed: number; total: number }>(
        "/settings/storage/thumbnails", { method: "POST" },
      );
      await loadUsage();
      notify(
        res.total === 0
          ? "تصویری برای بازسازی وجود ندارد."
          : `${res.built.toLocaleString("fa-IR")} بندانگشتی ساخته شد` +
            (res.failed ? ` · ${res.failed.toLocaleString("fa-IR")} تصویر قابل پردازش نبود.` : "."),
        res.failed ? "warning" : "success",
      );
    } catch (err) {
      notify(apiMessage(err, "بازسازی بندانگشتی‌ها ناموفق بود."), "warning");
    } finally {
      setThumbing(false);
    }
  };

  const takeBackup = async () => {
    setBackingUp(true);
    try {
      const res = await http<BackupFile>("/settings/backups", { method: "POST" });
      await loadBackups();
      notify(`پشتیبان «${res.name}» گرفته شد (${res.human_size}).`);
    } catch (err) {
      notify(apiMessage(err, "پشتیبان‌گیری ناموفق بود."), "warning");
    } finally {
      setBackingUp(false);
    }
  };

  // A plain <a href> would reach the endpoint without the bearer token and be
  // refused, so the file is fetched and handed to the browser as a blob.
  const downloadBackup = async (name: string) => {
    try {
      const res = await fetch(`/api/v1/settings/backups/${name}`, {
        headers: { Authorization: `Bearer ${localStorage.getItem("ms-access") ?? ""}` },
      });
      if (!res.ok) throw new Error();
      const url = URL.createObjectURL(await res.blob());
      const a = document.createElement("a");
      a.href = url;
      a.download = name;
      a.click();
      URL.revokeObjectURL(url);
    } catch {
      notify("دانلود پشتیبان ناموفق بود.", "warning");
    }
  };

  const removeBackup = async (name: string) => {
    try {
      await http(`/settings/backups/${name}`, { method: "DELETE" });
      await loadBackups();
      notify("پشتیبان حذف شد.", "info");
    } catch (err) {
      notify(apiMessage(err, "حذف پشتیبان ناموفق بود."), "warning");
    }
  };

  const loadUsage = () => http<StorageUsage>("/settings/storage").then(setUsage);
  useEffect(() => { loadUsage().catch(() => {}); }, []);

  const storageCategories = usage.categories;
  const topConsumers = usage.top_consumers;
  const totalGb = usage.disk_total_gb;
  const usedGb = usage.disk_used_gb;
  const usedPct = totalGb ? Math.round((usedGb / totalGb) * 100) : 0;
  // Guards the width calculation below when every category is still zero.
  const largestGb = Math.max(1e-9, ...storageCategories.map((x) => x.sizeGb));

  const cleanTemp = async () => {
    setCleaning(true);
    try {
      const res = await http<{ removed: number }>("/settings/storage", { method: "POST" });
      await loadUsage();
      notify(
        res.removed > 0
          ? `${res.removed.toLocaleString("fa-IR")} رکورد بدون فایل پاک‌سازی شد.`
          : "رکورد بدون فایلی برای پاک‌سازی یافت نشد.",
        res.removed > 0 ? "success" : "info"
      );
    } catch (err) {
      notify(apiMessage(err, "پاک‌سازی ناموفق بود."), "warning");
    } finally {
      setCleaning(false);
    }
  };

  return (
    <div className="space-y-5">
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        <StatCard label="فضای کل دیسک" value={`${totalGb.toLocaleString("fa-IR")} GB`} icon={<HardDrive size={16} />} tone="brand" />
        <StatCard label="فضای مصرف‌شده" value={`${usedGb.toFixed(1)} GB`} hint={`${usedPct.toLocaleString("fa-IR")}٪ از کل`} tone={usedPct > 80 ? "danger" : "success"} icon={<Database size={16} />} />
        <StatCard label="تعداد کل فایل‌ها" value={usage.attachments_files.toLocaleString("fa-IR")} hint={`${usage.attachments_gb.toFixed(2)} GB پیوست`} icon={<FolderOpen size={16} />} />
        <StatCard label="حجم پایگاه داده" value={`${usage.database_gb.toFixed(2)} GB`} hint="پشتیبان‌گیری روزانه — خودکار" tone="success" icon={<Archive size={16} />} />
      </div>

      <div className="card p-5">
        <div className="flex items-center justify-between text-xs mb-2">
          <h4 className="text-sm font-bold text-ink-900">مصرف کل دیسک</h4>
          <span className="text-ink-500">{usedGb.toFixed(1)} از {totalGb.toLocaleString("fa-IR")} گیگابایت</span>
        </div>
        <div className="h-3 rounded-full bg-ink-100 overflow-hidden flex">
          {storageCategories.map((c) => (
            <div key={c.label} className={`h-full ${c.color}`} style={{ width: `${(c.sizeGb / totalGb) * 100}%` }} title={c.label} />
          ))}
        </div>
        <div className="flex flex-wrap gap-x-4 gap-y-1 mt-3">
          {storageCategories.map((c) => (
            <span key={c.label} className="flex items-center gap-1.5 text-[11px] text-ink-500">
              <span className={`w-2.5 h-2.5 rounded-sm ${c.color}`} />
              {c.label} ({c.sizeGb} GB)
            </span>
          ))}
        </div>
      </div>

      <div className="card p-5">
        <h4 className="text-sm font-bold text-ink-900 mb-4">تفکیک بر اساس نوع محتوا</h4>
        <div className="space-y-3">
          {storageCategories.map((c) => (
            <div key={c.label}>
              <div className="flex items-center justify-between text-xs mb-1">
                <span className="text-ink-600">{c.label}</span>
                <span className="text-ink-400">{c.sizeGb} GB · {c.files.toLocaleString("fa-IR")} فایل</span>
              </div>
              <div className="h-2 rounded-full bg-ink-100 overflow-hidden">
                <div className={`h-full rounded-full ${c.color}`} style={{ width: `${(c.sizeGb / largestGb) * 100}%` }} />
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <div className="card p-5">
          <h4 className="text-sm font-bold text-ink-900 mb-3">پرمصرف‌ترین‌ها</h4>
          <div className="space-y-2">
            {topConsumers.length === 0 && <p className="text-xs text-ink-400">هنوز فایلی بارگذاری نشده است.</p>}
            {topConsumers.map((t) => (
              <div key={t.id} className="flex items-center justify-between text-xs bg-ink-50 rounded-lg p-2.5">
                <div>
                  <p className="font-medium text-ink-800">{t.name}</p>
                  <p className="text-ink-400 mt-0.5">{t.type} · {t.files.toLocaleString("fa-IR")} فایل</p>
                </div>
                <Badge tone="brand">{t.sizeGb} GB</Badge>
              </div>
            ))}
          </div>
        </div>

        <div className="card p-5">
          <h4 className="text-sm font-bold text-ink-900 mb-3">نگه‌داری و پاک‌سازی</h4>
          <div className="space-y-3">
            <div className="flex items-center justify-between gap-2 text-xs">
              <div>
                <p className="font-medium text-ink-800">پاک‌سازی رکوردهای بدون فایل</p>
                <p className="text-ink-400 mt-0.5">{usage.orphan_records.toLocaleString("fa-IR")} رکورد که فایلشان روی دیسک نیست (فایلی حذف نمی‌شود)</p>
              </div>
              <Button variant="secondary" size="sm" icon={<Trash2 size={13} />} onClick={cleanTemp} disabled={cleaning}>
                {cleaning ? "در حال پاک‌سازی…" : "پاک‌سازی"}
              </Button>
            </div>
            <div className="flex items-center justify-between gap-2 text-xs pt-3 border-t border-ink-100">
              <div>
                <p className="font-medium text-ink-800">بازسازی بندانگشتی‌ها</p>
                <p className="text-ink-400 mt-0.5">
                  تولید مجدد پیش‌نمایش {(usage.categories.find((c) => c.kind === "photo")?.files ?? 0).toLocaleString("fa-IR")} تصویر
                </p>
              </div>
              <Button variant="secondary" size="sm" icon={<RefreshCw size={13} />} onClick={rebuildThumbnails} disabled={thumbing}>
                {thumbing ? "در حال بازسازی…" : "بازسازی"}
              </Button>
            </div>

            <div className="pt-3 border-t border-ink-100">
              <div className="flex items-center justify-between gap-2 text-xs">
                <div>
                  <p className="font-medium text-ink-800">پشتیبان‌گیری دستی</p>
                  <p className="text-ink-400 mt-0.5">
                    علاوه بر پشتیبان‌گیری خودکار روزانه که سرویس مستقلی انجام می‌دهد
                  </p>
                </div>
                <Button variant="secondary" size="sm" icon={<Archive size={13} />} onClick={takeBackup} disabled={backingUp}>
                  {backingUp ? "در حال تهیه…" : "تهیه پشتیبان"}
                </Button>
              </div>

              {backups.length > 0 && (
                <div className="mt-3 space-y-1.5">
                  {backups.slice(0, 6).map((b) => (
                    <div key={b.name} className="flex items-center justify-between gap-2 bg-ink-50 rounded-lg px-2.5 py-2">
                      <span className="text-[11px] text-ink-700 font-mono truncate" dir="ltr">{b.name}</span>
                      <span className="flex items-center gap-2 shrink-0">
                        <span className="text-[11px] text-ink-400">{b.human_size}</span>
                        <button onClick={() => downloadBackup(b.name)} className="text-[11px] text-brand-600 hover:underline">
                          دانلود
                        </button>
                        <button onClick={() => removeBackup(b.name)} className="text-ink-300 hover:text-rose-600" title="حذف پشتیبان">
                          <Trash2 size={12} />
                        </button>
                      </span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
