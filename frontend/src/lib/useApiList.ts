import { useCallback, useEffect, useState } from "react";
import { http } from "./http";

/** Read-only collection loader: GET {path}?page_size=100 → fromApi[]. */
export function useApiList<T>(path: string, fromApi: (x: unknown) => T): T[] {
  return useApiListReloadable(path, fromApi)[0];
}

/**
 * Same, plus a `reload` for pages that also create or delete rows — without it
 * a page had no way to show what it had just written, which is why several
 * "create" buttons only ever raised a toast.
 */
export function useApiListReloadable<T>(
  path: string,
  fromApi: (x: unknown) => T,
): [T[], () => Promise<void>] {
  const [items, setItems] = useState<T[]>([]);
  const reload = useCallback(
    () =>
      http<unknown[]>(`${path}?page_size=100`)
        .then((rows) => setItems(rows.map(fromApi)))
        .catch(() => setItems([])),
    // fromApi is a module-level function in every caller; keyed on path alone.
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [path],
  );
  useEffect(() => { reload(); }, [reload]);
  return [items, reload];
}
