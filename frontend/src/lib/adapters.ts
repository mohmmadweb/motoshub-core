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

// ── Simple Fund pipeline (FundRecord) ───────────────────────────────────────
const fStage: Record<string, string> = { registered: "ثبت‌شده", screening: "انتخاب اولیه", judging: "داوری", allocated: "تخصیص‌یافته", monitoring: "در حال پایش" };
const fStageApi: Record<string, string> = { "ثبت‌شده": "registered", "انتخاب اولیه": "screening", "داوری": "judging", "تخصیص‌یافته": "allocated", "در حال پایش": "monitoring" };
export const fromFund = (f: any) => ({ id: f.id, title: f.title, applicant: f.applicant, stage: fStage[f.stage] ?? "ثبت‌شده", amount: faMoney(f.amount), roi: f.roi ?? "" });
export const toFund = (v: any) => ({ title: v.title, applicant: v.applicant, stage: fStageApi[v.stage] ?? "registered", amount: faToNumber(v.amount), roi: v.roi });

// ── Chat (channels + messages; author carried for rendering) ────────────────
const chCat = new Set(["علاقه‌مندی‌ها", "کانال‌ها", "بایگانی‌شده"]);
export const fromChannel = (c: any) => ({
  id: c.id, name: c.name, topic: c.topic ?? "", type: c.channel_type ?? "public",
  category: chCat.has(c.category) ? c.category : "کانال‌ها", unread: 0, mentions: 0, members: c.member_count ?? 0, pinnedCount: 0,
});
export const fromChannelMessage = (m: any) => ({
  id: m.id, channelId: m.channel, authorId: m.author?.id ?? "", text: m.text, time: toTime(m.created_at), pinned: m.pinned,
  reactions: m.reactions ?? [],
  _authorName: m.author?.name ?? "—", _authorColor: m.author?.avatar_color ?? "#1f4f99",
});

// ── Users (people directory: friends / profile) ─────────────────────────────
export const fromUser = (u: any) => ({
  id: u.id,
  name: u.name,
  role: u.title ?? "",
  org: u.org ?? "",
  avatarColor: u.avatar_color ?? "#1f4f99",
  skills: Array.isArray(u.skills) ? u.skills : [],
  online: u.presence === "online",
});

// ── Rich contract sub-modules (tech-transfer / tender / e-sign) ─────────────
export const fromTechTransfer = (t: any) => ({
  id: t.id, type: t.kind, title: t.title, nazer: t.nazer, city: t.city,
  holding: t.holding, company: t.company, mojri: t.mojri, companyRole: t.company_role,
  daneshmandRole: t.daneshmand_role, amount: t.amount, commitment: t.commitment,
  physicalProgress: t.physical_progress, timeProgress: t.time_progress,
  financialProgress: t.financial_progress, guarantee: t.guarantee, note: t.note || undefined,
});

const tnMethod: Record<string, string> = { public: "مناقصه عمومی", limited: "مناقصه محدود", auction: "مزایده", no_formality: "ترک تشریفات" };
const tnStage: Record<string, string> = { publish: "انتشار آگهی", receive: "دریافت پاکات", commission: "کمیسیون معاملات", award: "ابلاغ برنده", contract: "عقد قرارداد" };
export const fromTender = (t: any) => ({
  id: t.id, title: t.title, method: tnMethod[t.method] ?? t.method, stage: tnStage[t.stage] ?? t.stage,
  participants: t.participants, sessionDate: t.session_date || undefined, winner: t.winner || undefined, note: t.note || undefined,
});

const esKind: Record<string, string> = { nf: "قرارداد صندوق نوآور", tech: "قرارداد تبادل فناوری", amendment: "متمم قرارداد", minutes: "صورت‌جلسه" };
const esStatus: Record<string, string> = { signed: "امضا شد", awaiting: "در انتظار امضا", queued: "در نوبت" };
export const fromESign = (d: any) => ({
  id: d.id, title: d.title, kind: esKind[d.kind] ?? d.kind, relatedTo: d.related_to,
  method: d.method, letterNo: d.letter_no || undefined,
  steps: (d.steps ?? []).map((s: any) => ({ role: s.role, name: s.name, status: esStatus[s.status] ?? s.status, date: s.date || undefined })),
});

