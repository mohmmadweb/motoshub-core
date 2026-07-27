"use client";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useRouter } from "next/navigation";

import { api } from "@/lib/api";
import { routes } from "@/lib/routes";
import { useAuthStore } from "@/store/auth";
import type { User } from "@/types";

interface LoginResult {
  access: string;
  refresh: string;
  user: User;
}

export function useLogin() {
  const router = useRouter();
  const setSession = useAuthStore((s) => s.setSession);

  return useMutation({
    mutationFn: async (creds: { username: string; password: string }) => {
      const res = await api.post("/auth/login", creds);
      return res.data.data as LoginResult;
    },
    onSuccess: (data) => {
      setSession(data);
      router.push(routes.dashboard);
    },
  });
}

export function useLogout() {
  const router = useRouter();
  const reset = useAuthStore((s) => s.reset);
  const qc = useQueryClient();
  return () => {
    reset();
    qc.clear();
    router.push(routes.login);
  };
}
