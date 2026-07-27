"use client";
import ContentList, { VisibilityBadge, type Column } from "@/components/content/ContentList";
import Badge from "@/components/ui/Badge";
import type { KnowledgeDoc } from "@/types";

const typeLabel: Record<string, string> = { contract: "قرارداد", training: "آموزشی", minutes: "صورت‌جلسه", report: "گزارش" };

const columns: Column<KnowledgeDoc>[] = [
  { key: "title", label: "عنوان", render: (r) => <span className="font-medium text-ink-900">{r.title}</span> },
  { key: "category", label: "دسته", render: (r) => r.category || "—" },
  { key: "doc_type", label: "نوع", render: (r) => <Badge tone="warning">{typeLabel[r.doc_type] ?? r.doc_type}</Badge> },
  { key: "visibility", label: "دسترسی", render: (r) => <VisibilityBadge visibility={r.visibility} /> },
];

export default function KnowledgePage() {
  return <ContentList<KnowledgeDoc> resource="knowledge" title="مدیریت دانش" columns={columns} />;
}
