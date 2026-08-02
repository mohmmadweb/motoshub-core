import { useEffect, useState } from "react";
import { http } from "./http";

/** Read-only collection loader: GET {path}?page_size=100 → fromApi[]. */
export function useApiList<T>(path: string, fromApi: (x: any) => T): T[] {
  const [items, setItems] = useState<T[]>([]);
  useEffect(() => {
    http<any[]>(`${path}?page_size=100`).then((rows) => setItems(rows.map(fromApi))).catch(() => setItems([]));
  }, [path]);
  return items;
}
