"use client";
import { useMutation, useQueryClient } from "@tanstack/react-query";

import Button from "@/components/ui/Button";
import Card from "@/components/ui/Card";
import { useList } from "@/hooks/useContent";
import { api } from "@/lib/api";
import { faDateTime } from "@/lib/format";
import type { Notification } from "@/types";

export default function NotificationsPage() {
  const { data, isLoading } = useList<Notification>("notifications");
  const qc = useQueryClient();
  const readAll = useMutation({
    mutationFn: () => api.post("/notifications/read_all"),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["notifications"] }),
  });
  const rows = data?.data ?? [];
  return (
    <div>
      <div className="mb-4 flex items-center justify-between">
        <h1 className="text-lg font-bold text-ink-900">اعلان‌ها</h1>
        <Button size="sm" variant="secondary" onClick={() => readAll.mutate()} loading={readAll.isPending}>خواندن همه</Button>
      </div>
      {isLoading && <Card className="p-8 text-center text-sm text-ink-400">در حال بارگذاری…</Card>}
      <Card className="divide-y divide-ink-200">
        {rows.map((n) => (
          <div key={n.id} className={`flex items-start gap-3 p-4 ${n.read ? "" : "bg-brand-50/40"}`}>
            <span className={`mt-1.5 h-2 w-2 shrink-0 rounded-full ${n.read ? "bg-ink-300" : "bg-brand-500"}`} />
            <div>
              <p className="text-sm text-ink-800">{n.text}</p>
              <p className="mt-0.5 text-xs text-ink-400">{faDateTime(n.created_at)}</p>
            </div>
          </div>
        ))}
        {!isLoading && rows.length === 0 && <div className="p-8 text-center text-sm text-ink-400">اعلانی ندارید.</div>}
      </Card>
    </div>
  );
}
