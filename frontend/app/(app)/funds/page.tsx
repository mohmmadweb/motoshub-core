"use client";
import Link from "next/link";

import Badge from "@/components/ui/Badge";
import AddButton from "@/components/common/AddButton";
import RowActions from "@/components/common/RowActions";
import { fields } from "@/lib/moduleFields";
import Card from "@/components/ui/Card";
import { useList } from "@/hooks/useContent";
import { faNum } from "@/lib/format";
import { stageLabel } from "@/lib/nfStages";
import type { NfProject } from "@/types";

export default function FundsPage() {
  const { data, isLoading } = useList<NfProject>("funds/projects");
  const rows = data?.data ?? [];
  return (
    <div>
      <div className="mb-4 flex items-center justify-between"><h1 className="text-lg font-bold text-ink-900">صندوق نوآور</h1><AddButton resource="funds/projects" label="طرح جدید" fields={[{ name: "code", label: "کد طرح", required: true, placeholder: "NF-1405-0001" },{ name: "title_fa", label: "عنوان", required: true },{ name: "field", label: "حوزه" },{ name: "budget", label: "بودجه (ریال)", type: "number", default: 0 },{ name: "stage", label: "مرحله", type: "select", default: "proposal", options: [{ value: "proposal", label: "دریافت پروپوزال" }, { value: "screening", label: "ارزیابی اولیه" }] }]} /></div>
      {isLoading && <Card className="p-8 text-center text-sm text-ink-400">در حال بارگذاری…</Card>}
      <div className="space-y-3">
        {rows.map((p) => (
          <Link key={p.id} href={`/funds/${p.id}`}>
            <Card className="p-4 transition-shadow hover:shadow-md">
              <div className="flex items-center justify-between gap-3">
                <div className="min-w-0">
                  <div className="flex items-center gap-2">
                    <span className="font-semibold text-ink-900">{p.title_fa}</span>
                    {p.green_path && <Badge tone="success">مسیر سبز</Badge>}
                  </div>
                  <p className="mt-0.5 text-xs text-ink-400">{p.code} · {p.rahbar || "—"} · {faNum(p.budget)} ریال</p>
                </div>
                <span className="flex items-center gap-1">
                  <Badge tone="brand">{stageLabel(p.stage)}</Badge>
                  <RowActions resource="funds/projects" id={p.id} fields={fields.funds} initial={{ code: p.code, title_fa: p.title_fa, field: p.field, budget: p.budget }} />
                </span>
              </div>
              <div className="mt-3 h-1.5 overflow-hidden rounded-full bg-ink-100">
                <div className="h-full rounded-full bg-emerald-500" style={{ width: `${p.progress}%` }} />
              </div>
            </Card>
          </Link>
        ))}
      </div>
      {!isLoading && rows.length === 0 && <Card className="p-8 text-center text-sm text-ink-400">طرحی ثبت نشده است.</Card>}
    </div>
  );
}