// ── Innovation Fund dossier (NfProject — the richest aggregate) ──────────────
const nfStageL: Record<string, string> = { proposal: "دریافت پروپوزال", screening: "ارزیابی اولیه", jury: "ارزیابی موشکافانه", approval: "تصویب طرح", contract: "تنظیم قرارداد", monitoring: "نظارت و راهبری", exit: "خروج از صندوق" };
const nfStageApi: Record<string, string> = Object.fromEntries(Object.entries(nfStageL).map(([k, v]) => [v, k]));
const gStatus: Record<string, string> = { received: "دریافت‌شده", pending: "در انتظار", released: "آزادشده" };
const rType: Record<string, string> = { stage: "مرحله‌ای", monthly: "ماهانه", interactions: "ماهانه تعاملات", final: "نهایی" };
const rStatus: Record<string, string> = { pending_upload: "در انتظار بارگذاری", under_review: "در حال بررسی", needs_fix: "نیازمند اصلاح", approved: "تایید نهایی" };
const chRole: Record<string, string> = { fund_manager: "مدیر صندوق", rahbar: "راهبر", nazer: "ناظر" };
const chStatus: Record<string, string> = { approved: "تایید شده", pending: "در انتظار بررسی", needs_fix: "نیازمند اصلاح" };
const payStatus: Record<string, string> = { await_order: "در انتظار دستور پرداخت", ordered: "دستور پرداخت صادر شد", paid: "پرداخت انجام شد", docs_to_fund: "اسناد تحویل صندوق شد", docs_to_team: "اسناد به تیم مجری ارسال شد" };
const reqType: Record<string, string> = { extend: "تمدید ددلاین میانی", amendment: "متمم قرارداد", budget: "افزایش بودجه", letter: "معرفی‌نامه" };
const reqStatus: Record<string, string> = { pending: "در انتظار بررسی مدیر صندوق", approved: "تایید شده — اعمال خودکار", rejected: "رد شده" };

export const fromNfProject = (p: any) => ({
  id: p.code,
  titleFa: p.title_fa, titleEn: p.title_en ?? "", macroField: p.macro_field ?? "", field: p.field ?? "",
  motherProject: p.mother_project ?? "",
  team: { name: p.team_name ?? "", type: (p.team_type || "تیم فناور"), city: p.team_city ?? "", manager: p.team_manager ?? "", members: p.team_members ?? 0 },
  rahbar: p.rahbar ?? "", nazer: p.nazer ?? "", fundManager: p.fund_manager_name || "مدیر صندوق",
  budget: faMoney(p.budget), shareDaneshmand: p.share_percent ?? 0, durationMonths: p.duration_months ?? 0,
  contractNo: p.contract_no ?? "", stage: nfStageL[p.stage] ?? "دریافت پروپوزال", subStatus: p.sub_status ?? "",
  greenPath: p.green_path, progress: p.progress ?? 0,
  finance: p.finance && Object.keys(p.finance).length ? p.finance : { prepayment: "—", approvedByProgress: "—", paid: "—", pending: "—", retention: "—", remaining: "—" },
  guarantees: (p.guarantees ?? []).map((g: any) => ({ type: g.kind, amount: faMoney(g.amount), status: gStatus[g.status] ?? g.status })),
  gantt: p.gantt ?? [],
  reports: (p.reports ?? []).map((r: any) => ({
    id: r.id, type: rType[r.report_type] ?? r.report_type, title: r.title,
    due: r.due ? toJalali(r.due) : "", uploadedBy: "", uploadedAt: r.uploaded_at ? toJalali(r.uploaded_at) : undefined,
    status: rStatus[r.status] ?? r.status,
    chain: (r.chain ?? []).map((c: any) => ({ role: chRole[c.role] ?? c.role, name: c.name, status: chStatus[c.status] ?? c.status, late: c.late })),
  })),
  payments: (p.payments ?? []).map((pm: any) => ({ id: pm.id, type: pm.payment_type, title: pm.title, amount: faMoney(pm.amount), status: payStatus[pm.status] ?? pm.status, docNo: pm.doc_no || undefined })),
  timeline: p.timeline ?? [],
  requests: (p.requests ?? []).map((rq: any) => ({ id: rq.id, type: reqType[rq.request_type] ?? rq.request_type, note: rq.note, date: rq.created_at ? toJalali(rq.created_at) : "", status: reqStatus[rq.status] ?? rq.status })),
});

