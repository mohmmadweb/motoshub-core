"use client";
import Link from "next/link";

import Badge from "@/components/ui/Badge";
import AddButton from "@/components/common/AddButton";
import Card from "@/components/ui/Card";
import { useList } from "@/hooks/useContent";
import { faNum } from "@/lib/format";
import type { Project } from "@/types";

const health: Record<string, { tone: "success" | "warning" | "neutral"; label: string }> = {
  green: { tone: "success", label: "سالم" },
  yellow: { tone: "warning", label: "نیازمند توجه" },
  red: { tone: "neutral", label: "در خطر" },
};

export default function ProjectsPage() {
  const { data, isLoading } = useList<Project>("projects");
  const projects = data?.data ?? [];
  return (
    <div>
      <div className="mb-4 flex items-center justify-between">
        <h1 className="text-lg font-bold text-ink-900">پروژه‌ها</h1>
        <AddButton resource="projects" label="پروژه جدید" fields={[
          { name: "name", label: "نام پروژه", required: true },
          { name: "client", label: "کارفرما" },
          { name: "health", label: "سلامت", type: "select", default: "green", options: [
            { value: "green", label: "سالم" }, { value: "yellow", label: "نیازمند توجه" }, { value: "red", label: "در خطر" }] },
          { name: "progress", label: "پیشرفت (٪)", type: "number", default: 0 },
        ]} />
      </div>
      {isLoading && <Card className="p-8 text-center text-sm text-ink-400">در حال بارگذاری…</Card>}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {projects.map((p) => (
          <Link key={p.id} href={`/projects/${p.id}`}>
            <Card className="p-4 transition-shadow hover:shadow-md">
              <div className="mb-2 flex items-center justify-between">
                <h3 className="font-semibold text-ink-900">{p.name}</h3>
                <Badge tone={health[p.health]?.tone}>{health[p.health]?.label}</Badge>
              </div>
              <p className="text-xs text-ink-400">{p.client || "—"}</p>
              <div className="mt-3">
                <div className="mb-1 flex justify-between text-[11px] text-ink-400">
                  <span>پیشرفت</span><span>{faNum(p.progress)}٪</span>
                </div>
                <div className="h-1.5 overflow-hidden rounded-full bg-ink-100">
                  <div className="h-full rounded-full bg-brand-500" style={{ width: `${p.progress}%` }} />
                </div>
              </div>
              <p className="mt-3 text-xs text-ink-400">{faNum(p.task_count)} کار</p>
            </Card>
          </Link>
        ))}
      </div>
      {!isLoading && projects.length === 0 && <Card className="p-8 text-center text-sm text-ink-400">پروژه‌ای ثبت نشده است.</Card>}
    </div>
  );
}
