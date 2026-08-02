"use client";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { ArrowRight, CheckCircle2, Send } from "lucide-react";
import Link from "next/link";
import { useParams } from "next/navigation";
import { useState } from "react";

import Badge from "@/components/ui/Badge";
import Button from "@/components/ui/Button";
import Card from "@/components/ui/Card";
import Input from "@/components/ui/Input";
import { api, type Envelope } from "@/lib/api";
import { faDateTime } from "@/lib/format";
import type { ForumReply, ForumTopic } from "@/types";

export default function ForumTopicPage() {
  const { id } = useParams<{ id: string }>();
  const qc = useQueryClient();
  const [body, setBody] = useState("");

  const topic = useQuery({
    queryKey: ["forum/topics", id],
    queryFn: async () => (await api.get<Envelope<ForumTopic>>(`/forum/topics/${id}`)).data.data,
  });
  const replies = useQuery({
    queryKey: ["forum/topics", id, "replies"],
    queryFn: async () => (await api.get<Envelope<ForumReply[]>>(`/forum/topics/${id}/replies`)).data.data,
  });
  const reply = useMutation({
    mutationFn: () => api.post(`/forum/topics/${id}/replies`, { body }),
    onSuccess: () => { setBody(""); qc.invalidateQueries({ queryKey: ["forum/topics", id, "replies"] }); },
  });
  const solve = useMutation({
    mutationFn: () => api.post(`/forum/topics/${id}/solve`),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["forum/topics", id] }),
  });

  const t = topic.data;
  return (
    <div>
      <Link href="/forum" className="mb-4 inline-flex items-center gap-1 text-sm text-ink-500 hover:text-brand-600">
        <ArrowRight size={16} /> بازگشت به تالار
      </Link>
      {t && (
        <Card className="mb-4 p-5">
          <div className="mb-2 flex items-center gap-2">
            <h1 className="text-xl font-bold text-ink-900">{t.title}</h1>
            {t.solved ? <Badge tone="success"><CheckCircle2 size={11} /> حل‌شده</Badge>
                      : <Button size="sm" variant="secondary" onClick={() => solve.mutate()} loading={solve.isPending}>علامت حل‌شده</Button>}
          </div>
          <p className="text-xs text-ink-400">{t.author?.name ?? "—"} · {faDateTime(t.created_at)}</p>
          {t.body && <p className="mt-3 whitespace-pre-wrap leading-8 text-ink-800">{t.body}</p>}
        </Card>
      )}

      <div className="space-y-2">
        {(replies.data ?? []).map((r) => (
          <Card key={r.id} className={`p-4 ${r.is_solution ? "border-emerald-300" : ""}`}>
            <p className="text-xs text-ink-400">{r.author?.name ?? "—"} · {faDateTime(r.created_at)} {r.is_solution && "· پاسخ برگزیده"}</p>
            <p className="mt-1 whitespace-pre-wrap text-sm text-ink-800">{r.body}</p>
          </Card>
        ))}
      </div>

      <div className="mt-4 flex items-center gap-2">
        <Input value={body} onChange={(e) => setBody(e.target.value)} placeholder="پاسخ خود را بنویسید…"
          onKeyDown={(e) => e.key === "Enter" && body.trim() && reply.mutate()} />
        <Button icon={<Send size={16} />} onClick={() => reply.mutate()} loading={reply.isPending} disabled={!body.trim()}>ارسال</Button>
      </div>
    </div>
  );
}
