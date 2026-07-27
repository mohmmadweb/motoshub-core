"use client";
import { CalendarDays, MapPin } from "lucide-react";
import { useParams } from "next/navigation";

import DetailView from "@/components/content/DetailView";
import Badge from "@/components/ui/Badge";
import { VisibilityBadge } from "@/components/content/ContentList";
import { faDateTime, faNum } from "@/lib/format";
import type { EventItem } from "@/types";

export default function EventDetail() {
  const { id } = useParams<{ id: string }>();
  return (
    <DetailView<EventItem> resource="events" id={id} backHref="/events" backLabel="بازگشت به رویدادها" render={(e) => (
      <>
        <div className="mb-3 flex flex-wrap items-center gap-2">
          <h1 className="text-xl font-bold text-ink-900">{e.title}</h1>
          <Badge tone={e.mode === "online" ? "brand" : "navy"}>{e.mode === "online" ? "آنلاین" : "حضوری"}</Badge>
          <VisibilityBadge visibility={e.visibility} />
        </div>
        <div className="mb-4 flex flex-wrap gap-4 text-sm text-ink-500">
          <span className="flex items-center gap-1"><CalendarDays size={15} /> {faDateTime(e.starts_at)}</span>
          {e.location && <span className="flex items-center gap-1"><MapPin size={15} /> {e.location}</span>}
        </div>
        {e.description && <p className="whitespace-pre-wrap leading-8 text-ink-800">{e.description}</p>}
        <p className="mt-4 text-xs text-ink-400">{faNum(e.attendees)} شرکت‌کننده</p>
      </>
    )} />
  );
}
