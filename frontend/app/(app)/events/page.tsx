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

const createFields = [
  { name: "title", label: "عنوان", required: true },
  { name: "starts_at", label: "زمان برگزاری", type: "datetime" as const, required: true },
  { name: "location", label: "مکان" },
  { name: "mode", label: "حالت", type: "select" as const, default: "in_person", options: [{ value: "in_person", label: "حضوری" }, { value: "online", label: "آنلاین" }] },
  { name: "visibility", label: "دسترسی", type: "select" as const, default: "private", options: [{ value: "private", label: "خصوصی" }, { value: "public", label: "عمومی" }] },
];

export default function EventsPage() {
  return <ContentList<EventItem> resource="events" title="رویدادها" columns={columns} createFields={createFields} createLabel="رویداد جدید" deletable editable />;
}
