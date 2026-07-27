"use client";
import { useParams } from "next/navigation";

import Badge from "@/components/ui/Badge";
import Card from "@/components/ui/Card";
import { useList } from "@/hooks/useContent";
import type { Task } from "@/types";

const columns: { key: Task["status"]; label: string }[] = [
  { key: "planning", label: "برنامه‌ریزی" },
  { key: "in_progress", label: "در حال انجام" },
  { key: "review", label: "بازبینی" },
  { key: "done", label: "انجام‌شده" },
];
const prio: Record<string, { tone: "neutral" | "warning" | "success"; label: string }> = {
  low: { tone: "neutral", label: "کم" },
  medium: { tone: "warning", label: "متوسط" },
  high: { tone: "success", label: "زیاد" },
};

export default function ProjectBoardPage() {
  const { id } = useParams<{ id: string }>();
  const { data, isLoading } = useList<Task>("tasks", { project: id });
  const tasks = data?.data ?? [];

  return (
    <div>
      <h1 className="mb-4 text-lg font-bold text-ink-900">تختهٔ کارها</h1>
      {isLoading && <Card className="p-8 text-center text-sm text-ink-400">در حال بارگذاری…</Card>}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {columns.map((col) => {
          const items = tasks.filter((t) => t.status === col.key);
          return (
            <div key={col.key} className="rounded-xl bg-ink-100 p-3">
              <div className="mb-3 flex items-center justify-between px-1">
                <span className="text-sm font-semibold text-ink-700">{col.label}</span>
                <span className="text-xs text-ink-400">{items.length.toLocaleString("fa-IR")}</span>
              </div>
              <div className="space-y-2">
                {items.map((t) => (
                  <Card key={t.id} className="p-3">
                    <p className="text-sm text-ink-900">{t.title}</p>
                    <div className="mt-2 flex items-center justify-between">
                      <Badge tone={prio[t.priority]?.tone}>{prio[t.priority]?.label}</Badge>
                      <span className="text-[11px] text-ink-400">{t.assignee?.name ?? "—"}</span>
                    </div>
                  </Card>
                ))}
                {items.length === 0 && <p className="px-1 py-4 text-center text-xs text-ink-400">—</p>}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
