"use client";
import ContentList, { VisibilityBadge, type Column } from "@/components/content/ContentList";
import Badge from "@/components/ui/Badge";
import type { EventItem } from "@/types";

const columns: Column<EventItem>[] = [
  { key: "title", label: "عنوان", render: (r) => <span className="font-medium text-ink-900">{r.title}</span> },
  { key: "location", label: "مکان", render: (r) => r.location || "—" },
  { key: "mode", label: "حالت", render: (r) => <Badge tone={r.mode === "online" ? "brand" : "navy"}>{r.mode === "online" ? "آنلاین" : "حضوری"}</Badge> },
  { key: "visibility", label: "دسترسی", render: (r) => <VisibilityBadge visibility={r.visibility} /> },
];

export default function EventsPage() {
  return <ContentList<EventItem> resource="events" title="رویدادها" columns={columns} />;
}
