"use client";
import Badge from "@/components/ui/Badge";
import Card from "@/components/ui/Card";
import { useList } from "@/hooks/useContent";
import { faNum } from "@/lib/format";
import type { ResearchOpportunity } from "@/types";

const stage: Record<string, string> = { open: "فراخوان باز", review: "بررسی درخواست‌ها", judging: "داوری", running: "در حال اجرا", closed: "پایان‌یافته" };

export default function ResearchPage() {
  const { data, isLoading } = useList<ResearchOpportunity>("research");
  const rows = data?.data ?? [];
  return (
    <div>
      <h1 className="mb-4 text-lg font-bold text-ink-900">پژوهش</h1>
      {isLoading && <Card className="p-8 text-center text-sm text-ink-400">در حال بارگذاری…</Card>}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
        {rows.map((r) => (
          <Card key={r.id} className="p-4">
            <div className="mb-2 flex items-center justify-between">
              <h3 className="font-semibold text-ink-900">{r.title}</h3>
              <Badge tone="brand">{stage[r.stage]}</Badge>
            </div>
            <p className="text-xs text-ink-400">{r.field} · ناظر: {r.supervisor || "—"}</p>
            <p className="mt-2 text-xs text-ink-400">{faNum(r.applicant_count)} متقاضی · بودجه {faNum(r.budget)} ریال</p>
          </Card>
        ))}
      </div>
      {!isLoading && rows.length === 0 && <Card className="p-8 text-center text-sm text-ink-400">فراخوانی موجود نیست.</Card>}
    </div>
  );
}
