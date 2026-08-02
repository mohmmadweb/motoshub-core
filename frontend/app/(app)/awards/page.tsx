"use client";
import Badge from "@/components/ui/Badge";
import AddButton from "@/components/common/AddButton";
import Card from "@/components/ui/Card";
import { useList } from "@/hooks/useContent";
import { faNum } from "@/lib/format";
import type { AwardTrack } from "@/types";

const st: Record<string, string> = { submitted: "ثبت‌شده", validating: "صحت‌سنجی", judging: "داوری", scored: "امتیازدهی‌شده", finalist: "منتخب نهایی" };

export default function AwardsPage() {
  const { data, isLoading } = useList<AwardTrack>("awards/tracks");
  const tracks = data?.data ?? [];
  return (
    <div>
      <div className="mb-4 flex items-center justify-between"><h1 className="text-lg font-bold text-ink-900">جایزه نوآوری</h1><AddButton resource="awards/tracks" label="محور جدید" transform={(v) => ({ ...v, categories: String(v.categories || "").split(",").map((x) => x.trim()).filter(Boolean) })} fields={[{ name: "title", label: "عنوان محور", required: true },{ name: "categories", label: "دسته‌ها (با کاما)", placeholder: "نرم‌افزار, سخت‌افزار" }]} /></div>
      {isLoading && <Card className="p-8 text-center text-sm text-ink-400">در حال بارگذاری…</Card>}
      <div className="space-y-4">
        {tracks.map((t) => (
          <Card key={t.id} className="p-4">
            <div className="mb-3 flex items-center justify-between">
              <h3 className="font-semibold text-ink-900">{t.title}</h3>
              <span className="text-xs text-ink-400">{faNum(t.submission_count)} اثر</span>
            </div>
            <div className="space-y-2">
              {t.entries.map((e) => (
                <div key={e.id} className="flex items-center justify-between rounded-lg bg-ink-50 p-2 text-sm">
                  <span className="text-ink-800">{e.title} <span className="text-ink-400">· {e.company}</span></span>
                  <span className="flex items-center gap-2">
                    {e.score != null && <span className="text-xs text-amber-600">{faNum(e.score)}</span>}
                    <Badge tone="neutral">{st[e.status] ?? e.status}</Badge>
                  </span>
                </div>
              ))}
              {t.entries.length === 0 && <p className="text-xs text-ink-400">اثری ثبت نشده.</p>}
            </div>
          </Card>
        ))}
      </div>
      {!isLoading && tracks.length === 0 && <Card className="p-8 text-center text-sm text-ink-400">محوری تعریف نشده است.</Card>}
    </div>
  );
}
