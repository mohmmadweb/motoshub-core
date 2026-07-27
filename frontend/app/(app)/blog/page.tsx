"use client";
import ContentList, { VisibilityBadge, type Column } from "@/components/content/ContentList";
import type { BlogPost } from "@/types";

const columns: Column<BlogPost>[] = [
  { key: "title", label: "عنوان", render: (r) => <span className="font-medium text-ink-900">{r.title}</span> },
  { key: "author", label: "نویسنده", render: (r) => r.author?.name ?? "—" },
  { key: "rating", label: "امتیاز", render: (r) => Number(r.rating).toLocaleString("fa-IR") },
  { key: "visibility", label: "دسترسی", render: (r) => <VisibilityBadge visibility={r.visibility} /> },
];

export default function BlogPage() {
  return <ContentList<BlogPost> resource="blogs" title="بلاگ" columns={columns} />;
}
