"use client";
import { useQuery } from "@tanstack/react-query";
import { useParams } from "next/navigation";

import Badge from "@/components/ui/Badge";
import Card from "@/components/ui/Card";
import { api, type Envelope } from "@/lib/api";
import { faNum } from "@/lib/format";
import { NF_STAGES } from "@/lib/nfStages";

export default function FundDetailPage() {
  const { id } = useParams<{ id: string }>();
  const { data } = useQuery({
    queryKey: ["funds/projects", id],
    queryFn: async () => (await api.get<Envelope<any>>(`/funds/projects/${id}`)).data.data,
  });
  if (!data) return <Card className="p-8 text-center text-sm text-ink-400">در حال بارگذاری…</Card>;
  const activeIdx = NF_STAGES.findIndex((s) => s.key === data.stage);

  return (
    <div className="space-y-4">
      <div>
        <h1 className="text-lg font-bold text-ink-900">{data.title_fa}</h1>
        <p className="text-xs text-ink-400">{data.code} · {faNum(data.budget)} ریال · سهم صندوق {faNum(data.share_percent)}٪</p>
      </div>

      {/* stage pipeline */}
      <Card className="p-4">
        <p className="mb-3 text-sm font-semibold text-ink-700">خط‌لولهٔ مراحل</p>
        <div className="flex flex-wrap gap-2">
          {NF_STAGES.map((s, i) => (
            <span key={s.key} className={`rounded-full px-3 py-1 text-xs ${
              i < activeIdx ? "bg-emerald-50 text-emerald-700"
              : i === activeIdx ? "bg-brand-600 text-white"
              : "bg-ink-100 text-ink-400"}`}>{s.label}</span>
          ))}
        </div>
      </Card>

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
        <Card className="p-4">
          <p className="mb-2 text-sm font-semibold text-ink-700">گزارش‌ها</p>
          <div className="space-y-2">
            {(data.reports ?? []).map((r: any) => (
              <div key={r.id} className="flex items-center justify-between text-sm">
                <span className="text-ink-800">{r.title}</span>
                <Badge tone={r.status === "approved" ? "success" : "warning"}>{r.status}</Badge>
              </div>
            ))}
            {(data.reports ?? []).length === 0 && <p className="text-xs text-ink-400">—</p>}
          </div>
        </Card>
        <Card className="p-4">
          <p className="mb-2 text-sm font-semibold text-ink-700">پرداخت‌ها</p>
          <div className="space-y-2">
            {(data.payments ?? []).map((p: any) => (
              <div key={p.id} className="flex items-center justify-between text-sm">
                <span className="text-ink-800">{p.title}</span>
                <span className="text-xs text-ink-400">{faNum(p.amount)} ریال</span>
              </div>
            ))}
            {(data.payments ?? []).length === 0 && <p className="text-xs text-ink-400">—</p>}
          </div>
        </Card>
      </div>
    </div>
  );
}
