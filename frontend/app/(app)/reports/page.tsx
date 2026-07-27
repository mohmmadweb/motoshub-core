"use client";
import { useQuery } from "@tanstack/react-query";

import Card from "@/components/ui/Card";
import { api, type Envelope } from "@/lib/api";
import { faNum } from "@/lib/format";
import type { ReportSummary } from "@/types";

const totalLabels: Record<string, string> = {
  projects: "پروژه‌ها", contracts: "قراردادها", funds: "طرح‌های صندوق", tickets: "تیکت‌ها", award_entries: "آثار جایزه",
};

function Breakdown({ title, data }: { title: string; data: Record<string, number> }) {
  const total = Object.values(data).reduce((s, n) => s + n, 0) || 1;
  return (
    <Card className="p-4">
      <p className="mb-3 text-sm font-semibold text-ink-700">{title}</p>
      <div className="space-y-2">
        {Object.entries(data).map(([k, n]) => (
          <div key={k}>
            <div className="mb-1 flex justify-between text-xs text-ink-500"><span>{k}</span><span>{faNum(n)}</span></div>
            <div className="h-1.5 overflow-hidden rounded-full bg-ink-100"><div className="h-full rounded-full bg-brand-500" style={{ width: `${(n / total) * 100}%` }} /></div>
          </div>
        ))}
        {Object.keys(data).length === 0 && <p className="text-xs text-ink-400">داده‌ای نیست.</p>}
      </div>
    </Card>
  );
}

export default function ReportsPage() {
  const { data, isError } = useQuery({
    queryKey: ["reports/summary"],
    queryFn: async () => (await api.get<Envelope<ReportSummary>>("/reports/summary")).data.data,
  });
  if (isError) return <Card className="p-8 text-center text-sm text-red-600">دسترسی به گزارش‌ها مجاز نیست.</Card>;
  if (!data) return <Card className="p-8 text-center text-sm text-ink-400">در حال بارگذاری…</Card>;

  return (
    <div>
      <h1 className="mb-4 text-lg font-bold text-ink-900">گزارش‌گیری</h1>
      <div className="mb-4 grid grid-cols-2 gap-4 lg:grid-cols-5">
        {Object.entries(data.totals).map(([k, n]) => (
          <Card key={k} className="p-4">
            <p className="text-xs text-ink-400">{totalLabels[k] ?? k}</p>
            <p className="text-2xl font-bold text-ink-900">{faNum(n)}</p>
          </Card>
        ))}
      </div>
      <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
        <Breakdown title="پروژه‌ها بر اساس سلامت" data={data.projects_by_health} />
        <Breakdown title="قراردادها بر اساس مرحله" data={data.contracts_by_stage} />
        <Breakdown title="طرح‌های صندوق بر اساس مرحله" data={data.funds_by_stage} />
        <Breakdown title="تیکت‌ها بر اساس وضعیت" data={data.tickets_by_status} />
      </div>
    </div>
  );
}
