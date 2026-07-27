import { cn } from "@/lib/cn";
import type { ReactNode } from "react";

export default function Card({ className, children }: { className?: string; children: ReactNode }) {
  return (
    <div className={cn("rounded-xl border border-ink-200 bg-[var(--surface)] shadow-sm", className)}>
      {children}
    </div>
  );
}
