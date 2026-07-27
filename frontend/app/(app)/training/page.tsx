"use client";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { Clock, Users } from "lucide-react";

import Badge from "@/components/ui/Badge";
import Button from "@/components/ui/Button";
import Card from "@/components/ui/Card";
import { useList } from "@/hooks/useContent";
import { api } from "@/lib/api";
import { faNum } from "@/lib/format";
import type { TrainingCourse } from "@/types";

const status: Record<string, { tone: "success" | "brand" | "neutral"; label: string }> = {
  open: { tone: "success", label: "ثبت‌نام باز" }, running: { tone: "brand", label: "در حال برگزاری" }, done: { tone: "neutral", label: "برگزار شده" },
};

export default function TrainingPage() {
  const { data, isLoading } = useList<TrainingCourse>("training/courses");
  const qc = useQueryClient();
  const toggle = useMutation({
    mutationFn: (c: TrainingCourse) => api.post(`/training/courses/${c.id}/${c.is_enrolled ? "leave" : "enroll"}`),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["training/courses"] }),
  });
  const rows = data?.data ?? [];
  return (
    <div>
      <h1 className="mb-4 text-lg font-bold text-ink-900">آموزش</h1>
      {isLoading && <Card className="p-8 text-center text-sm text-ink-400">در حال بارگذاری…</Card>}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {rows.map((c) => (
          <Card key={c.id} className="p-4">
            <div className="mb-2 flex items-center justify-between">
              <h3 className="font-semibold text-ink-900">{c.title}</h3>
              <Badge tone={status[c.status]?.tone}>{status[c.status]?.label}</Badge>
            </div>
            <p className="text-xs text-ink-400">{c.instructor || "—"}</p>
            <div className="mt-3 flex items-center gap-3 text-xs text-ink-400">
              <span className="flex items-center gap-1"><Clock size={13} /> {faNum(c.hours)} ساعت</span>
              <span className="flex items-center gap-1"><Users size={13} /> {faNum(c.enrolled)}/{faNum(c.capacity)}</span>
            </div>
            <Button size="sm" className="mt-3 w-full" variant={c.is_enrolled ? "secondary" : "primary"} loading={toggle.isPending} onClick={() => toggle.mutate(c)}>
              {c.is_enrolled ? "لغو ثبت‌نام" : "ثبت‌نام"}
            </Button>
          </Card>
        ))}
      </div>
      {!isLoading && rows.length === 0 && <Card className="p-8 text-center text-sm text-ink-400">دوره‌ای موجود نیست.</Card>}
    </div>
  );
}
