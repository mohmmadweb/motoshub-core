"use client";
import { Newspaper, PenSquare, CalendarDays, BookOpen } from "lucide-react";

import Card from "@/components/ui/Card";
import { useList } from "@/hooks/useContent";
import { useAuthStore } from "@/store/auth";

function Stat({ icon, label, resource }: { icon: React.ReactNode; label: string; resource: string }) {
  const { data } = useList(resource);
  return (
    <Card className="flex items-center gap-3 p-4">
      <span className="flex h-10 w-10 items-center justify-center rounded-lg bg-brand-50 text-brand-600">{icon}</span>
      <div>
        <p className="text-xs text-ink-400">{label}</p>
        <p className="text-lg font-bold text-ink-900">{(data?.meta?.count ?? 0).toLocaleString("fa-IR")}</p>
      </div>
    </Card>
  );
}

export default function DashboardPage() {
  const user = useAuthStore((s) => s.user);
  return (
    <div>
      <h1 className="mb-1 text-lg font-bold text-ink-900">سلام{user ? `، ${user.name}` : ""} 👋</h1>
      <p className="mb-5 text-sm text-ink-500">خلاصهٔ فعالیت‌های سازمان شما</p>
      <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
        <Stat icon={<Newspaper size={18} />} label="اخبار" resource="news" />
        <Stat icon={<PenSquare size={18} />} label="یادداشت‌های بلاگ" resource="blogs" />
        <Stat icon={<CalendarDays size={18} />} label="رویدادها" resource="events" />
        <Stat icon={<BookOpen size={18} />} label="اسناد دانش" resource="knowledge" />
      </div>
    </div>
  );
}
