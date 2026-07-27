"use client";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { Users, Lock, Globe } from "lucide-react";

import Badge from "@/components/ui/Badge";
import Button from "@/components/ui/Button";
import AddButton from "@/components/common/AddButton";
import Card from "@/components/ui/Card";
import { useList } from "@/hooks/useContent";
import { api } from "@/lib/api";
import { faNum } from "@/lib/format";
import type { Group } from "@/types";

export default function GroupsPage() {
  const { data, isLoading } = useList<Group>("groups");
  const qc = useQueryClient();
  const toggle = useMutation({
    mutationFn: async (g: Group) => api.post(`/groups/${g.id}/${g.is_member ? "leave" : "join"}`),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["groups"] }),
  });
  const groups = data?.data ?? [];

  return (
    <div>
      <div className="mb-4 flex items-center justify-between"><h1 className="text-lg font-bold text-ink-900">گروه‌ها</h1><AddButton resource="groups" label="گروه جدید" fields={[{ name: "name", label: "نام گروه", required: true },{ name: "description", label: "توضیح", type: "textarea" },{ name: "privacy", label: "حریم", type: "select", default: "public", options: [{ value: "public", label: "عمومی" }, { value: "private", label: "خصوصی" }] },{ name: "category", label: "دسته" }]} /></div>
      {isLoading && <Card className="p-8 text-center text-sm text-ink-400">در حال بارگذاری…</Card>}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {groups.map((g) => (
          <Card key={g.id} className="p-4">
            <div className="mb-2 flex items-center justify-between">
              <span className="h-9 w-9 rounded-lg" style={{ backgroundColor: g.color }} />
              <Badge tone={g.privacy === "public" ? "success" : "neutral"}>
                {g.privacy === "public" ? <Globe size={11} /> : <Lock size={11} />}
                {g.privacy === "public" ? "عمومی" : "خصوصی"}
              </Badge>
            </div>
            <h3 className="font-semibold text-ink-900">{g.name}</h3>
            <p className="mt-1 line-clamp-2 text-xs text-ink-400">{g.description || "بدون توضیح"}</p>
            <div className="mt-3 flex items-center justify-between">
              <span className="flex items-center gap-1 text-xs text-ink-400"><Users size={13} /> {faNum(g.member_count)} عضو</span>
              <Button size="sm" variant={g.is_member ? "secondary" : "primary"} loading={toggle.isPending} onClick={() => toggle.mutate(g)}>
                {g.is_member ? "خروج" : "عضویت"}
              </Button>
            </div>
          </Card>
        ))}
      </div>
      {!isLoading && groups.length === 0 && <Card className="p-8 text-center text-sm text-ink-400">گروهی برای نمایش نیست.</Card>}
    </div>
  );
}