// Only the writable top-level fields + JSON aggregates are sent; nested children
// (guarantees/reports/payments/requests) are read-only on the serializer.
export const toNfProject = (v: any) => ({
  code: v.id, title_fa: v.titleFa, title_en: v.titleEn ?? "", macro_field: v.macroField ?? "", field: v.field ?? "",
  mother_project: v.motherProject ?? "", rahbar: v.rahbar ?? "", nazer: v.nazer ?? "",
  budget: faToNumber(v.budget), share_percent: v.shareDaneshmand ?? 0, duration_months: v.durationMonths ?? 0,
  contract_no: v.contractNo ?? "", stage: nfStageApi[v.stage] ?? "proposal", sub_status: v.subStatus ?? "",
  green_path: !!v.greenPath, progress: v.progress ?? 0,
  team_name: v.team?.name ?? "", team_type: v.team?.type ?? "", team_city: v.team?.city ?? "",
  team_manager: v.team?.manager ?? "", team_members: v.team?.members ?? 0,
  finance: v.finance ?? {}, gantt: v.gantt ?? [], timeline: v.timeline ?? [],
});

// ── Competitions + challenges ────────────────────────────────────────────────
const cpStatus: Record<string, string> = { open: "ثبت‌نام باز", judging: "در حال داوری", results: "اعلام نتایج" };
export const fromCompetition = (c: any) => ({
  id: c.id, title: c.title, category: c.category, deadline: c.deadline,
  participants: c.participants, status: cpStatus[c.status] ?? c.status, prize: c.prize,
  entries: (c.entries ?? []).map((e: any) => ({ id: e.id, by: e.by, title: e.title, votes: e.votes, color: e.color, myVote: e.my_vote })),
});

const chKind: Record<string, string> = { individual: "فردی", collective: "همگانی" };
const chStat: Record<string, string> = { active: "فعال", ended: "پایان‌یافته" };
export const fromChallenge = (c: any) => ({
  id: c.id, title: c.title, kind: chKind[c.kind] ?? c.kind, category: c.category,
  joined: c.joined, progress: c.progress ?? undefined, status: chStat[c.status] ?? c.status, isJoined: c.is_joined,
});

// ── Awards (innovation award: tracks + entries) ─────────────────────────────
const awStatus: Record<string, string> = { submitted: "ثبت‌شده", validating: "صحت‌سنجی هلدینگ", judging: "در حال داوری", scored: "امتیازدهی شده", finalist: "منتخب مرحله نهایی" };
export const fromAwardTrack = (t: any) => ({
  id: t.id, title: t.title, categories: Array.isArray(t.categories) ? t.categories : [],
  submissions: t.submission_count ?? (t.entries?.length ?? 0),
  judged: (t.entries ?? []).filter((e: any) => ["scored", "finalist"].includes(e.status)).length,
});
export const fromAwardEntry = (e: any, trackTitle = "") => ({
  id: e.id, title: e.title, track: trackTitle, company: e.company ?? "",
  status: awStatus[e.status] ?? e.status, score: e.score ?? undefined, editUsed: e.edit_used,
});

// ── Project tasks (Kanban board) ────────────────────────────────────────────
const tkStatus: Record<string, string> = { planning: "برنامه‌ریزی", in_progress: "در حال انجام", review: "بازبینی", done: "انجام‌شده" };
export const tkStatusApi: Record<string, string> = { "برنامه‌ریزی": "planning", "در حال انجام": "in_progress", "بازبینی": "review", "انجام‌شده": "done" };
const tkPrio: Record<string, string> = { low: "کم", medium: "متوسط", high: "زیاد" };
export const tkPrioApi: Record<string, string> = { "کم": "low", "متوسط": "medium", "زیاد": "high" };
export const fromTask = (t: any) => ({
  id: t.id, title: t.title, status: tkStatus[t.status] ?? "برنامه‌ریزی",
  assignee: t.assignee?.name ?? "بدون مسئول", priority: tkPrio[t.priority] ?? "متوسط",
  due: t.due ? toJalali(t.due) : "نامشخص", progress: t.progress ?? 0,
});

// ── Feed posts (dashboard / profile / group activity stream) ────────────────
export const fromPost = (p: any) => ({
  id: p.id, authorId: p.author?.id ?? "", groupId: p.group ?? undefined,
  content: p.content, time: relativeFa(p.created_at),
  likes: p.likes ?? 0, comments: p.comments ?? 0, tags: p.tags ?? [], pinned: p.pinned,
  attachment: p.attachment ?? undefined,
  _authorName: p.author?.name ?? "—", _authorColor: p.author?.avatar_color ?? "#1f4f99",
  _groupName: p.group_name ?? "", _myLike: p.my_like ?? false,
});

