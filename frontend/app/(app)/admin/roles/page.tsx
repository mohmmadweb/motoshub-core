"use client";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Plus, Trash2 } from "lucide-react";
import { useState } from "react";

import Badge from "@/components/ui/Badge";
import Button from "@/components/ui/Button";
import Card from "@/components/ui/Card";
import Input from "@/components/ui/Input";
import Modal from "@/components/ui/Modal";
import { api, type Envelope } from "@/lib/api";
import type { PermGroup, Role } from "@/types";

const scopeLabel: Record<string, string> = { platform: "پلتفرم", tenant: "سازمان", group: "گروه" };

export default function RolesAdminPage() {
  const qc = useQueryClient();
  const [open, setOpen] = useState(false);
  const [title, setTitle] = useState("");
  const [perms, setPerms] = useState<Set<string>>(new Set());

  const roles = useQuery({ queryKey: ["roles"], queryFn: async () => (await api.get<Envelope<Role[]>>("/roles")).data.data });
  const catalog = useQuery({ queryKey: ["permissions/catalog"], queryFn: async () => (await api.get<Envelope<PermGroup[]>>("/permissions/catalog")).data.data });

  const create = useMutation({
    mutationFn: () => api.post("/roles", { title, scope: "tenant", permissions: [...perms] }),
    onSuccess: () => { setOpen(false); setTitle(""); setPerms(new Set()); qc.invalidateQueries({ queryKey: ["roles"] }); },
  });
  const remove = useMutation({
    mutationFn: (id: string) => api.delete(`/roles/${id}`),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["roles"] }),
  });

  const toggle = (id: string) => setPerms((p) => { const n = new Set(p); n.has(id) ? n.delete(id) : n.add(id); return n; });

  return (
    <div>
      <div className="mb-4 flex items-center justify-between">
        <h1 className="text-lg font-bold text-ink-900">نقش‌ها و دسترسی‌ها</h1>
        <Button size="sm" icon={<Plus size={15} />} onClick={() => setOpen(true)}>نقش سفارشی</Button>
      </div>

      <Card className="divide-y divide-ink-200">
        {(roles.data ?? []).map((r) => (
          <div key={r.id} className="flex items-center justify-between p-4">
            <div>
              <div className="flex items-center gap-2">
                <span className="font-medium text-ink-900">{r.title}</span>
                <Badge tone={r.is_system ? "navy" : "brand"}>{scopeLabel[r.scope] ?? r.scope}</Badge>
                {r.is_system && <Badge tone="neutral">سیستمی</Badge>}
              </div>
              <p className="mt-0.5 text-xs text-ink-400">{r.permissions.length.toLocaleString("fa-IR")} مجوز · {r.member_count.toLocaleString("fa-IR")} کاربر</p>
            </div>
            {!r.is_system && (
              <button onClick={() => confirm("حذف این نقش؟") && remove.mutate(r.id)} className="rounded p-1 text-ink-400 hover:bg-red-50 hover:text-red-600" aria-label="حذف">
                <Trash2 size={15} />
              </button>
            )}
          </div>
        ))}
      </Card>

      <Modal open={open} onClose={() => setOpen(false)} title="نقش سفارشی جدید">
        <div className="space-y-3">
          <Input placeholder="عنوان نقش" value={title} onChange={(e) => setTitle(e.target.value)} />
          <div className="max-h-72 space-y-3 overflow-y-auto rounded-lg border border-ink-200 p-3">
            {(catalog.data ?? []).map((g) => (
              <div key={g.group}>
                <p className="mb-1 text-xs font-bold text-ink-600">{g.label}</p>
                <div className="flex flex-wrap gap-2">
                  {g.permissions.map((p) => (
                    <label key={p.id} className={`cursor-pointer rounded-md border px-2 py-1 text-[11px] ${perms.has(p.id) ? "border-brand-400 bg-brand-50 text-brand-700" : "border-ink-200 text-ink-500"}`}>
                      <input type="checkbox" className="hidden" checked={perms.has(p.id)} onChange={() => toggle(p.id)} />
                      {p.action}
                    </label>
                  ))}
                </div>
              </div>
            ))}
          </div>
          <div className="flex items-center gap-2">
            <Button className="flex-1 justify-center" loading={create.isPending} disabled={!title.trim()} onClick={() => create.mutate()}>ثبت نقش ({perms.size.toLocaleString("fa-IR")} مجوز)</Button>
            <Button variant="secondary" onClick={() => setOpen(false)}>انصراف</Button>
          </div>
        </div>
      </Modal>
    </div>
  );
}
