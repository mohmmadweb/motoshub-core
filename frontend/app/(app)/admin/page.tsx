"use client";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useEffect, useState } from "react";

import Button from "@/components/ui/Button";
import Card from "@/components/ui/Card";
import Input from "@/components/ui/Input";
import { api, type Envelope } from "@/lib/api";
import type { WorkflowSettings } from "@/types";

const fields: { key: keyof WorkflowSettings; label: string; unit: string }[] = [
  { key: "report_reminder_days", label: "یادآوری گزارش پیش از موعد", unit: "روز" },
  { key: "review_escalation_days", label: "تشدید بررسی", unit: "روز" },
  { key: "dormant_project_days", label: "تشخیص طرح راکد", unit: "روز" },
  { key: "screening_threshold", label: "حد نصاب غربالگری", unit: "از ۲۰۰" },
  { key: "jury_threshold", label: "حد نصاب داوری", unit: "از ۱۰۰" },
  { key: "legal_review_days", label: "بررسی حقوقی قرارداد", unit: "روز کاری" },
  { key: "retention_percent", label: "حسن انجام کار", unit: "٪" },
  { key: "prepayment_percent", label: "سقف پیش‌پرداخت", unit: "٪" },
  { key: "rate_limit_per_minute", label: "محدودیت نرخ درخواست", unit: "در دقیقه" },
  { key: "edit_window_count", label: "دفعات مجاز ویرایش اثر", unit: "بار" },
];

export default function AdminPage() {
  const qc = useQueryClient();
  const { data } = useQuery({
    queryKey: ["settings/workflow"],
    queryFn: async () => (await api.get<Envelope<WorkflowSettings>>("/settings/workflow")).data.data,
  });
  const [form, setForm] = useState<Partial<WorkflowSettings>>({});
  useEffect(() => { if (data) setForm(data); }, [data]);

  const save = useMutation({
    mutationFn: (patch: Partial<WorkflowSettings>) => api.put("/settings/workflow", patch),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["settings/workflow"] }),
  });

  return (
    <div>
      <h1 className="mb-1 text-lg font-bold text-ink-900">پنل مدیریت</h1>
      <p className="mb-5 text-sm text-ink-500">پارامترهای گردش کار سازمان</p>
      <Card className="p-5">
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
          {fields.map((f) => (
            <label key={f.key} className="text-sm">
              <span className="mb-1 block text-ink-600">{f.label} <span className="text-xs text-ink-400">({f.unit})</span></span>
              <Input type="number" value={String(form[f.key] ?? "")}
                onChange={(e) => setForm((p) => ({ ...p, [f.key]: Number(e.target.value) }))} />
            </label>
          ))}
        </div>
        <div className="mt-5 flex items-center gap-3">
          <Button onClick={() => save.mutate(form)} loading={save.isPending}>ذخیره تغییرات</Button>
          {save.isSuccess && <span className="text-xs text-emerald-600">ذخیره شد ✓</span>}
          {save.isError && <span className="text-xs text-red-600">دسترسی لازم را ندارید.</span>}
        </div>
      </Card>
    </div>
  );
}
