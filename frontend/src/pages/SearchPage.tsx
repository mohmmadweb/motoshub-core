import { useEffect, useMemo, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import {
  Search,
  Newspaper,
  NotebookPen,
  CalendarDays,
  Image as ImageIcon,
  BookOpen,
  Users,
  MessagesSquare,
  User,
  KanbanSquare,
  FileSignature,
  PiggyBank,
  GraduationCap,
  Trophy,
  Hash,
  ListChecks,
} from "lucide-react";
import { http } from "../lib/http";
import PageHeader from "../components/ui/PageHeader";
import Badge from "../components/ui/Badge";
import EmptyState from "../components/ui/EmptyState";

// جستجوی سراسری واقعی: همه‌ی ماژول‌های سامانه ایندکس می‌شوند
type Hit = {
  id: string;
  type: string;
  icon: typeof Search;
  title: string;
  snippet: string;
  to: string;
};

const typeMeta: Record<string, { label: string; icon: typeof Search }> = {
  news: { label: "خبر", icon: Newspaper },
  blog: { label: "بلاگ", icon: NotebookPen },
  event: { label: "رویداد", icon: CalendarDays },
  media: { label: "رسانه", icon: ImageIcon },
  doc: { label: "سند دانش", icon: BookOpen },
  group: { label: "گروه", icon: Users },
  forum: { label: "انجمن", icon: MessagesSquare },
  user: { label: "کاربر", icon: User },
  project: { label: "پروژه", icon: KanbanSquare },
  contract: { label: "قرارداد", icon: FileSignature },
  nf: { label: "صندوق نوآور", icon: PiggyBank },
  training: { label: "دوره آموزشی", icon: GraduationCap },
  channel: { label: "کانال", icon: Hash },
  publication: { label: "نشریه", icon: NotebookPen },
  award: { label: "جایزه نوآوری", icon: Trophy },
  transfer: { label: "تبادل فناوری", icon: FileSignature },
  rfp: { label: "فراخوان RFP", icon: ListChecks },
};

export default function SearchPage() {
  const [params, setParams] = useSearchParams();
  const q = params.get("q") ?? "";
  const [typeFilter, setTypeFilter] = useState<string>("all");
  const [allMatched, setAllMatched] = useState<Hit[]>([]);

  // Real server-side search across all modules (debounced).
  useEffect(() => {
    const term = q.trim();
    if (term.length < 2) { setAllMatched([]); return; }
    const timer = setTimeout(() => {
      http<{ results: any[] }>(`/search?q=${encodeURIComponent(term)}`)
        .then((d) => setAllMatched(d.results.map((h) => ({
          ...h, id: `${h.type}-${h.id}`, icon: (typeMeta[h.type]?.icon ?? Search),
        }))))
        .catch(() => setAllMatched([]));
    }, 250);
    return () => clearTimeout(timer);
  }, [q]);

  const results = typeFilter === "all" ? allMatched : allMatched.filter((h) => h.type === typeFilter);

  const countsByType = useMemo(
    () => allMatched.reduce<Record<string, number>>((acc, h) => ((acc[h.type] = (acc[h.type] ?? 0) + 1), acc), {}),
    [allMatched]
  );

  const setQuery = (value: string) => {
    const next = new URLSearchParams(params);
    if (value) next.set("q", value);
    else next.delete("q");
    setParams(next, { replace: true });
  };

  return (
    <div>
      <PageHeader
        title="جستجوی سراسری"
        description="جستجو در همه‌ی ماژول‌ها: اخبار، بلاگ، رویداد، اسناد، گروه‌ها، انجمن، کاربران، پروژه‌ها، صندوق، قراردادها، آموزش، کانال‌ها و…"
        icon={<Search size={18} />}
      />

      <div className="relative max-w-xl mb-4">
        <Search size={16} className="absolute right-3.5 top-1/2 -translate-y-1/2 text-ink-400" />
        <input
          autoFocus
          value={q}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="چه چیزی را جستجو می‌کنید؟"
          className="input-field !pr-10 !py-3 !text-sm"
          aria-label="عبارت جستجو"
        />
      </div>

      {q.trim() && (
        <div className="flex items-center gap-1.5 flex-wrap mb-4">
          <button
            onClick={() => setTypeFilter("all")}
            className={`px-3 py-1.5 text-xs font-medium rounded-full border transition-colors ${typeFilter === "all" ? "bg-navy-900 text-white border-navy-900" : "bg-white text-ink-600 border-ink-200 hover:bg-ink-50"}`}
          >
            همه ({allMatched.length.toLocaleString("fa-IR")})
          </button>
          {Object.entries(countsByType).map(([t, count]) => (
            <button
              key={t}
              onClick={() => setTypeFilter(typeFilter === t ? "all" : t)}
              className={`px-3 py-1.5 text-xs font-medium rounded-full border transition-colors ${typeFilter === t ? "bg-brand-600 text-white border-brand-600" : "bg-white text-ink-600 border-ink-200 hover:border-brand-300"}`}
            >
              {typeMeta[t]?.label ?? t} ({count.toLocaleString("fa-IR")})
            </button>
          ))}
        </div>
      )}

      {!q.trim() ? (
        <EmptyState icon={<Search size={20} />} title="عبارتی بنویسید تا در کل سامانه جستجو شود" />
      ) : results.length === 0 ? (
        <EmptyState icon={<Search size={20} />} title={`نتیجه‌ای برای «${q}» پیدا نشد`} />
      ) : (
        <div className="card divide-y divide-ink-100">
          {results.slice(0, 50).map((h) => {
            const Icon = h.icon;
            return (
              <Link key={h.id} to={h.to} className="flex items-center gap-3 px-4 py-3 hover:bg-ink-50/60 transition-colors group">
                <span className="w-9 h-9 rounded-lg bg-ink-100 text-ink-500 flex items-center justify-center shrink-0 group-hover:bg-brand-50 group-hover:text-brand-600 transition-colors">
                  <Icon size={15} />
                </span>
                <span className="flex-1 min-w-0">
                  <span className="block text-sm font-medium text-ink-900 group-hover:text-brand-700 truncate">{h.title}</span>
                  <span className="block text-[12px] text-ink-400 truncate">{h.snippet}</span>
                </span>
                <Badge tone="neutral">{typeMeta[h.type]?.label ?? h.type}</Badge>
              </Link>
            );
          })}
          {results.length > 50 && (
            <p className="p-3 text-center text-[12px] text-ink-400">{(results.length - 50).toLocaleString("fa-IR")} نتیجه‌ی دیگر — عبارت را دقیق‌تر کنید</p>
          )}
        </div>
      )}
    </div>
  );
}
