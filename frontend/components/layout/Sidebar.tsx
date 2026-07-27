"use client";
import { Newspaper, PenSquare, CalendarDays, Image as ImageIcon, BookOpen, LayoutDashboard, Users, MessagesSquare, FolderKanban, FileSignature, Landmark, GraduationCap, BarChart3, LifeBuoy, FlaskConical, Trophy } from "lucide-react";
import Link from "next/link";
import { usePathname } from "next/navigation";

import { cn } from "@/lib/cn";
import { routes } from "@/lib/routes";

const items = [
  { href: routes.dashboard, label: "داشبورد", icon: LayoutDashboard },
  { href: routes.groups, label: "گروه‌ها", icon: Users },
  { href: routes.forum, label: "تالار گفتگو", icon: MessagesSquare },
  { href: routes.news, label: "اخبار", icon: Newspaper },
  { href: routes.blog, label: "بلاگ", icon: PenSquare },
  { href: routes.events, label: "رویدادها", icon: CalendarDays },
  { href: routes.media, label: "رسانه", icon: ImageIcon },
  { href: routes.knowledge, label: "مدیریت دانش", icon: BookOpen },
  { href: routes.projects, label: "پروژه‌ها", icon: FolderKanban },
  { href: routes.contracts, label: "قراردادها", icon: FileSignature },
  { href: routes.funds, label: "صندوق نوآور", icon: Landmark },
  { href: routes.training, label: "آموزش", icon: GraduationCap },
  { href: routes.polls, label: "نظرسنجی‌ها", icon: BarChart3 },
  { href: routes.research, label: "پژوهش", icon: FlaskConical },
  { href: routes.awards, label: "جایزه نوآوری", icon: Trophy },
  { href: routes.tickets, label: "تیکت‌ها", icon: LifeBuoy },
];

export default function Sidebar() {
  const pathname = usePathname();
  return (
    <aside className="hidden w-60 shrink-0 border-l border-ink-200 bg-[var(--surface)] p-3 md:block">
      <div className="mb-6 flex items-center gap-2 px-2 pt-2">
        <span className="flex h-9 w-9 items-center justify-center rounded-lg bg-brand-600 font-bold text-white">م</span>
        <span className="font-bold text-ink-900">موتوشاب</span>
      </div>
      <nav className="space-y-1">
        {items.map(({ href, label, icon: Icon }) => {
          const active = pathname === href || pathname.startsWith(href + "/");
          return (
            <Link
              key={href}
              href={href}
              className={cn(
                "flex items-center gap-3 rounded-lg px-3 py-2 text-sm transition-colors",
                active ? "bg-brand-50 font-semibold text-brand-700" : "text-ink-600 hover:bg-ink-100",
              )}
            >
              <Icon size={18} /> {label}
            </Link>
          );
        })}
      </nav>
    </aside>
  );
}
