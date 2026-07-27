"use client";
import { useMutation, useQueryClient } from "@tanstack/react-query";

import AddButton from "@/components/common/AddButton";
import Card from "@/components/ui/Card";
import { useList } from "@/hooks/useContent";
import { api } from "@/lib/api";
import { faNum } from "@/lib/format";
import type { Poll } from "@/types";

export default function PollsPage() {
  const { data, isLoading } = useList<Poll>("polls");
  const qc = useQueryClient();
  const vote = useMutation({
    mutationFn: (p: { pollId: string; optionId: string }) => api.post(`/polls/${p.pollId}/vote`, { option_id: p.optionId }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["polls"] }),
  });
  const polls = data?.data ?? [];
  return (
    <div>
      <div className="mb-4 flex items-center justify-between"><h1 className="text-lg font-bold text-ink-900">نظرسنجی‌ها</h1><AddButton resource="polls" label="نظرسنجی جدید" transform={(v) => ({ ...v, option_labels: String(v.option_labels || "").split(",").map((x) => x.trim()).filter(Boolean) })} fields={[{ name: "question", label: "پرسش", required: true },{ name: "option_labels", label: "گزینه‌ها (با کاما)", placeholder: "بله, خیر, نظری ندارم" }]} /></div>
      {isLoading && <Card className="p-8 text-center text-sm text-ink-400">در حال بارگذاری…</Card>}
      <div className="space-y-4">
        {polls.map((p) => {
          const total = p.options.reduce((s, o) => s + o.votes, 0) || 1;
          return (
            <Card key={p.id} className="p-4">
              <h3 className="mb-3 font-semibold text-ink-900">{p.question}</h3>
              <div className="space-y-2">
                {p.options.map((o) => {
                  const pct = Math.round((o.votes / total) * 100);
                  const mine = p.my_vote === o.id;
                  return (
                    <button key={o.id} onClick={() => vote.mutate({ pollId: p.id, optionId: o.id })}
                      className="relative w-full overflow-hidden rounded-lg border border-ink-200 p-2 text-right text-sm">
                      <span className="absolute inset-y-0 right-0 bg-brand-50" style={{ width: `${pct}%` }} />
                      <span className="relative flex justify-between">
                        <span className={mine ? "font-bold text-brand-700" : "text-ink-800"}>{o.label}{mine && " ✓"}</span>
                        <span className="text-ink-400">{faNum(pct)}٪ ({faNum(o.votes)})</span>
                      </span>
                    </button>
                  );
                })}
              </div>
            </Card>
          );
        })}
      </div>
      {!isLoading && polls.length === 0 && <Card className="p-8 text-center text-sm text-ink-400">نظرسنجی‌ای موجود نیست.</Card>}
    </div>
  );
}
