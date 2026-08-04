/**
 * Shared UI types (previously colocated with sample data).
 *
 * All application data now comes from /api/v1 — these are the TypeScript shapes
 * the prototype's components render against. No sample records live here.
 */

export type Tenant = {
  id: string;
  name: string;
  domain: string;
  logoColor: string;
  plan: "پایه" | "حرفه‌ای" | "سازمانی";
  users: number;
  modules: string[];
};

export type UserProfile = {
  id: string;
  name: string;
  role: string;
  org: string;
  avatarColor: string;
  skills: string[];
  online: boolean;
};

export type Group = {
  id: string;
  name: string;
  description: string;
  members: number;
  privacy: "عمومی" | "خصوصی";
  color: string;
  unread: number;
  category: string;
  createdAt: string; // تاریخ ساخت (شمسی)
  lastActivityAt: string; // آخرین فعالیت (شمسی)
  lastActivityRel: string; // نمایش نسبی
};

export type Post = {
  id: string;
  authorId: string;
  groupId?: string;
  content: string;
  time: string;
  likes: number;
  comments: number;
  tags: string[];
  pinned?: boolean;
  attachment?: { type: "poll" | "image" | "doc"; label: string };
};

export type Visibility = "عمومی" | "خصوصی";

export type ForumTopic = {
  id: string;
  title: string;
  author: string;
  replies: number;
  views: number;
  lastActivity: string;
  category: string;
  solved?: boolean;
  visibility: Visibility;
};

export type KnowledgeDoc = {
  id: string;
  title: string;
  category: string;
  type: "قرارداد" | "آموزشی" | "صورت‌جلسه" | "گزارش";
  updatedAt: string;
  owner: string;
  size: string;
  visibility: Visibility;
};

export type Task = {
  id: string;
  title: string;
  status: "برنامه‌ریزی" | "در حال انجام" | "بازبینی" | "انجام‌شده";
  assignee: string;
  priority: "کم" | "متوسط" | "زیاد";
  due: string;
  progress: number;
};

export type Project = {
  id: string;
  name: string;
  client: string;
  health: "سبز" | "زرد" | "قرمز";
  progress: number;
  budgetUsed: number;
  deadline: string;
  tasks: Task[];
};

export type Notification = {
  id: string;
  text: string;
  time: string;
  read: boolean;
  type: "mention" | "like" | "comment" | "system" | "task";
};

export type ChatThread = {
  id: string;
  with: string;
  avatarColor: string;
  lastMessage: string;
  time: string;
  unread: number;
  online?: boolean;
  messages: { from: "me" | "them"; text: string; time: string; read?: boolean }[];
};

export type EventItem = {
  id: string;
  title: string;
  date: string;
  jalaliDate: string;
  time: string;
  location: string;
  attendees: number;
  hashtags: string[];
  description: string;
  visibility: Visibility;
  mode: "حضوری" | "آنلاین";
  joinLink?: string;
  mapUrl?: string;
};

export type BlogPost = {
  id: string;
  title: string;
  author: string;
  excerpt: string;
  date: string;
  rating: number;
  tags: string[];
  visibility: Visibility;
};

export type MediaItem = {
  id: string;
  kind: "photo" | "video";
  title: string;
  album: string;
  uploadedBy: string;
  date: string;
  rating: number;
  tags: string[];
  color: string;
  visibility: Visibility;
};

export type NewsItem = {
  id: string;
  title: string;
  summary: string;
  date: string;
  comments: number;
  views: number;
  pinned?: boolean;
  visibility: Visibility;
};

export type SessionItem = {
  id: string;
  device: string;
  location: string;
  ip: string;
  lastActive: string;
  current?: boolean;
};

export type ContractRecord = {
  id: string;
  title: string;
  vendor: string;
  stage: "مذاکره" | "فراخوان" | "داوری" | "در حال اجرا" | "تسویه‌شده";
  value: string;
  deadline: string;
  owner: string;
};

export type FundRecord = {
  id: string;
  title: string;
  applicant: string;
  stage: "ثبت‌شده" | "انتخاب اولیه" | "داوری" | "تخصیص‌یافته" | "در حال پایش";
  amount: string;
  roi: string;
};

export type ResearchOpportunity = {
  id: string;
  title: string;
  field: string;
  stage: "فراخوان باز" | "بررسی درخواست‌ها" | "داوری" | "در حال اجرا" | "پایان‌یافته";
  applicants: number;
  deadline: string;
};

export type ModuleDef = {
  id: string;
  name: string;
  description: string;
  category: "اجتماعی" | "دانش و پروژه" | "امنیت" | "زیرساخت";
  core?: boolean;
};

