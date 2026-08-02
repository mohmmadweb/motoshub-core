"use client";
import ContentList, { type Column } from "@/components/content/ContentList";
import Badge from "@/components/ui/Badge";
import type { UserRow } from "@/types";

const columns: Column<UserRow>[] = [
  { key: "name", label: "نام", render: (u) => <span className="font-medium text-ink-900">{u.name}</span> },
  { key: "username", label: "نام کاربری", render: (u) => <span className="text-ink-500">{u.username}</span> },
  { key: "title", label: "سمت", render: (u) => u.title || "—" },
  { key: "roles", label: "نقش‌ها", render: (u) => <Badge tone="neutral">{u.role_ids.length.toLocaleString("fa-IR")}</Badge> },
  { key: "active", label: "وضعیت", render: (u) => <Badge tone={u.is_active ? "success" : "neutral"}>{u.is_active ? "فعال" : "غیرفعال"}</Badge> },
];
const createFields = [
  { name: "name", label: "نام", required: true },
  { name: "username", label: "نام کاربری", required: true },
  { name: "title", label: "سمت" },
  { name: "email", label: "ایمیل" },
  { name: "password", label: "گذرواژه", type: "text" as const, placeholder: "حداقل ۸ کاراکتر" },
];

// UserRow uses date_joined, not created_at — map it so ContentList's date column works.
type Row = UserRow & { created_at: string };

export default function UsersAdminPage() {
  return <ContentList<Row> resource="users" title="مدیریت کاربران" columns={columns as Column<Row>[]}
    createFields={createFields} createLabel="کاربر جدید" editable deletable />;
}
