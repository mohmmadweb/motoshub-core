import axios, { AxiosError, type AxiosInstance, type InternalAxiosRequestConfig } from "axios";

import { useAuthStore } from "@/store/auth";

// One interceptor-configured instance for the whole app. Base URL is relative so
// the Next rewrite proxies /api/v1 to the backend (no CORS in the browser).
export const api: AxiosInstance = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_BASE_URL || "/api/v1",
  headers: { "Content-Type": "application/json" },
  timeout: 15000,
});

api.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  const token = useAuthStore.getState().access;
  if (token) config.headers.Authorization = `Bearer ${token}`;
  // For file uploads let the browser set the multipart boundary.
  if (typeof FormData !== "undefined" && config.data instanceof FormData) {
    delete config.headers["Content-Type"];
  }
  return config;
});

// Single-flight refresh: on 401, try the refresh token once, then replay.
let refreshing: Promise<string | null> | null = null;

async function refreshAccess(): Promise<string | null> {
  const refresh = useAuthStore.getState().refresh;
  if (!refresh) return null;
  try {
    const res = await axios.post(
      (process.env.NEXT_PUBLIC_API_BASE_URL || "/api/v1") + "/auth/refresh",
      { refresh },
    );
    const access = res.data?.data?.access as string | undefined;
    if (access) {
      useAuthStore.getState().setAccess(access);
      return access;
    }
  } catch {
    /* fall through */
  }
  useAuthStore.getState().reset();
  return null;
}

api.interceptors.response.use(
  (r) => r,
  async (error: AxiosError) => {
    const original = error.config as (InternalAxiosRequestConfig & { _retry?: boolean }) | undefined;
    if (error.response?.status === 401 && original && !original._retry) {
      original._retry = true;
      refreshing = refreshing ?? refreshAccess();
      const access = await refreshing;
      refreshing = null;
      if (access) {
        original.headers.Authorization = `Bearer ${access}`;
        return api(original);
      }
    }
    return Promise.reject(error);
  },
);

// The API envelope. Detail endpoints return `data` only; lists add links/meta.
export interface Envelope<T> {
  data: T;
  links?: Record<string, string | null>;
  meta?: { count: number; page: number; pages: number; page_size: number };
}
