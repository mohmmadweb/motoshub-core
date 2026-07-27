import { create } from "zustand";
import { persist } from "zustand/middleware";

import type { User } from "@/types";

interface AuthState {
  access: string | null;
  refresh: string | null;
  user: User | null;
  setSession: (p: { access: string; refresh: string; user: User }) => void;
  setAccess: (access: string) => void;
  setUser: (user: User) => void;
  reset: () => void;
  can: (perm: string) => boolean;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      access: null,
      refresh: null,
      user: null,
      setSession: ({ access, refresh, user }) => set({ access, refresh, user }),
      setAccess: (access) => set({ access }),
      setUser: (user) => set({ user }),
      reset: () => set({ access: null, refresh: null, user: null }),
      can: (perm) => !!get().user?.permissions.includes(perm),
    }),
    { name: "motoshub-auth" },
  ),
);
