"use client";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { ArrowRight, Send } from "lucide-react";
import Link from "next/link";
import { useParams } from "next/navigation";
import { useState } from "react";

import Badge from "@/components/ui/Badge";
import Button from "@/components/ui/Button";
import Card from "@/components/ui/Card";
import Input from "@/components/ui/Input";
import { api, type Envelope } from "@/lib/api";
import { faDateTime } from "@/lib/format";
import type { TicketDetail } from "@/types";

const st: Record<string, string> = { open: "باز", in_review: "در حال بررسی", answered: "پاسخ داده شد", closed: "بسته" };

export default function TicketPage() {
  const { id } = useParams<{ id: string }>();
  const qc = useQueryClient();
  const [body, setBody] = useState("");
  const { data: t } = useQuery({
    queryKey: ["tickets", id],
    queryFn: async () => (await api.get<Envelope<TicketDetail>>(`/tickets/${id}`)).data.data,
  });
  const reply = useMutation({
    mutationFn: () => api.post(`/tickets/${id}/reply`, { body }),
    onSuccess: () => { setBody(""); qc.invalidateQueries({ queryKey: ["tickets", id] }); },
  });
  const close = useMutation({
    mutationFn: () => api.post(`/tickets/${id}/close`),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["tickets", id] }),
  });

  return (
    <div>
      <Link href="/tickets" className="mb-4 inline-flex items-center gap-1 text-sm text-ink-500 hover:text-brand-600">
        <ArrowRight size={16} /> بازگشت به تیکت‌ها
      </Link>
      {t && (
        <>
          <Card className="mb-4 p-5">
            <div className="flex items-center gap-2">
              <h1 className="text-xl font-bold text-ink-900">{t.subject}</h1>
              <Badge tone="neutral">{st[t.status]}</Badge>
              {t.status !== "closed" && <Button size="sm" variant="secondary" onClick={() => close.mutate()} loading={close.isPending}>بستن تیکت</Button>}
            </div>
            <p className="mt-1 text-xs text-ink-400">{t.number} · {t.category}</p>
          </Card>
          <div className="space-y-2">
            {t.messages.map((m) => (
              <Card key={m.id} className={`p-4 ${m.from_support ? "border-brand-200 bg-brand-50/40" : ""}`}>
                <p className="text-xs text-ink-400">{m.from_support ? "پشتیبانی" : m.author?.name ?? "شما"} · {faDateTime(m.created_at)}</p>
                <p className="mt-1 whitespace-pre-wrap text-sm text-ink-800">{m.body}</p>
              </Card>
            ))}
          </div>
          {t.status !== "closed" && (
            <div className="mt-4 flex items-center gap-2">
              <Input value={body} onChange={(e) => setBody(e.target.value)} placeholder="پیام خود را بنویسید…"
                onKeyDown={(e) => e.key === "Enter" && body.trim() && reply.mutate()} />
              <Button icon={<Send size={16} />} onClick={() => reply.mutate()} loading={reply.isPending} disabled={!body.trim()}>ارسال</Button>
            </div>
          )}
        </>
      )}
    </div>
  );
}
