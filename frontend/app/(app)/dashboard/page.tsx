"use client";
import { BookOpen, CalendarDays, Newspaper, PenSquare } from "lucide-react";
import Link from "next/link";

import Card from "@/components/ui/Card";
import { useList } from "@/hooks/useContent";
import { faDate } from "@/lib/format";
import { useAuthStore } from "@/store/auth";
import type { EventItem, News } from "@/types";

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
  const news = useList<News>("news");
  const events = useList<EventItem>("events");
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

      <div className="mt-6 grid grid-cols-1 gap-4 lg:grid-cols-2">
        <Card className="p-4">
          <h2 className="mb-3 text-sm font-bold text-ink-700">آخرین اخبار</h2>
          <div className="space-y-2">
            {(news.data?.data ?? []).slice(0, 5).map((n) => (
              <Link key={n.id} href={`/news/${n.id}`} className="block rounded-lg p-2 hover:bg-ink-100">
                <p className="text-sm text-ink-800">{n.title}</p>
                <p className="text-xs text-ink-400">{faDate(n.created_at)}</p>
              </Link>
            ))}
            {(news.data?.data ?? []).length === 0 && <p className="text-xs text-ink-400">خبری نیست.</p>}
          </div>
        </Card>
        <Card className="p-4">
          <h2 className="mb-3 text-sm font-bold text-ink-700">رویدادهای پیش‌رو</h2>
          <div className="space-y-2">
            {(events.data?.data ?? []).slice(0, 5).map((e) => (
              <Link key={e.id} href={`/events/${e.id}`} className="block rounded-lg p-2 hover:bg-ink-100">
                <p className="text-sm text-ink-800">{e.title}</p>
                <p className="text-xs text-ink-400">{e.location} · {faDate(e.starts_at)}</p>
              </Link>
            ))}
            {(events.data?.data ?? []).length === 0 && <p className="text-xs text-ink-400">رویدادی نیست.</p>}
          </div>
        </Card>
      </div>
    </div>
  );
}
