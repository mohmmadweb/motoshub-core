import { cn } from "@/lib/cn";
import type { ReactNode } from "react";

type Tone = "brand" | "navy" | "success" | "warning" | "neutral";
const tones: Record<Tone, string> = {
  brand: "bg-brand-50 text-brand-700",
  navy: "bg-navy-100 text-navy-700",
  success: "bg-emerald-50 text-emerald-700",
  warning: "bg-amber-50 text-amber-700",
  neutral: "bg-ink-100 text-ink-600",
};

export default function Badge({ tone = "neutral", children }: { tone?: Tone; children: ReactNode }) {
  return <span className={cn("inline-flex items-center gap-1 rounded-full px-2.5 py-0.5 text-[11px] font-medium", tones[tone])}>{children}</span>;
}
