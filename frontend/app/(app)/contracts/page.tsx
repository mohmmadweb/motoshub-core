"use client";
import Badge from "@/components/ui/Badge";
import AddButton from "@/components/common/AddButton";
import Card from "@/components/ui/Card";
import { useList } from "@/hooks/useContent";
import { faNum, faDate } from "@/lib/format";
import type { Contract } from "@/types";

const stage: Record<string, { tone: "neutral" | "warning" | "brand" | "success"; label: string }> = {
  negotiation: { tone: "neutral", label: "مذاکره" },
  rfp: { tone: "brand", label: "فراخوان" },
  evaluation: { tone: "warning", label: "داوری" },
  executing: { tone: "brand", label: "در حال اجرا" },
  settled: { tone: "success", label: "تسویه‌شده" },
};

export default function ContractsPage() {
  const { data, isLoading } = useList<Contract>("contracts");
  const rows = data?.data ?? [];
  return (
    <div>
      <div className="mb-4 flex items-center justify-between">
        <h1 className="text-lg font-bold text-ink-900">قراردادها</h1>
        <AddButton resource="contracts" label="قرارداد جدید" fields={[
          { name: "title", label: "عنوان", required: true },
          { name: "vendor", label: "طرف قرارداد" },
          { name: "contract_type", label: "نوع", type: "select", default: "service", options: [
            { value: "tech", label: "فناورانه" }, { value: "research", label: "پژوهشی" }, { value: "construction", label: "عمرانی" }, { value: "service", label: "خدماتی" }] },
          { name: "method", label: "روش", type: "select", default: "public_call", options: [
            { value: "public_call", label: "فراخوان عمومی" }, { value: "limited", label: "استعلام محدود" }, { value: "no_tender", label: "ترک تشریفات" }] },
          { name: "value", label: "مبلغ (ریال)", type: "number", default: 0 },
        ]} />
      </div>
      {isLoading && <Card className="p-8 text-center text-sm text-ink-400">در حال بارگذاری…</Card>}
      <Card className="overflow-hidden">
        <table className="hidden w-full text-right sm:table">
          <thead>
            <tr className="bg-ink-100 text-[11px] uppercase tracking-wide text-ink-400">
              <th className="px-4 py-2 font-semibold">عنوان</th>
              <th className="px-4 py-2 font-semibold">طرف قرارداد</th>
              <th className="px-4 py-2 font-semibold">مرحله</th>
              <th className="px-4 py-2 font-semibold">مبلغ (ریال)</th>
              <th className="px-4 py-2 font-semibold">مهلت</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-ink-200">
            {rows.map((c) => (
              <tr key={c.id} className="text-sm text-ink-800">
                <td className="px-4 py-3 font-medium text-ink-900">{c.title}</td>
                <td className="px-4 py-3 text-ink-500">{c.vendor || "—"}</td>
                <td className="px-4 py-3"><Badge tone={stage[c.stage]?.tone}>{stage[c.stage]?.label}</Badge></td>
                <td className="px-4 py-3">{faNum(c.value)}</td>
                <td className="px-4 py-3 text-xs text-ink-400">{c.deadline ? faDate(c.deadline) : "—"}</td>
              </tr>
            ))}
          </tbody>
        </table>
        <div className="divide-y divide-ink-200 sm:hidden">
          {rows.map((c) => (
            <div key={c.id} className="space-y-1.5 p-4">
              <div className="flex items-center justify-between"><span className="font-medium text-ink-900">{c.title}</span><Badge tone={stage[c.stage]?.tone}>{stage[c.stage]?.label}</Badge></div>
              <p className="text-xs text-ink-400">{c.vendor} · {faNum(c.value)} ریال</p>
            </div>
          ))}
        </div>
        {!isLoading && rows.length === 0 && <div className="p-8 text-center text-sm text-ink-400">قراردادی ثبت نشده است.</div>}
      </Card>
    </div>
  );
}
