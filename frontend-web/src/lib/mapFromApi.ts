// Map Django API payloads → the prototype's data shapes (incl. enum translation).
const vis = (v: string) => (v === "public" ? "عمومی" : "خصوصی") as "عمومی" | "خصوصی";
const name = (o: any) => o?.name ?? "—";
const docType: Record<string, string> = { contract: "قرارداد", training: "آموزشی", minutes: "صورت‌جلسه", report: "گزارش" };

export const mapNews = (n: any) => ({
  id: n.id, title: n.title, summary: n.summary, date: n.created_at,
  comments: n.comment_count ?? 0, views: n.views ?? 0, pinned: !!n.pinned, visibility: vis(n.visibility),
});
export const mapBlog = (b: any) => ({
  id: b.id, title: b.title, author: name(b.author), excerpt: b.excerpt, date: b.created_at,
  rating: Number(b.rating) || 0, tags: b.tags ?? [], visibility: vis(b.visibility),
});
export const mapEvent = (e: any) => ({
  id: e.id, title: e.title, date: e.starts_at, jalaliDate: "", time: "",
  location: e.location, attendees: e.attendees ?? 0, hashtags: [], description: e.description ?? "",
  visibility: vis(e.visibility), mode: e.mode === "online" ? "آنلاین" : "حضوری",
  joinLink: e.join_link || undefined, mapUrl: e.map_url || undefined,
});
export const mapMedia = (m: any) => ({
  id: m.id, kind: m.kind, title: m.title, album: m.album, uploadedBy: name(m.author),
  date: m.created_at, rating: Number(m.rating) || 0, tags: m.tags ?? [], color: m.color || "#1f4f99",
  visibility: vis(m.visibility),
});
export const mapKnowledge = (k: any) => ({
  id: k.id, title: k.title, category: k.category, type: docType[k.doc_type] ?? "گزارش",
  updatedAt: k.updated_at ?? k.created_at, owner: name(k.owner), size: k.size || "—", visibility: vis(k.visibility),
});
export const mapGroup = (g: any) => ({
  id: g.id, name: g.name, description: g.description, members: g.member_count ?? 0,
  privacy: vis(g.privacy), color: g.color || "#1f4f99", unread: 0, category: g.category || "",
  createdAt: g.created_at, lastActivityAt: g.created_at, lastActivityRel: "",
});
export const mapForum = (t: any) => ({
  id: t.id, title: t.title, author: name(t.author), replies: t.reply_count ?? 0, views: t.views ?? 0,
  lastActivity: "", category: t.category || "", solved: !!t.solved, visibility: vis(t.visibility),
});
