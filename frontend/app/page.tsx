"use client";
import { useQuery } from "@tanstack/react-query";
import { ArrowLeft, CalendarDays, Newspaper, PenSquare } from "lucide-react";
import Link from "next/link";

import Button from "@/components/ui/Button";
import Card from "@/components/ui/Card";
import { api, type Envelope } from "@/lib/api";
import { faDate } from "@/lib/format";
import type { BlogPost, EventItem, News } from "@/types";

interface Feed { news: News[]; blogs: BlogPost[]; events: EventItem[]; }

export default function PublicLanding() {
  const { data } = useQuery({
    queryKey: ["public/feed"],
    queryFn: async () => (await api.get<Envelope<Feed>>("/public/feed")).data.data,
  });
  return (
    <main dir="rtl" className="min-h-screen bg-ink-50">
      <header className="flex items-center justify-between border-b border-ink-200 bg-[var(--surface)] px-6 py-4">
        <div className="flex items-center gap-2">
          <span className="flex h-9 w-9 items-center justify-center rounded-lg bg-brand-600 font-bold text-white">م</span>
          <span className="font-bold text-ink-900">موتوشاب</span>
        </div>
        <Link href="/login"><Button size="sm" icon={<ArrowLeft size={15} />}>ورود به سامانه</Button></Link>
      </header>

      <section className="bg-navy-900 px-6 py-16 text-center text-white">
        <h1 className="text-3xl font-bold">پلتفرم ارتباطات و فرآیندهای سازمانی</h1>
        <p className="mx-auto mt-3 max-w-xl text-navy-200">اخبار، رویدادها و دستاوردهای عمومی سازمان را این‌جا دنبال کنید.</p>
      </section>

      <div className="mx-auto max-w-5xl space-y-8 p-6">
        <Section title="اخبار" icon={<Newspaper size={18} />}>
          {(data?.news ?? []).map((n) => (
            <Card key={n.id} className="p-4"><h3 className="font-semibold text-ink-900">{n.title}</h3><p className="mt-1 text-sm text-ink-500">{n.summary}</p><p className="mt-2 text-xs text-ink-400">{faDate(n.created_at)}</p></Card>
          ))}
        </Section>
        <Section title="یادداشت‌ها" icon={<PenSquare size={18} />}>
          {(data?.blogs ?? []).map((b) => (
            <Card key={b.id} className="p-4"><h3 className="font-semibold text-ink-900">{b.title}</h3><p className="mt-1 text-sm text-ink-500">{b.excerpt}</p></Card>
          ))}
        </Section>
        <Section title="رویدادها" icon={<CalendarDays size={18} />}>
          {(data?.events ?? []).map((e) => (
            <Card key={e.id} className="p-4"><h3 className="font-semibold text-ink-900">{e.title}</h3><p className="mt-1 text-xs text-ink-400">{e.location} · {faDate(e.starts_at)}</p></Card>
          ))}
        </Section>
      </div>
    </main>
  );
}

function Section({ title, icon, children }: { title: string; icon: React.ReactNode; children: React.ReactNode }) {
  return (
    <div>
      <h2 className="mb-3 flex items-center gap-2 text-lg font-bold text-ink-900">{icon} {title}</h2>
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">{children}</div>
    </div>
  );
}
