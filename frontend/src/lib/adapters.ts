/**
 * Adapters: backend /api/v1 shapes → prototype UI shapes (and payloads back).
 * Keeps the prototype UI untouched while data comes from the real API.
 */
import { relativeFa, toJalali, toTime, visToApi, visToFa } from "./jalali";

const docType: Record<string, string> = { contract: "قرارداد", training: "آموزشی", minutes: "صورت‌جلسه", report: "گزارش" };
const docTypeApi: Record<string, string> = { "قرارداد": "contract", "آموزشی": "training", "صورت‌جلسه": "minutes", "گزارش": "report" };

/* eslint-disable @typescript-eslint/no-explicit-any */
export const fromNews = (n: any) => ({
  id: n.id, title: n.title, summary: n.summary, date: toJalali(n.created_at),
  comments: n.comment_count ?? 0, views: n.views ?? 0, pinned: n.pinned, visibility: visToFa(n.visibility),
});
export const toNews = (v: any) => ({ title: v.title, summary: v.summary, pinned: v.pinned, visibility: visToApi(v.visibility) });

export const fromBlog = (b: any) => ({
  id: b.id, title: b.title, author: b.author?.name ?? "—", excerpt: b.excerpt,
  date: toJalali(b.created_at), rating: Number(b.rating ?? 0), tags: b.tags ?? [], visibility: visToFa(b.visibility),
});
export const toBlog = (v: any) => ({ title: v.title, excerpt: v.excerpt, tags: v.tags ?? [], visibility: visToApi(v.visibility) });

export const fromEvent = (e: any) => ({
  id: e.id, title: e.title, date: toJalali(e.starts_at), jalaliDate: toJalali(e.starts_at), time: toTime(e.starts_at),
  location: e.location, attendees: e.attendees ?? 0, hashtags: e.hashtags ?? [], description: e.description,
  visibility: visToFa(e.visibility), mode: e.mode === "online" ? "آنلاین" : "حضوری", joinLink: e.join_link, mapUrl: e.map_url,
});
export const toEvent = (v: any) => ({
  title: v.title, location: v.location, description: v.description, visibility: visToApi(v.visibility),
  mode: v.mode === "آنلاین" ? "online" : "in_person",
  ...(v.starts_at || v.date ? { starts_at: v.starts_at || v.date } : {}),
});

export const fromMedia = (m: any) => ({
  id: m.id, kind: m.kind, title: m.title, album: m.album, uploadedBy: m.author?.name ?? "—",
  date: toJalali(m.created_at), rating: Number(m.rating ?? 0), tags: m.tags ?? [], color: m.color ?? "#1f4f99", visibility: visToFa(m.visibility),
});
export const toMedia = (v: any) => ({ kind: v.kind, title: v.title, album: v.album, color: v.color, visibility: visToApi(v.visibility) });

export const fromKnowledge = (k: any) => ({
  id: k.id, title: k.title, category: k.category, type: docType[k.doc_type] ?? "گزارش",
  updatedAt: toJalali(k.updated_at ?? k.created_at), owner: k.owner?.name ?? "—", size: k.size ?? "—", visibility: visToFa(k.visibility),
});
export const toKnowledge = (v: any) => ({ title: v.title, category: v.category, doc_type: docTypeApi[v.type] ?? "report", size: v.size, visibility: visToApi(v.visibility) });

export const fromForum = (t: any) => ({
  id: t.id, title: t.title, author: t.author?.name ?? "—", replies: t.reply_count ?? 0, views: t.views ?? 0,
  lastActivity: relativeFa(t.updated_at ?? t.created_at), category: t.category, solved: t.solved, visibility: visToFa(t.visibility),
});
export const toForum = (v: any) => ({ title: v.title, body: v.body ?? "", category: v.category, visibility: visToApi(v.visibility) });

export const fromGroup = (g: any) => ({
  id: g.id, name: g.name, description: g.description, members: g.member_count ?? 0,
  privacy: g.privacy === "public" ? "عمومی" : "خصوصی", color: g.color ?? "#1f4f99", unread: 0, category: g.category ?? "",
  createdAt: toJalali(g.created_at), lastActivityAt: toJalali(g.updated_at ?? g.created_at), lastActivityRel: relativeFa(g.updated_at ?? g.created_at),
});
export const toGroup = (v: any) => ({ name: v.name, description: v.description, category: v.category, color: v.color, privacy: v.privacy === "عمومی" ? "public" : "private" });
