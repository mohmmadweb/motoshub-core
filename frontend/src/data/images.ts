// Presentation helper for content imagery.
// The image itself comes from the record (`image` field on news/blog/event/media).
// When a record has none, we pick deterministically from the bundled set so the
// same item always renders the same picture instead of a bare colour block.
import type { CSSProperties } from "react";

const POOL = [
  "construction", "teamwork", "datacenter", "meeting", "school",
  "expo", "factory", "warehouse", "training", "lab", "energy",
];

const url = (name?: string) =>
  !name ? undefined : /^https?:|^\//.test(name) ? name : `/img/${name}.jpg`;

/** Stable pick so a given id always maps to the same picture. */
function deterministic(id: string): string {
  let h = 0;
  for (let i = 0; i < id.length; i++) h = (h * 31 + id.charCodeAt(i)) >>> 0;
  return POOL[h % POOL.length];
}

/** Image for a content item: its own `image`, else a stable pick from the pool. */
export const contentImg = (id: string, image?: string) => url(image || deterministic(id));

/** Background: image (if any) layered over the item's fallback colour. */
export const bgStyle = (img: string | undefined, color: string): CSSProperties =>
  img
    ? { backgroundImage: `url(${img})`, backgroundSize: "cover", backgroundPosition: "center", backgroundColor: color }
    : { backgroundColor: color };
