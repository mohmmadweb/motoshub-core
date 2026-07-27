"use client";
import ContentList, { VisibilityBadge, type Column } from "@/components/content/ContentList";
import type { BlogPost } from "@/types";

const columns: Column<BlogPost>[] = [
  { key: "title", label: "عنوان", render: (r) => <span className="font-medium text-ink-900">{r.title}</span> },
  { key: "author", label: "نویسنده", render: (r) => r.author?.name ?? "—" },
  { key: "rating", label: "امتیاز", render: (r) => Number(r.rating).toLocaleString("fa-IR") },
  { key: "visibility", label: "دسترسی", render: (r) => <VisibilityBadge visibility={r.visibility} /> },
];

const createFields = [
  { name: "title", label: "عنوان", required: true },
  { name: "excerpt", label: "چکیده", type: "textarea" as const },
  { name: "tags", label: "برچسب‌ها (با کاما)", placeholder: "راهبردی, فناوری" },
  { name: "visibility", label: "دسترسی", type: "select" as const, default: "private", options: [{ value: "private", label: "خصوصی" }, { value: "public", label: "عمومی" }] },
];
const transform = (v: Record<string, unknown>) => ({ ...v, tags: String(v.tags || "").split(",").map((t) => t.trim()).filter(Boolean) });

export default function BlogPage() {
  return <ContentList<BlogPost> resource="blogs" title="بلاگ" columns={columns} createFields={createFields} createTransform={transform} createLabel="یادداشت جدید" deletable />;
}
