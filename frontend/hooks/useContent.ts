"use client";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { api, type Envelope } from "@/lib/api";
import { toast } from "@/store/toast";

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
    mutationFn: async (payload: Partial<T> | FormData) => {
      const res = await api.post<Envelope<T>>(`/${resource}`, payload);
      return res.data.data;
    },
    onSuccess: () => { qc.invalidateQueries({ queryKey: [resource] }); toast("با موفقیت ثبت شد."); },
    onError: () => toast("ثبت ناموفق بود.", "error"),
  });
}

export function useUpdate<T>(resource: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async ({ id, payload }: { id: string; payload: Partial<T> }) => {
      const res = await api.patch<Envelope<T>>(`/${resource}/${id}`, payload);
      return res.data.data;
    },
    onSuccess: () => { qc.invalidateQueries({ queryKey: [resource] }); toast("تغییرات ذخیره شد."); },
    onError: () => toast("ذخیره ناموفق بود.", "error"),
  });
}

export function useRemoveById(resource: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (id: string) => {
      await api.delete(`/${resource}/${id}`);
    },
    onSuccess: () => { qc.invalidateQueries({ queryKey: [resource] }); toast("حذف شد."); },
    onError: () => toast("حذف ناموفق بود.", "error"),
  });
}
