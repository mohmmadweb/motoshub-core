"use client";
import { useQuery } from "@tanstack/react-query";
import { Bell, LogOut, Moon, Palette, Sun, Type } from "lucide-react";
import Link from "next/link";
import { useEffect, useState } from "react";

import Button from "@/components/ui/Button";
import { useLogout } from "@/hooks/useAuth";
import { api, type Envelope } from "@/lib/api";
import { routes } from "@/lib/routes";
import { useAuthStore } from "@/store/auth";

export default function Header() {
  const user = useAuthStore((s) => s.user);
  const logout = useLogout();
  const [dark, setDark] = useState(false);
  const [large, setLarge] = useState(false);
  const [accentOpen, setAccentOpen] = useState(false);

  useEffect(() => {
    setDark(document.documentElement.classList.contains("dark"));
    setLarge(document.documentElement.getAttribute("data-font") === "large");
  }, []);

  const setAccent = (a: string) => {
    document.documentElement.setAttribute("data-accent", a);
    try { localStorage.setItem("ms-accent", a); } catch { /* ignore */ }
    setAccentOpen(false);
  };

  const toggleFont = () => {
    const next = !large;
    document.documentElement.setAttribute("data-font", next ? "large" : "normal");
    try { localStorage.setItem("ms-font", next ? "large" : "normal"); } catch { /* ignore */ }
    setLarge(next);
  };

  const { data: unread } = useQuery({
    queryKey: ["notifications", "unread_count"],
    queryFn: async () => (await api.get<Envelope<{ count: number }>>("/notifications/unread_count")).data.data,
    refetchInterval: 30000,
  });

  const toggleTheme = () => {
    const next = !dark;
    document.documentElement.classList.toggle("dark", next);
    try { localStorage.setItem("ms-dark", next ? "1" : "0"); } catch { /* ignore */ }
    setDark(next);
  };

  return (
    <header className="flex h-14 items-center justify-between border-b border-ink-200 bg-[var(--surface)] px-4">
      <div className="text-sm text-ink-500">{user ? `${user.name} · ${user.title || "کاربر"}` : ""}</div>
      <div className="flex items-center gap-2">
        <Link href={routes.notifications} className="relative rounded-lg p-2 text-ink-500 hover:bg-ink-100" aria-label="اعلان‌ها">
          <Bell size={18} />
          {!!unread?.count && (
            <span className="absolute -top-0.5 right-0 flex h-4 min-w-4 items-center justify-center rounded-full bg-red-500 px-1 text-[10px] font-bold text-white">
              {unread.count.toLocaleString("fa-IR")}
            </span>
          )}
        </Link>
        <span className="relative">
          <button onClick={() => setAccentOpen((v) => !v)} className="rounded-lg p-2 text-ink-500 hover:bg-ink-100" aria-label="رنگ سازمان">
            <Palette size={18} />
          </button>
          {accentOpen && (
            <span className="absolute left-0 top-full z-20 mt-1 flex gap-1 rounded-lg border border-ink-200 bg-[var(--surface)] p-2 shadow-lg">
              {[["blue","#1f4f99"],["teal","#0d9488"],["amber","#b45309"],["purple","#7c3aed"]].map(([k,c]) => (
                <button key={k} onClick={() => setAccent(k)} className="h-6 w-6 rounded-full border border-ink-200" style={{ backgroundColor: c }} aria-label={k} />
              ))}
            </span>
          )}
        </span>
        <button onClick={toggleFont} className={`rounded-lg p-2 hover:bg-ink-100 ${large ? "text-brand-600" : "text-ink-500"}`} aria-label="اندازه فونت" title="اندازه فونت">
          <Type size={18} />
        </button>
        <button onClick={toggleTheme} className="rounded-lg p-2 text-ink-500 hover:bg-ink-100" aria-label="تغییر تم">
          {dark ? <Sun size={18} /> : <Moon size={18} />}
        </button>
        <Button variant="ghost" size="sm" icon={<LogOut size={16} />} onClick={logout}>خروج</Button>
      </div>
    </header>
  );
}