export type AdminPageDef = { id: string; title: string; slug: string; visible: boolean };
export const adminPages: AdminPageDef[] = [
  { id: "pg1", title: "درباره ما", slug: "/about", visible: true },
  { id: "pg2", title: "قوانین و مقررات", slug: "/terms", visible: true },
  { id: "pg3", title: "تماس با ما", slug: "/contact", visible: true },
  { id: "pg4", title: "سوالات متداول", slug: "/faq", visible: false },
];

export type AdminMenuDef = { id: string; title: string; order: number; visible: boolean };
export const adminMenus: AdminMenuDef[] = [
  { id: "mn1", title: "داشبورد", order: 1, visible: true },
  { id: "mn2", title: "گروه‌ها", order: 2, visible: true },
  { id: "mn3", title: "مدیریت دانش", order: 3, visible: true },
  { id: "mn4", title: "مدیریت پروژه", order: 4, visible: true },
  { id: "mn5", title: "طرح‌های اشتغال‌زایی", order: 5, visible: false },
];

// ---------------------------------------------------------------------------
// Roles & granular permissions (custom roles)
// ---------------------------------------------------------------------------
export type PermissionGroup = {
  id: string;
  label: string;
  actions: { id: string; label: string }[];
};

export type RoleDef = {
  id: string;
  title: string;
  scope: "پلتفرم" | "سازمان" | "گروه";
  members: number;
  description: string;
  permissions: string[];
  system?: boolean;
};

export type RoleAssignment = Record<string, string>;

export type SearchResult = { id: string; type: "پست" | "گروه" | "سند" | "پروژه" | "کاربر"; title: string; snippet: string };
export const searchResults: SearchResult[] = [
  { id: "sr1", type: "سند", title: "چارچوب حقوقی واگذاری هتل‌ها و اموال مازاد بنیاد", snippet: "آرشیو قراردادها · بروزرسانی ۱۴۰۵/۰۲/۰۱" },
  { id: "sr2", type: "پروژه", title: "طرح آبادانی و پیشرفت قلعه‌گنج — فاز دوم", snippet: "کارفرما: بنیاد علوی · پیشرفت ۷۰٪" },
  { id: "sr3", type: "گروه", title: "ستاد محرومیت‌زدایی", snippet: "۱۸ عضو · خصوصی" },
  { id: "sr4", type: "پست", title: "گزارش پیشرفت طرح‌های آبادانی قلعه‌گنج بارگذاری شد", snippet: "۱۲ پسندیدن · ۳ نظر" },
  { id: "sr5", type: "کاربر", title: "محسن مردعلی", snippet: "قائم‌مقام بنیاد علوی · بنیاد علوی" },
];

// ---------------------------------------------------------------------------
// Internal communication workspace (Mattermost-inspired) — channels, presence,
// threads, reactions, pinned/saved messages. Distinct from "Groups": Groups
// are community/social (public browsing, posts, likes, forum-per-group);
// Channels are the internal team-communication workspace (sidebar categories,
// threaded replies, slash commands, integrations).
// ---------------------------------------------------------------------------
export type PresenceStatus = "online" | "away" | "dnd" | "offline";

export const userPresence: Record<string, PresenceStatus> = {
  u1: "online",
  u2: "dnd",
  u3: "offline",
  u4: "away",
  u5: "online",
  u6: "online",
  u7: "online",
  u8: "offline",
  u9: "online",
  u10: "online",
  u11: "away",
  u12: "online",
  u13: "dnd",
};

export type Channel = {
  id: string;
  name: string;
  topic: string;
  type: "public" | "private";
  category: "علاقه‌مندی‌ها" | "کانال‌ها" | "بایگانی‌شده";
  unread: number;
  mentions: number;
  members: number;
  pinnedCount: number;
};

export type ReactionIcon = "ThumbsUp" | "Heart" | "Smile" | "CheckCircle2";

export type Reaction = { icon: ReactionIcon; count: number; reactedByMe?: boolean };

export type ChannelMessage = {
  id: string;
  channelId: string;
  authorId: string;
  text: string;
  time: string;
  pinned?: boolean;
  saved?: boolean;
  reactions?: Reaction[];
  threadReplies?: number;
};

export type Integration = {
  id: string;
  name: string;
  type: "وب‌هوک ورودی" | "وب‌هوک خروجی" | "بات" | "دستور اسلش";
  channel: string;
  status: "فعال" | "غیرفعال";
  createdBy: string;
};

export type GuestAccount = { id: string; name: string; org: string; channels: string[]; expires: string };
export type PlaybookTemplate = { id: string; name: string; category: string; steps: number; usedCount: number };
