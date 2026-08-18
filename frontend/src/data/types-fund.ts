import type { Scoped } from "./types";

/**
 * Shared UI types (previously colocated with sample data).
 *
 * All application data now comes from /api/v1 — these are the TypeScript shapes
 * the prototype's components render against. No sample records live here.
 */

import type { NfStage } from "./constants";
export type { NfStage };

export type NfReportChainStep = {
  role: "مدیر صندوق" | "راهبر" | "ناظر";
  name: string;
  status: "تایید شده" | "در انتظار بررسی" | "نیازمند اصلاح";
  late?: boolean; // اسکالیشن: عدم بررسی در مهلت ۱۵ روزه
};

export type NfReport = {
  id: string;
  type: "مرحله‌ای" | "ماهانه" | "ماهانه تعاملات" | "نهایی";
  title: string;
  due: string;
  uploadedBy: string;
  uploadedAt?: string;
  status: "در انتظار بارگذاری" | "در حال بررسی" | "نیازمند اصلاح" | "تایید نهایی";
  chain: NfReportChainStep[];
};

export type NfPayment = {
  id: string;
  type: "پیش‌پرداخت" | "پرداخت مرحله‌ای" | "پرداخت فاز نهایی" | "حسن انجام کار";
  title: string;
  amount: string;
  status:
    | "در انتظار دستور پرداخت"
    | "دستور پرداخت صادر شد"
    | "پرداخت انجام شد"
    | "اسناد تحویل صندوق شد"
    | "اسناد به تیم مجری ارسال شد";
  orderedBy?: string;
  paidAt?: string;
  docNo?: string;
};

export type NfGuarantee = { type: string; amount: string; status: "دریافت‌شده" | "در انتظار" | "آزادشده" };

export type NfGanttRow = { title: string; weight: number; months: string; cost: string; done: number };

export type NfTimelineItem = { date: string; time: string; step: string; text: string };

export type NfRequest = {
  id: string;
  type: "تمدید ددلاین میانی" | "متمم قرارداد" | "افزایش بودجه" | "معرفی‌نامه";
  note: string;
  date: string;
  status: "در انتظار بررسی مدیر صندوق" | "تایید شده — اعمال خودکار" | "رد شده";
};

export type NfProject = {
  id: string; // کد یکتا NF-YYYY-NNNN
  titleFa: string;
  titleEn: string;
  macroField: string; // کلان محور
  field: string; // زمینه اصلی
  motherProject: string; // پروژه مادر (رویداد/فراخوان)
  team: { name: string; type: "تیم فناور" | "شرکت" | "دانشگاه یا مرکز پژوهشی"; city: string; manager: string; members: number };
  rahbar: string; // راهبر (شتاب‌دهنده)
  nazer: string; // ناظر (شخص حقیقی)
  fundManager: string;
  budget: string; // مبلغ کل (میلیون ریال)
  shareDaneshmand: number; // سهم بنیاد ٪
  durationMonths: number;
  contractNo: string;
  stage: NfStage;
  subStatus: string; // ریزوضعیت از ماشین وضعیت صندوق
  greenPath?: boolean; // مسیر سبز
  progress: number; // درصد پیشرفت تاییدشده
  finance: {
    prepayment: string;
    approvedByProgress: string; // مبلغ تاییدشده بر اساس پیشرفت
    paid: string; // پرداخت‌شده به مجری
    pending: string; // در انتظار پرداخت
    retention: string; // حسن انجام کار نزد مجری
    remaining: string; // باقی‌مانده
  };
  guarantees: NfGuarantee[];
  gantt: NfGanttRow[];
  reports: NfReport[];
  payments: NfPayment[];
  timeline: NfTimelineItem[];
  requests: NfRequest[];
} & Scoped;
