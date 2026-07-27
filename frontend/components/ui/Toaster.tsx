"use client";
import { CheckCircle2, Info, X, XCircle } from "lucide-react";

import { useToastStore } from "@/store/toast";

const icon = { success: CheckCircle2, error: XCircle, info: Info };
const tone = {
  success: "border-emerald-200 bg-emerald-50 text-emerald-800",
  error: "border-red-200 bg-red-50 text-red-800",
  info: "border-ink-200 bg-[var(--surface)] text-ink-800",
};

export default function Toaster() {
  const { toasts, dismiss } = useToastStore();
  return (
    <div className="fixed bottom-4 left-1/2 z-[60] flex -translate-x-1/2 flex-col items-center gap-2" dir="rtl">
      {toasts.map((t) => {
        const Icon = icon[t.type];
        return (
          <div key={t.id} className={`flex items-center gap-2 rounded-lg border px-4 py-2 text-sm shadow-lg ${tone[t.type]}`}>
            <Icon size={16} /> <span>{t.message}</span>
            <button onClick={() => dismiss(t.id)} className="opacity-60 hover:opacity-100" aria-label="بستن"><X size={14} /></button>
          </div>
        );
      })}
    </div>
  );
}
