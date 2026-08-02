"use client";
import { useState } from "react";

import Button from "@/components/ui/Button";
import Input from "@/components/ui/Input";
import { useCreate, useUpdate } from "@/hooks/useContent";

export interface Field {
  name: string;
  label: string;
  type?: "text" | "textarea" | "number" | "select" | "datetime" | "file";
  options?: { value: string; label: string }[];
  required?: boolean;
  placeholder?: string;
  default?: string | number;
}

interface Props {
  resource: string;
  fields: Field[];
  onDone: () => void;
  /** Transform the raw form values before submit (e.g. split tags). */
  transform?: (values: Record<string, unknown>) => Record<string, unknown>;
  /** When set, the form edits (PATCH) that record instead of creating. */
  editId?: string;
  initialValues?: Record<string, unknown>;
}

/** Config-driven create/edit form: renders fields, POST/PATCHes, closes on success. */
export default function CreateForm({ resource, fields, onDone, transform, editId, initialValues }: Props) {
  const create = useCreate(resource);
  const update = useUpdate(resource);
  const pending = create.isPending || update.isPending;

  const [values, setValues] = useState<Record<string, unknown>>(
    initialValues ?? Object.fromEntries(fields.map((f) => [f.name, f.default ?? ""])),
  );
  const [error, setError] = useState<string | null>(null);

  const set = (name: string, v: unknown) => setValues((p) => ({ ...p, [name]: v }));

  const submit = () => {
    for (const f of fields) {
      if (f.required && !String(values[f.name] ?? "").trim()) {
        setError(`«${f.label}» الزامی است.`);
        return;
      }
    }
    const raw = transform ? transform(values) : values;
    const onError = () => setError("ثبت ناموفق بود (احتمالاً دسترسی لازم را ندارید).");
    const hasFile = Object.values(raw).some((v) => typeof File !== "undefined" && v instanceof File);
    let payload: Record<string, unknown> | FormData = raw;
    if (hasFile) {
      const fd = new FormData();
      Object.entries(raw).forEach(([k, v]) => {
        if (v instanceof File) fd.append(k, v);
        else if (Array.isArray(v)) v.forEach((x) => fd.append(k, String(x)));
        else if (v !== "" && v != null) fd.append(k, String(v));
      });
      payload = fd;
    }
    if (editId) update.mutate({ id: editId, payload: payload as never }, { onSuccess: onDone, onError });
    else create.mutate(payload as never, { onSuccess: onDone, onError });
  };

  return (
    <div className="space-y-3">
      {fields.map((f) => (
        <label key={f.name} className="block text-sm">
          <span className="mb-1 block text-ink-600">{f.label}</span>
          {f.type === "textarea" ? (
            <textarea
              className="w-full rounded-lg border border-ink-200 bg-[var(--surface)] px-3 py-2 text-sm text-ink-900 focus:border-brand-500 focus:outline-none focus:ring-2 focus:ring-brand-500/20"
              rows={3} value={String(values[f.name] ?? "")} placeholder={f.placeholder}
              onChange={(e) => set(f.name, e.target.value)}
            />
          ) : f.type === "select" ? (
            <select
              className="w-full rounded-lg border border-ink-200 bg-[var(--surface)] px-3 py-2 text-sm text-ink-900 focus:border-brand-500 focus:outline-none"
              value={String(values[f.name] ?? "")} onChange={(e) => set(f.name, e.target.value)}
            >
              {f.options?.map((o) => <option key={o.value} value={o.value}>{o.label}</option>)}
            </select>
          ) : f.type === "file" ? (
            <input type="file" className="w-full text-sm text-ink-700 file:mr-3 file:rounded-lg file:border-0 file:bg-brand-50 file:px-3 file:py-1.5 file:text-brand-700"
              onChange={(e) => set(f.name, e.target.files?.[0] ?? "")} />
          ) : (
            <Input
              type={f.type === "number" ? "number" : f.type === "datetime" ? "datetime-local" : "text"}
              value={String(values[f.name] ?? "")} placeholder={f.placeholder}
              onChange={(e) => set(f.name, f.type === "number" ? Number(e.target.value) : e.target.value)}
            />
          )}
        </label>
      ))}
      {error && <p className="text-xs text-red-600">{error}</p>}
      <div className="flex items-center gap-2 pt-1">
        <Button onClick={submit} loading={pending} className="flex-1 justify-center">{editId ? "ذخیره" : "ثبت"}</Button>
        <Button variant="secondary" onClick={onDone}>انصراف</Button>
      </div>
    </div>
  );
}
