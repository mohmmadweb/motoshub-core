/**
 * Shared UI types (previously colocated with sample data).
 *
 * All application data now comes from /api/v1 — these are the TypeScript shapes
 * the prototype's components render against. No sample records live here.
 */

export type ProjectMilestone = {
  id: string;
  title: string;
  due: string;
  status: "انجام‌شده" | "در حال انجام" | "پیش‌رو" | "در خطر";
};

export type ProjectRisk = {
  id: string;
  title: string;
  severity: "کم" | "متوسط" | "بحرانی";
  probability: "کم" | "متوسط" | "زیاد";
  status: "باز" | "در حال رفع" | "بسته";
  owner: string;
  mitigation: string;
};

export type ProjectMember = {
  id: string;
  name: string;
  role: string;
  allocation: number;
  openTasks: number;
};

export type ProjectExpense = {
  id: string;
  title: string;
  category: string;
  amount: string;
  date: string;
  status: "پرداخت‌شده" | "در انتظار تأیید" | "برنامه‌ریزی‌شده";
};

export type ProjectMinute = {
  id: string;
  title: string;
  date: string;
  attendees: number;
  decisions: number;
  followUps: number;
};

export type ProjectDetail = {
  manager: string;
  sponsor: string;
  budgetTotal: string;
  budgetSpent: string;
  milestones: ProjectMilestone[];
  risks: ProjectRisk[];
  team: ProjectMember[];
  expenses: ProjectExpense[];
  minutes: ProjectMinute[];
};

export type ContractPayment = {
  id: string;
  title: string;
  amount: string;
  due: string;
  status: "پرداخت‌شده" | "در انتظار تأیید" | "آینده";
};

export type ContractObligation = {
  id: string;
  title: string;
  due: string;
  done: boolean;
};

export type ContractApproval = {
  id: string;
  role: string;
  name: string;
  status: "تأیید شده" | "در انتظار" | "رد شده";
  date?: string;
};

export type ContractEvent = { id: string; text: string; date: string };

export type ContractDetail = {
  type: "فناورانه" | "پژوهشی" | "عمرانی" | "خدماتی";
  method: "فراخوان عمومی" | "استعلام محدود" | "ترک تشریفات";
  guarantee: string;
  payments: ContractPayment[];
  obligations: ContractObligation[];
  approvals: ContractApproval[];
  history: ContractEvent[];
};

export type FundTranche = {
  id: string;
  title: string;
  amount: string;
  condition: string;
  status: "پرداخت‌شده" | "در انتظار" | "مشروط";
};

export type FundKpi = { label: string; value: string; target: string; onTrack: boolean };

export type FundDetail = {
  requested: string;
  approved: string;
  score: number;
  committee: string;
  region: string;
  field: string;
  tranches: FundTranche[];
  kpis: FundKpi[];
  notes: string;
};

export type ReviewSession = { id: string; title: string; date: string; items: number; committee: string };
export const reviewSessions: ReviewSession[] = [
  { id: "rv1", title: "جلسه داوری طرح‌های اشتغال خرد — نوبت ۱۴", date: "۱۴۰۵/۰۴/۱۸", items: 6, committee: "کارگروه اشتغال روستایی" },
  { id: "rv2", title: "بررسی طرح‌های کشاورزی نیمه اول سال", date: "۱۴۰۵/۰۴/۲۵", items: 4, committee: "کارگروه کشاورزی" },
];

// ------------------------------ Research -----------------------------------
export type ResearchApplicant = {
  id: string;
  name: string;
  affiliation: string;
  score?: number;
  status: "در بررسی" | "پذیرفته" | "رد شده";
};

export type ResearchDetail = {
  description: string;
  budget: string;
  duration: string;
  supervisor: string;
  outputs: string[];
  applicantsList: ResearchApplicant[];
  progress?: number;
};

export type SavedReport = {
  id: string;
  name: string;
  module: string;
  groupBy: string;
  schedule: "بدون زمان‌بندی" | "هفتگی" | "ماهانه";
  lastRun: string;
  format: "Excel" | "PDF" | "CSV";
};
