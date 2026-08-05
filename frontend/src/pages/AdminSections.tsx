import { useEffect, useState } from "react";
import { http, apiMessage } from "../lib/http";
import {
  SlidersHorizontal,
  HardDrive,
  Database,
  Trash2,
  RefreshCw,
  Archive,
  FolderOpen,
  AlertTriangle,
} from "lucide-react";
import Badge from "../components/ui/Badge";
import Button from "../components/ui/Button";
import Toggle from "../components/ui/Toggle";
import StatCard from "../components/ui/StatCard";

type Notify = (message: string, tone?: "success" | "info" | "warning") => void;

const defaultSystemSettings = [
  {
    group: "آپلود و فایل",
    items: [
      { key: "upload_max_mb", label: "حداکثر حجم آپلود (مگابایت)", value: "100", hint: "برای هر فایل؛ فایل‌های بزرگ‌تر به صورت چندتکه (chunk) ارسال می‌شوند" },
      { key: "chunk_size_mb", label: "اندازه هر تکه آپلود (مگابایت)", value: "10", hint: "کوچک‌تر = پایدارتر روی اینترنت ضعیف، بزرگ‌تر = سریع‌تر" },
      { key: "user_quota_gb", label: "سهمیه دیسک هر کاربر (گیگابایت)", value: "5", hint: "پس از پر شدن، آپلود جدید مسدود می‌شود" },
      { key: "image_max_px", label: "حداکثر ابعاد تصویر (پیکسل)", value: "1920", hint: "تصاویر بزرگ‌تر به این ابعاد کوچک می‌شوند" },
    ],
  },
  {
    group: "نشست و امنیت",
    items: [
      { key: "session_hours", label: "طول عمر نشست (ساعت)", value: "24", hint: "پس از این مدت کاربر باید دوباره وارد شود" },
      { key: "login_attempts", label: "حداکثر تلاش ناموفق ورود", value: "5", hint: "پس از آن حساب موقتاً قفل می‌شود" },
      { key: "lock_minutes", label: "مدت قفل حساب (دقیقه)", value: "15", hint: "" },
    ],
  },
  {
    group: "محتوا و اعلان",
    items: [
      { key: "feed_page_size", label: "تعداد آیتم هر صفحه فید", value: "20", hint: "" },
      { key: "notif_batch", label: "حداکثر اعلان ارسالی در هر دقیقه", value: "500", hint: "برای کنترل فشار روی صف اعلان‌ها" },
      { key: "digest_hour", label: "ساعت ارسال خلاصه روزانه", value: "8", hint: "به وقت سرور" },
    ],
  },
];

export function SystemSection({ notify }: { notify: Notify }) {
  const [settings, setSettings] = useState(defaultSystemSettings);
  const [maintenance, setMaintenance] = useState(false);
  const [dirty, setDirty] = useState(false);

  const updateValue = (groupIdx: number, itemIdx: number, value: string) => {
    setSettings((prev) =>
      prev.map((g, gi) =>
        gi === groupIdx ? { ...g, items: g.items.map((it, ii) => (ii === itemIdx ? { ...it, value } : it)) } : g
      )
    );
    setDirty(true);
  };

  const save = () => {
    setDirty(false);
    notify("تنظیمات سیستم ذخیره شد و بدون نیاز به دیپلوی مجدد روی همه سرویس‌ها اعمال می‌شود.");
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
            <Button variant="primary" size="sm" onClick={save} disabled={!dirty}>
              ذخیره تغییرات
            </Button>
          </div>
        </div>
      </div>

      {settings.map((group, gi) => (
        <div key={group.group} className="card p-5">
          <h4 className="text-sm font-bold text-ink-900 mb-4">{group.group}</h4>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {group.items.map((item, ii) => (
              <div key={item.key}>
                <label className="text-xs font-medium text-ink-600 block mb-1.5">{item.label}</label>
                <input
                  value={item.value}
                  onChange={(e) => updateValue(gi, ii, e.target.value)}
                  className="input-field"
                  dir="ltr"
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
            <Toggle
              on={maintenance}
              onChange={() => {
                setMaintenance(!maintenance);
                notify(!maintenance ? "حالت تعمیر فعال شد — فقط راهبران به سامانه دسترسی دارند." : "حالت تعمیر غیرفعال شد.", "info");
              }}
            />
          </div>
          <p className="text-xs text-ink-500 mt-2 leading-6">
            با فعال‌سازی، کاربران عادی صفحه‌ی «در حال به‌روزرسانی» می‌بینند و فقط راهبران وارد می‌شوند.
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

const EMPTY_USAGE: StorageUsage = {
  disk_total_gb: 0, disk_used_gb: 0, disk_free_gb: 0,
  attachments_gb: 0, attachments_files: 0, database_gb: 0,
  categories: [], top_consumers: [], orphan_records: 0,
};

export function StorageSection({ notify }: { notify: Notify }) {
  const [usage, setUsage] = useState<StorageUsage>(EMPTY_USAGE);
  const [cleaning, setCleaning] = useState(false);

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
                <p className="text-ink-400 mt-0.5">تولید مجدد پیش‌نمایش تصاویر پس از تغییر ابعاد</p>
              </div>
              <Button variant="secondary" size="sm" icon={<RefreshCw size={13} />} onClick={() => notify("بازسازی بندانگشتی‌ها در صف پردازش قرار گرفت.", "info")}>
                شروع
              </Button>
            </div>
            <div className="flex items-center justify-between gap-2 text-xs pt-3 border-t border-ink-100">
              <div>
                <p className="font-medium text-ink-800">پشتیبان‌گیری دستی</p>
                <p className="text-ink-400 mt-0.5">علاوه بر پشتیبان‌گیری خودکار روزانه</p>
              </div>
              <Button variant="secondary" size="sm" icon={<Archive size={13} />} onClick={() => notify("پشتیبان‌گیری کامل آغاز شد — پس از اتمام اعلان دریافت می‌کنید.", "info")}>
                شروع
              </Button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
