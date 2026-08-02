import { useEffect, useRef, useState } from "react";
import { http } from "./http";

/* eslint-disable @typescript-eslint/no-explicit-any */
/**
 * Loads a collection from /api/v1 and returns [items, setItems] where setItems
 * has the SAME signature as useState's setter but persists the diff to the API
 * (create POST / update PATCH / delete DELETE). Lets prototype pages that do
 * local CRUD become real without rewriting them.
 */
export function useApiCollection<T extends { id: string }>(
  path: string,
  fromApi: (x: any) => T,
  toApi: (x: T) => any,
): [T[], (updater: (prev: T[]) => T[]) => void] {
  const [items, setItemsRaw] = useState<T[]>([]);
  const cur = useRef<T[]>([]);
  cur.current = items;

  useEffect(() => {
    let cancelled = false;
    http<any[]>(`${path}?page_size=100`)
      .then((rows) => { if (!cancelled) setItemsRaw(rows.map(fromApi)); })
      .catch(() => {});
    return () => { cancelled = true; };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [path]);

  const setItems = (updater: (prev: T[]) => T[]) => {
    const prev = cur.current;
    const next = updater(prev);
    setItemsRaw(next);
    const prevById = new Map(prev.map((x) => [x.id, x]));
    const nextById = new Map(next.map((x) => [x.id, x]));
    next.filter((x) => !prevById.has(x.id)).forEach((item) => {
      http(path, { method: "POST", body: JSON.stringify(toApi(item)) })
        .then((created: any) => setItemsRaw(cur.current.map((c) => (c.id === item.id ? fromApi(created) : c))))
        .catch(() => {});
    });
    prev.filter((x) => !nextById.has(x.id)).forEach((item) =>
      http(`${path}/${item.id}`, { method: "DELETE" }).catch(() => {}));
    next.filter((x) => prevById.has(x.id) && JSON.stringify(x) !== JSON.stringify(prevById.get(x.id))).forEach((item) =>
      http(`${path}/${item.id}`, { method: "PATCH", body: JSON.stringify(toApi(item)) }).catch(() => {}));
  };

  return [items, setItems];
}