// ── Project milestones & risks (board tabs) ─────────────────────────────────
const msStatus: Record<string, string> = { done: "انجام‌شده", in_progress: "در حال انجام", upcoming: "پیش‌رو", at_risk: "در خطر" };
export const fromMilestone = (m: any) => ({ id: m.id, title: m.title, due: m.due || "—", status: msStatus[m.status] ?? "پیش‌رو" });
const rkSev: Record<string, string> = { low: "کم", medium: "متوسط", critical: "بحرانی" };
const rkProb: Record<string, string> = { low: "کم", medium: "متوسط", high: "زیاد" };
const rkStatus: Record<string, string> = { open: "باز", mitigating: "در حال رفع", closed: "بسته" };
export const fromRisk = (r: any) => ({
  id: r.id, title: r.title, severity: rkSev[r.severity] ?? "متوسط", probability: rkProb[r.probability] ?? "متوسط",
  status: rkStatus[r.status] ?? "باز", owner: r.owner ?? "", mitigation: r.mitigation ?? "",
});

// ── RFP calls + sabbaticals (research sub-tabs) ─────────────────────────────
const rfpStage: Record<string, string> = { publish: "انتشار فراخوان", docs: "دریافت مستندات", biz: "ارزیابی کسب‌وکاری", tech: "ارزیابی فنی", open: "بازگشایی پاکات", selected: "فناور برتر انتخاب شد" };
export const fromRfpCall = (c: any) => ({
  id: c.id, title: c.title, company: c.company, holding: c.holding,
  stage: rfpStage[c.stage] ?? c.stage, deadline: c.deadline, channels: c.channels ?? [],
  vendors: (c.vendors ?? []).map((v: any) => ({
    id: v.id, name: v.name, bizScore: v.biz_score ?? undefined, techScore: v.tech_score ?? undefined,
    priceOpened: v.price_opened, price: v.price || undefined, winner: v.winner || undefined,
  })),
});

const sabStage: Record<string, string> = { call: "فراخوان", select: "انتخاب استاد", contract: "قرارداد", running: "در حال اجرا", final: "کتابچه و ارائه نهایی", closed: "خاتمه" };
const sabRepStatus: Record<string, string> = { pending: "در انتظار", sent: "ارسال به صنعت و داور", needs_fix: "نیازمند اصلاح", paid: "تایید و پرداخت شد" };
export const fromSabbatical = (s: any) => ({
  id: s.id, professor: s.professor, university: s.university, industry: s.industry, topic: s.topic,
  trlBefore: s.trl_before, trlAfter: s.trl_after ?? undefined, contract: s.contract,
  stage: sabStage[s.stage] ?? s.stage,
  reports: (s.reports ?? []).map((r: any) => ({
    no: r.no, title: r.title, status: sabRepStatus[r.status] ?? r.status, paidAmount: r.paid_amount || undefined,
  })),
});

// ── Publications / R&D docs / registries ────────────────────────────────────
const magazine: Record<string, string> = { bonyad: "ماهنامه بنیاد", bonyadtech: "نشریه بنیادتک" };
const pubStage: Record<string, string> = { collect: "گردآوری محتوا", edit: "ویراستاری", layout: "صفحه‌آرایی", print: "چاپ و توزیع", published: "منتشر شده" };
export const fromPublication = (p: any) => ({
  id: p.id, magazine: magazine[p.magazine] ?? p.magazine, issueNo: p.issue_no,
  title: p.title, season: p.season, stage: pubStage[p.stage] ?? p.stage, articles: p.articles,
});

export const fromRndDoc = (d: any) => ({
  id: d.id, company: d.company, holding: d.holding, progress: d.progress,
  statusLabel: d.status_label, obstacles: d.obstacles || undefined,
});

export const fromSupportedProduct = (p: any) => ({ id: p.id, name: p.name, company: p.company, trl: p.trl, status: p.status });
const supportType: Record<string, string> = { tech_contract: "قرارداد فناورانه", seed: "بذرمایه", vc: "سرمایه خطرپذیر" };
export const fromSupportedVenture = (v: any) => ({ id: v.id, name: v.name, supportType: supportType[v.support_type] ?? v.support_type, field: v.field, year: v.year });
export const fromPartnerTechnologist = (t: any) => ({ id: t.id, name: t.name, expertise: t.expertise, projects: t.projects, rating: Number(t.rating) });
