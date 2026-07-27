"use client";
import { type ReactNode } from "react";

import Badge from "@/components/ui/Badge";
import Card from "@/components/ui/Card";
import { useList } from "@/hooks/useContent";
import { faDate } from "@/lib/format";

export interface Column<T> {
  key: string;
  label: string;
  render: (row: T) => ReactNode;
}

interface Props<T> {
  resource: string;
  title: string;
  columns: Column<T>[];
}

/** Generic tenant-scoped list: desktop table + mobile cards, envelope-aware. */
export default function ContentList<T extends { id: string; created_at: string; visibility?: string }>({
  resource, title, columns,
}: Props<T>) {
  const { data, isLoading, isError } = useList<T>(resource);
  const rows = data?.data ?? [];

  return (
    <div>
      <div className="mb-4 flex items-center justify-between">
        <h1 className="text-lg font-bold text-ink-900">{title}</h1>
        {data?.meta && <span className="text-xs text-ink-400">{data.meta.count.toLocaleString("fa-IR")} مورد</span>}
      </div>

      {isLoading && <Card className="p-8 text-center text-sm text-ink-400">در حال بارگذاری…</Card>}
      {isError && <Card className="p-8 text-center text-sm text-red-600">خطا در دریافت داده.</Card>}

      {!isLoading && !isError && rows.length === 0 && (
        <Card className="p-8 text-center text-sm text-ink-400">موردی ثبت نشده است.</Card>
      )}

      {rows.length > 0 && (
        <Card className="overflow-hidden">
          {/* desktop */}
          <table className="hidden w-full text-right sm:table">
            <thead>
              <tr className="bg-ink-100 text-[11px] uppercase tracking-wide text-ink-400">
                {columns.map((c) => <th key={c.key} className="px-4 py-2 font-semibold">{c.label}</th>)}
                <th className="px-4 py-2 font-semibold">تاریخ</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-ink-200">
              {rows.map((row) => (
                <tr key={row.id} className="text-sm text-ink-800">
                  {columns.map((c) => <td key={c.key} className="px-4 py-3">{c.render(row)}</td>)}
                  <td className="px-4 py-3 text-xs text-ink-400">{faDate(row.created_at)}</td>
                </tr>
              ))}
            </tbody>
          </table>
          {/* mobile */}
          <div className="divide-y divide-ink-200 sm:hidden">
            {rows.map((row) => (
              <div key={row.id} className="space-y-2 p-4">
                {columns.map((c) => (
                  <div key={c.key} className="flex justify-between gap-3 text-sm">
                    <span className="text-ink-400">{c.label}</span>
                    <span className="text-ink-800">{c.render(row)}</span>
                  </div>
                ))}
                <div className="flex justify-between text-xs text-ink-400">
                  <span>تاریخ</span><span>{faDate(row.created_at)}</span>
                </div>
              </div>
            ))}
          </div>
        </Card>
      )}
    </div>
  );
}

export function VisibilityBadge({ visibility }: { visibility?: string }) {
  return <Badge tone={visibility === "public" ? "success" : "neutral"}>{visibility === "public" ? "عمومی" : "خصوصی"}</Badge>;
}
