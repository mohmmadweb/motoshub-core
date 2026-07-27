"use client";
import { Pencil, Plus, Search, Trash2 } from "lucide-react";
import { useState, type ReactNode } from "react";

import CreateForm, { type Field } from "@/components/common/CreateForm";
import Badge from "@/components/ui/Badge";
import Button from "@/components/ui/Button";
import Card from "@/components/ui/Card";
import Input from "@/components/ui/Input";
import Modal from "@/components/ui/Modal";
import { useList, useRemoveById } from "@/hooks/useContent";
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
  createFields?: Field[];
  createTransform?: (values: Record<string, unknown>) => Record<string, unknown>;
  createLabel?: string;
  deletable?: boolean;
  editable?: boolean;
  searchable?: boolean;
}

/** Generic tenant-scoped list: search, create, delete; desktop table + mobile cards. */
export default function ContentList<T extends { id: string; created_at: string; visibility?: string }>({
  resource, title, columns, createFields, createTransform, createLabel = "افزودن",
  deletable, editable, searchable = true,
}: Props<T>) {
  const [open, setOpen] = useState(false);
  const [editing, setEditing] = useState<T | null>(null);
  const [search, setSearch] = useState("");
  const { data, isLoading, isError } = useList<T>(resource, search ? { search } : undefined);
  const remove = useRemoveById(resource);
  const rows = data?.data ?? [];
  const canEdit = editable && !!createFields;
  const hasActions = deletable || canEdit;

  const onDelete = (id: string) => {
    if (window.confirm("آیا از حذف این مورد مطمئن هستید؟")) remove.mutate(id);
  };

  const initialFor = (row: T): Record<string, unknown> =>
    Object.fromEntries((createFields ?? []).map((f) => [f.name, (row as Record<string, unknown>)[f.name] ?? ""]));

  return (
    <div>
      <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
        <h1 className="text-lg font-bold text-ink-900">{title}</h1>
        <div className="flex items-center gap-3">
          {searchable && (
            <span className="relative">
              <Search size={15} className="pointer-events-none absolute right-3 top-1/2 -translate-y-1/2 text-ink-400" />
              <Input className="w-48 pr-9" placeholder="جستجو…" value={search} onChange={(e) => setSearch(e.target.value)} />
            </span>
          )}
          {data?.meta && <span className="text-xs text-ink-400">{data.meta.count.toLocaleString("fa-IR")} مورد</span>}
          {createFields && <Button size="sm" icon={<Plus size={15} />} onClick={() => setOpen(true)}>{createLabel}</Button>}
        </div>
      </div>

      {createFields && (
        <Modal open={open} onClose={() => setOpen(false)} title={createLabel}>
          <CreateForm resource={resource} fields={createFields} transform={createTransform} onDone={() => setOpen(false)} />
        </Modal>
      )}
      {canEdit && (
        <Modal open={!!editing} onClose={() => setEditing(null)} title="ویرایش">
          {editing && (
            <CreateForm resource={resource} fields={createFields!} transform={createTransform}
              editId={editing.id} initialValues={initialFor(editing)} onDone={() => setEditing(null)} />
          )}
        </Modal>
      )}

      {isLoading && <Card className="p-8 text-center text-sm text-ink-400">در حال بارگذاری…</Card>}
      {isError && <Card className="p-8 text-center text-sm text-red-600">خطا در دریافت داده.</Card>}
      {!isLoading && !isError && rows.length === 0 && (
        <Card className="p-8 text-center text-sm text-ink-400">موردی یافت نشد.</Card>
      )}

      {rows.length > 0 && (
        <Card className="overflow-hidden">
          <table className="hidden w-full text-right sm:table">
            <thead>
              <tr className="bg-ink-100 text-[11px] uppercase tracking-wide text-ink-400">
                {columns.map((c) => <th key={c.key} className="px-4 py-2 font-semibold">{c.label}</th>)}
                <th className="px-4 py-2 font-semibold">تاریخ</th>
                {hasActions && <th className="px-4 py-2" aria-label="عملیات" />}
              </tr>
            </thead>
            <tbody className="divide-y divide-ink-200">
              {rows.map((row) => (
                <tr key={row.id} className="text-sm text-ink-800">
                  {columns.map((c) => <td key={c.key} className="px-4 py-3">{c.render(row)}</td>)}
                  <td className="px-4 py-3 text-xs text-ink-400">{faDate(row.created_at)}</td>
                  {hasActions && (
                    <td className="px-4 py-3">
                      <span className="flex items-center gap-1">
                        {canEdit && (
                          <button onClick={() => setEditing(row)} className="rounded p-1 text-ink-400 hover:bg-brand-50 hover:text-brand-600" aria-label="ویرایش">
                            <Pencil size={15} />
                          </button>
                        )}
                        {deletable && (
                          <button onClick={() => onDelete(row.id)} className="rounded p-1 text-ink-400 hover:bg-red-50 hover:text-red-600" aria-label="حذف">
                            <Trash2 size={15} />
                          </button>
                        )}
                      </span>
                    </td>
                  )}
                </tr>
              ))}
            </tbody>
          </table>
          <div className="divide-y divide-ink-200 sm:hidden">
            {rows.map((row) => (
              <div key={row.id} className="space-y-2 p-4">
                {columns.map((c) => (
                  <div key={c.key} className="flex justify-between gap-3 text-sm">
                    <span className="text-ink-400">{c.label}</span>
                    <span className="text-ink-800">{c.render(row)}</span>
                  </div>
                ))}
                <div className="flex items-center justify-between text-xs text-ink-400">
                  <span>{faDate(row.created_at)}</span>
                  <span className="flex items-center gap-2">
                    {canEdit && <button onClick={() => setEditing(row)} className="text-brand-500" aria-label="ویرایش"><Pencil size={15} /></button>}
                    {deletable && <button onClick={() => onDelete(row.id)} className="text-red-500" aria-label="حذف"><Trash2 size={15} /></button>}
                  </span>
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
