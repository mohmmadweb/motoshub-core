"use client";
import { LogOut, Moon, Sun } from "lucide-react";
import { useEffect, useState } from "react";

import Button from "@/components/ui/Button";
import { useLogout } from "@/hooks/useAuth";
import { useAuthStore } from "@/store/auth";

export default function Header() {
  const user = useAuthStore((s) => s.user);
  const logout = useLogout();
  const [dark, setDark] = useState(false);

  useEffect(() => {
    const isDark = document.documentElement.classList.contains("dark");
    setDark(isDark);
  }, []);

  const toggleTheme = () => {
    const next = !dark;
    document.documentElement.classList.toggle("dark", next);
    setDark(next);
  };

  return (
    <header className="flex h-14 items-center justify-between border-b border-ink-200 bg-[var(--surface)] px-4">
      <div className="text-sm text-ink-500">
        {user ? `${user.name} · ${user.title || "کاربر"}` : ""}
      </div>
      <div className="flex items-center gap-2">
        <button onClick={toggleTheme} className="rounded-lg p-2 text-ink-500 hover:bg-ink-100" aria-label="تغییر تم">
          {dark ? <Sun size={18} /> : <Moon size={18} />}
        </button>
        <Button variant="ghost" size="sm" icon={<LogOut size={16} />} onClick={logout}>
          خروج
        </Button>
      </div>
    </header>
  );
}
