"use client";
import { useRouter } from "next/navigation";
import { useEffect, useState, type ReactNode } from "react";

import Header from "@/components/layout/Header";
import Sidebar from "@/components/layout/Sidebar";
import { routes } from "@/lib/routes";
import { useAuthStore } from "@/store/auth";

export default function AppLayout({ children }: { children: ReactNode }) {
  const router = useRouter();
  const access = useAuthStore((s) => s.access);
  const [ready, setReady] = useState(false);

  useEffect(() => {
    // Auth state hydrates from localStorage on the client.
    if (!access) router.replace(routes.login);
    else setReady(true);
  }, [access, router]);

  if (!ready) {
    return <div className="flex min-h-screen items-center justify-center text-ink-400">در حال بارگذاری…</div>;
  }

  return (
    <div className="flex min-h-screen" dir="rtl">
      <Sidebar />
      <div className="flex min-w-0 flex-1 flex-col">
        <Header />
        <main className="flex-1 overflow-auto p-5">{children}</main>
      </div>
    </div>
  );
}
