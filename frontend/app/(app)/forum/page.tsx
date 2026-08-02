"use client";
import Link from "next/link";
import { CheckCircle2, Eye, MessageSquare } from "lucide-react";

import Badge from "@/components/ui/Badge";
import AddButton from "@/components/common/AddButton";
import Card from "@/components/ui/Card";
import { useList } from "@/hooks/useContent";
import { faNum, faDate } from "@/lib/format";
import type { ForumTopic } from "@/types";

export default function ForumPage() {
  const { data, isLoading } = useList<ForumTopic>("forum/topics");
  const topics = data?.data ?? [];
  return (
    <div>
      <div className="mb-4 flex items-center justify-between"><h1 className="text-lg font-bold text-ink-900">تالار گفتگو</h1><AddButton resource="forum/topics" label="موضوع جدید" fields={[{ name: "title", label: "عنوان موضوع", required: true },{ name: "body", label: "متن", type: "textarea" },{ name: "category", label: "دسته" }]} /></div>
      {isLoading && <Card className="p-8 text-center text-sm text-ink-400">در حال بارگذاری…</Card>}
      <Card className="divide-y divide-ink-200">
        {topics.map((t) => (
          <div key={t.id} className="flex items-center justify-between gap-3 p-4">
            <div className="min-w-0">
              <div className="flex items-center gap-2">
                <Link href={`/forum/${t.id}`} className="font-medium text-ink-900 hover:text-brand-700">{t.title}</Link>
                {t.solved && <Badge tone="success"><CheckCircle2 size={11} /> حل‌شده</Badge>}
              </div>
              <p className="mt-0.5 text-xs text-ink-400">{t.author?.name ?? "—"} · {faDate(t.created_at)}</p>
            </div>
            <div className="flex shrink-0 items-center gap-3 text-xs text-ink-400">
              <span className="flex items-center gap-1"><MessageSquare size={13} /> {faNum(t.reply_count)}</span>
              <span className="flex items-center gap-1"><Eye size={13} /> {faNum(t.views)}</span>
            </div>
          </div>
        ))}
        {!isLoading && topics.length === 0 && <div className="p-8 text-center text-sm text-ink-400">موضوعی ثبت نشده است.</div>}
      </Card>
    </div>
  );
}
