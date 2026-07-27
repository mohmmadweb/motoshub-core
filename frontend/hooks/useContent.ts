"use client";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { api, type Envelope } from "@/lib/api";

// Generic list/create hooks over any tenant-scoped content resource.
export function useList<T>(resource: string, params?: Record<string, unknown>) {
  return useQuery({
    queryKey: [resource, params ?? {}],
    queryFn: async () => {
      const res = await api.get<Envelope<T[]>>(`/${resource}`, { params });
      return res.data;
    },
  });
}

export function useCreate<T>(resource: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (payload: Partial<T>) => {
      const res = await api.post<Envelope<T>>(`/${resource}`, payload);
      return res.data.data;
    },
    onSuccess: () => qc.invalidateQueries({ queryKey: [resource] }),
  });
}

export function useUpdate<T>(resource: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async ({ id, payload }: { id: string; payload: Partial<T> }) => {
      const res = await api.patch<Envelope<T>>(`/${resource}/${id}`, payload);
      return res.data.data;
    },
    onSuccess: () => qc.invalidateQueries({ queryKey: [resource] }),
  });
}

export function useRemoveById(resource: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (id: string) => {
      await api.delete(`/${resource}/${id}`);
    },
    onSuccess: () => qc.invalidateQueries({ queryKey: [resource] }),
  });
}
