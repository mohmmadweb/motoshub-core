import { create } from "zustand";

export type ToastType = "success" | "error" | "info";
export interface Toast { id: number; message: string; type: ToastType; }

interface ToastState {
  toasts: Toast[];
  push: (message: string, type?: ToastType) => void;
  dismiss: (id: number) => void;
}

let seq = 1;
export const useToastStore = create<ToastState>((set) => ({
  toasts: [],
  push: (message, type = "success") => {
    const id = seq++;
    set((s) => ({ toasts: [...s.toasts, { id, message, type }] }));
    setTimeout(() => set((s) => ({ toasts: s.toasts.filter((t) => t.id !== id) })), 3000);
  },
  dismiss: (id) => set((s) => ({ toasts: s.toasts.filter((t) => t.id !== id) })),
}));

/** Non-hook accessor so plain functions (query hooks) can toast. */
export const toast = (message: string, type: ToastType = "success") =>
  useToastStore.getState().push(message, type);
