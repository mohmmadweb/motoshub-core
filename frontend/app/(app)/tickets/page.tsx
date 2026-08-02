"use client";
import Link from "next/link";
import Badge from "@/components/ui/Badge";
import AddButton from "@/components/common/AddButton";
import Card from "@/components/ui/Card";
import { useList } from "@/hooks/useContent";
import { faDate } from "@/lib/format";
import type { Ticket } from "@/types";

const prio: Record<string, { tone: "neutral" | "warning" | "success"; label: string }> = {
  low: { tone: "neutral", label: "کم" }, medium: { tone: "warning", label: "متوسط" }, urgent: { tone: "success", label: "فوری" },
};
const st: Record<string, string> = { open: "باز", in_review: "در حال بررسی", answered: "پاسخ داده شد", closed: "بسته" };

export default function TicketsPage() {
  const { data, isLoading } = useList<Ticket>("tickets");
  const rows = data?.data ?? [];
  return (
    <div>
      <div className="mb-4 flex items-center justify-between"><h1 className="text-lg font-bold text-ink-900">تیکت‌های پشتیبانی</h1><AddButton resource="tickets" label="تیکت جدید" fields={[{ name: "subject", label: "موضوع", required: true },{ name: "category", label: "دسته" },{ name: "priority", label: "اولویت", type: "select", default: "medium", options: [{ value: "low", label: "کم" }, { value: "medium", label: "متوسط" }, { value: "urgent", label: "فوری" }] }]} /></div>
      {isLoading && <Card className="p-8 text-center text-sm text-ink-400">در حال بارگذاری…</Card>}
      <Card className="divide-y divide-ink-200">
        {rows.map((t) => (
          <div key={t.id} className="flex items-center justify-between gap-3 p-4">
            <div className="min-w-0">
              <div className="flex items-center gap-2">
                <Link href={`/tickets/${t.id}`} className="font-medium text-ink-900 hover:text-brand-700">{t.subject}</Link>
                <Badge tone={prio[t.priority]?.tone}>{prio[t.priority]?.label}</Badge>
              </div>
              <p className="mt-0.5 text-xs text-ink-400">{t.number} · {t.category} · {faDate(t.created_at)}</p>
            </div>
            <Badge tone="neutral">{st[t.status]}</Badge>
          </div>
        ))}
        {!isLoading && rows.length === 0 && <div className="p-8 text-center text-sm text-ink-400">تیکتی ثبت نشده است.</div>}
      </Card>
    </div>
  );
}
