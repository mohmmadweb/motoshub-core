"use client";
import ContentList, { VisibilityBadge, type Column } from "@/components/content/ContentList";
import Badge from "@/components/ui/Badge";
import type { News } from "@/types";

const columns: Column<News>[] = [
  { key: "title", label: "عنوان", render: (r) => <span className="font-medium text-ink-900">{r.title}{r.pinned && " 📌"}</span> },
  { key: "views", label: "بازدید", render: (r) => r.views.toLocaleString("fa-IR") },
  { key: "scope", label: "دامنه", render: (r) => <Badge tone="navy">{r.scope === "global" ? "سراسری" : r.scope === "holding" ? "هلدینگ" : "شرکت"}</Badge> },
  { key: "visibility", label: "دسترسی", render: (r) => <VisibilityBadge visibility={r.visibility} /> },
];

const createFields = [
  { name: "title", label: "عنوان", required: true },
  { name: "summary", label: "خلاصه", type: "textarea" as const },
  { name: "visibility", label: "دسترسی", type: "select" as const, default: "private", options: [{ value: "private", label: "خصوصی" }, { value: "public", label: "عمومی" }] },
  { name: "scope", label: "دامنه", type: "select" as const, default: "global", options: [{ value: "global", label: "سراسری" }, { value: "holding", label: "هلدینگ" }, { value: "company", label: "شرکت" }] },
];

export default function NewsPage() {
  return <ContentList<News> resource="news" title="اخبار" columns={columns} createFields={createFields} createLabel="خبر جدید" />;
}
