"use client";
import { X } from "lucide-react";
import { useEffect, type ReactNode } from "react";

interface Props {
  open: boolean;
  onClose: () => void;
  title: string;
  children: ReactNode;
}

export default function Modal({ open, onClose, title, children }: Props) {
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => e.key === "Escape" && onClose();
    if (open) document.addEventListener("keydown", onKey);
    return () => document.removeEventListener("keydown", onKey);
  }, [open, onClose]);

  if (!open) return null;
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4" role="dialog" aria-modal="true">
      <div className="absolute inset-0 bg-black/40" onClick={onClose} />
      <div className="relative z-10 w-full max-w-md rounded-2xl bg-[var(--surface)] p-5 shadow-xl">
        <div className="mb-4 flex items-center justify-between">
          <h2 className="font-bold text-ink-900">{title}</h2>
          <button onClick={onClose} className="rounded-lg p-1 text-ink-400 hover:bg-ink-100" aria-label="بستن">
            <X size={18} />
          </button>
        </div>
        {children}
      </div>
    </div>
  );
}
