"use client";
import { useParams } from "next/navigation";

import DetailView from "@/components/content/DetailView";
import Badge from "@/components/ui/Badge";
import { VisibilityBadge } from "@/components/content/ContentList";
import { faNum } from "@/lib/format";
import type { News } from "@/types";

const scopeLabel: Record<string, string> = { global: "سراسری", holding: "هلدینگ", company: "شرکت" };

export default function NewsDetail() {
  const { id } = useParams<{ id: string }>();
  return (
    <DetailView<News> resource="news" id={id} backHref="/news" backLabel="بازگشت به اخبار" render={(n) => (
      <>
        <div className="mb-3 flex flex-wrap items-center gap-2">
          <h1 className="text-xl font-bold text-ink-900">{n.title}{n.pinned && " 📌"}</h1>
          <VisibilityBadge visibility={n.visibility} />
          <Badge tone="navy">{scopeLabel[n.scope] ?? n.scope}</Badge>
        </div>
        {n.summary && <p className="mb-4 text-sm text-ink-500">{n.summary}</p>}
        {n.body && <p className="whitespace-pre-wrap leading-8 text-ink-800">{n.body}</p>}
        <p className="mt-4 text-xs text-ink-400">نویسنده: {n.author?.name ?? "—"} · {faNum(n.views)} بازدید</p>
      </>
    )} />
  );
}
