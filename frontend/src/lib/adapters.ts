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

// ── Process modules ─────────────────────────────────────────────────────────
const health: Record<string, string> = { green: "سبز", yellow: "زرد", red: "قرمز" };
const healthApi: Record<string, string> = { "سبز": "green", "زرد": "yellow", "قرمز": "red" };
export const fromProject = (p: any) => ({
  id: p.id, name: p.name, client: p.client, health: health[p.health] ?? "سبز",
  progress: p.progress ?? 0, budgetUsed: Number(p.budget_used ?? 0), deadline: toJalali(p.deadline), tasks: [] as any[],
});
export const toProject = (v: any) => ({ name: v.name, client: v.client, health: healthApi[v.health] ?? "green", progress: v.progress, budget_used: v.budgetUsed });

const rStage: Record<string, string> = { open: "فراخوان باز", review: "بررسی درخواست‌ها", judging: "داوری", running: "در حال اجرا", closed: "پایان‌یافته" };
const rStageApi: Record<string, string> = { "فراخوان باز": "open", "بررسی درخواست‌ها": "review", "داوری": "judging", "در حال اجرا": "running", "پایان‌یافته": "closed" };
export const fromResearch = (r: any) => ({
  id: r.id, title: r.title, field: r.field, stage: rStage[r.stage] ?? "فراخوان باز",
  applicants: r.applicant_count ?? 0, deadline: toJalali(r.deadline),
});
export const toResearch = (v: any) => ({ title: v.title, field: v.field, stage: rStageApi[v.stage] ?? "open" });

const cStatus: Record<string, string> = { open: "ثبت‌نام باز", running: "در حال برگزاری", done: "برگزار شده" };
const cStatusApi: Record<string, string> = { "ثبت‌نام باز": "open", "در حال برگزاری": "running", "برگزار شده": "done" };
export const fromCourse = (c: any) => ({
  id: c.id, title: c.title, instructor: c.instructor, date: toJalali(c.starts_at), hours: c.hours ?? 0,
  capacity: c.capacity ?? 0, enrolled: c.enrolled ?? 0, status: cStatus[c.status] ?? "ثبت‌نام باز",
  satisfaction: c.satisfaction != null ? Number(c.satisfaction) : undefined,
});
export const toCourse = (v: any) => ({ title: v.title, instructor: v.instructor, hours: v.hours, capacity: v.capacity, status: cStatusApi[v.status] ?? "open" });

// ── Tickets & Polls (list + create real; sub-actions reply/vote stay local) ──
const prio: Record<string, string> = { low: "کم", medium: "متوسط", urgent: "فوری" };
const prioApi: Record<string, string> = { "کم": "low", "متوسط": "medium", "فوری": "urgent" };
const tStatus: Record<string, string> = { open: "باز", in_review: "در حال بررسی", answered: "پاسخ داده شد", closed: "بسته" };
export const fromTicket = (t: any) => ({
  id: t.id, no: t.number ?? "", subject: t.subject, category: t.category ?? "",
  priority: prio[t.priority] ?? "متوسط", status: tStatus[t.status] ?? "باز", updated: toJalali(t.updated_at ?? t.created_at),
  messages: (t.messages ?? []).map((m: any) => ({ from: m.from_support ? "support" : "me", text: m.body, time: toTime(m.created_at) })),
});
export const toTicket = (v: any) => ({ subject: v.subject, category: v.category, priority: prioApi[v.priority] ?? "medium" });

export const fromPoll = (p: any) => ({
  id: p.id, question: p.question, by: p.author?.name ?? "—", ends: toJalali(p.ends_at),
  options: (p.options ?? []).map((o: any) => ({ id: o.id, label: o.label, votes: o.votes ?? 0 })),
  myVote: p.my_vote ?? undefined,
});
export const toPoll = (v: any) => ({ question: v.question, option_labels: (v.options ?? []).map((o: any) => o.label) });

// ── Notifications (read real) + Contracts (core real) ───────────────────────
import { faMoney, faToNumber } from "./jalali";
export const fromNotification = (n: any) => ({ id: n.id, text: n.text, time: relativeFa(n.created_at), read: n.read, type: n.kind });

const cStage: Record<string, string> = { negotiation: "مذاکره", rfp: "فراخوان", evaluation: "داوری", executing: "در حال اجرا", settled: "تسویه‌شده" };
const cStageApi: Record<string, string> = { "مذاکره": "negotiation", "فراخوان": "rfp", "داوری": "evaluation", "در حال اجرا": "executing", "تسویه‌شده": "settled" };
export const fromContract = (c: any) => ({
  id: c.id, title: c.title, vendor: c.vendor, stage: cStage[c.stage] ?? "مذاکره",
  value: faMoney(c.value), deadline: toJalali(c.deadline), owner: c.owner?.name ?? "—",
});
export const toContract = (v: any) => ({ title: v.title, vendor: v.vendor, stage: cStageApi[v.stage] ?? "negotiation", value: faToNumber(v.value) });

// ── RBAC roles (admin) ──────────────────────────────────────────────────────
const rbScope: Record<string, string> = { platform: "پلتفرم", tenant: "سازمان", group: "گروه" };
const rbScopeApi: Record<string, string> = { "پلتفرم": "platform", "سازمان": "tenant", "گروه": "group" };
export const fromRole = (r: any) => ({
  id: r.id, title: r.title, scope: rbScope[r.scope] ?? "سازمان", members: r.member_count ?? 0,
  description: r.description ?? "", permissions: r.permissions ?? [], system: r.is_system,
});
export const toRole = (v: any) => ({ title: v.title, scope: rbScopeApi[v.scope] ?? "tenant", description: v.description ?? "", permissions: v.permissions ?? [] });
