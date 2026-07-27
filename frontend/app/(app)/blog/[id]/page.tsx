"use client";
import { useParams } from "next/navigation";

import DetailView from "@/components/content/DetailView";
import Badge from "@/components/ui/Badge";
import { VisibilityBadge } from "@/components/content/ContentList";
import { faNum } from "@/lib/format";
import type { BlogPost } from "@/types";

export default function BlogDetail() {
  const { id } = useParams<{ id: string }>();
  return (
    <DetailView<BlogPost> resource="blogs" id={id} backHref="/blog" backLabel="بازگشت به بلاگ" render={(b) => (
      <>
        <div className="mb-3 flex flex-wrap items-center gap-2">
          <h1 className="text-xl font-bold text-ink-900">{b.title}</h1>
          <VisibilityBadge visibility={b.visibility} />
        </div>
        {b.excerpt && <p className="mb-4 text-sm text-ink-500">{b.excerpt}</p>}
        {b.body && <p className="whitespace-pre-wrap leading-8 text-ink-800">{b.body}</p>}
        <div className="mt-4 flex flex-wrap items-center gap-2">
          {b.tags?.map((t) => <Badge key={t} tone="neutral">#{t}</Badge>)}
        </div>
        <p className="mt-3 text-xs text-ink-400">نویسنده: {b.author?.name ?? "—"} · امتیاز {faNum(b.rating)}</p>
      </>
    )} />
  );
}
