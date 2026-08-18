import type { Scoped } from "./types";

/**
 * Shared UI types (previously colocated with sample data).
 *
 * All application data now comes from /api/v1 — these are the TypeScript shapes
 * the prototype's components render against. No sample records live here.
 */

export type SubCompany = { id: string; name: string };
export type Holding = { id: string; name: string; color: string; companies: SubCompany[] };

export type ContentScope = "سراسری" | "هلدینگ" | "شرکت";

// دامنه انتشار محتوای شرکتی: خبر با scope «شرکت» فقط برای اعضای همان شرکت،
// «هلدینگ» برای همه شرکت‌های آن هلدینگ و «سراسری» برای کل مجموعه نمایش داده می‌شود.
export type ScopedNews = {
  id: string;
  title: string;
  summary: string;
  date: string;
  scope: ContentScope;
  holdingId?: string;
  companyId?: string;
};

export type TechTransferContract = {
  id: string;
  type: string; // نوع قرارداد
  title: string;
  nazer: string; // ناظر فنی پروژه
  city: string;
  holding: string; // هلدینگ متقاضی
  company: string; // شرکت متقاضی
  mojri: string; // مجری پروژه
  companyRole: string; // نقش شرکت متقاضی
  daneshmandRole: string; // نقش بنیاد
  amount: string; // مبلغ قرارداد
  commitment: string; // تعهد بنیاد
  physicalProgress: number; // درصد پیشرفت فیزیکی
  timeProgress: number; // درصد پیشرفت زمانی
  financialProgress: number; // درصد پیشرفت مالی
  guarantee: string;
  note?: string;
};

export type RndOpportunityDoc = {
  id: string;
  company: string;
  holding: string;
  progress: number; // ۰ تا ۱۰۰
  statusLabel: string;
  obstacles?: string;
};

export type AwardTrack = {
  id: string;
  title: string;
  categories: string[];
  submissions: number;
  judged: number;
};

export type AwardEntry = {
  id: string;
  title: string;
  track: string;
  company: string;
  status: "ثبت‌شده" | "صحت‌سنجی هلدینگ" | "در حال داوری" | "امتیازدهی شده" | "منتخب مرحله نهایی";
  score?: number;
  editUsed: boolean; // یک بار امکان ویرایش
};

export type TrainingCourse = {
  id: string;
  title: string;
  instructor: string;
  date: string;
  hours: number;
  capacity: number;
  enrolled: number;
  status: "ثبت‌نام باز" | "در حال برگزاری" | "برگزار شده";
  attendanceRate?: number; // درصد حضور
  satisfaction?: number; // ارزشیابی از ۵
  effectiveness?: "در انتظار سنجش" | "اثربخش" | "نیازمند دوره تکمیلی";
  certificates?: number; // گواهینامه صادرشده
} & Scoped;

export type SignatureStep = {
  role: string;
  name: string;
  status: "امضا شد" | "در انتظار امضا" | "در نوبت";
  date?: string;
};

export type ESignDocument = {
  id: string;
  title: string;
  kind: "قرارداد صندوق نوآور" | "قرارداد تبادل فناوری" | "متمم قرارداد" | "صورت‌جلسه";
  relatedTo: string;
  method: "امضای الکترونیک غیرحضوری";
  steps: SignatureStep[];
  letterNo?: string; // شماره نامه پس از تکمیل امضاها
};

export type ScreeningForm = {
  total: number; // از ۲۰۰
  threshold: number; // حد نصاب ۸۰
  topCriteria: { title: string; max: number; score: number }[]; // منتخب از ۲۲ معیار
};

export type JuryForm = {
  total: number; // از ۱۰۰
  threshold: number; // حد نصاب ~۵۰
  dimensions: { title: string; max: number; score: number }[]; // ۵ بُعد
};

export type AssistantExchange = { q: string; a: string };

// ------------------- کاتالوگ صندوق‌های سرمایه‌گذاری بنیاد -------------------
export type FundEntity = {
  id: string;
  name: string;
  focus: string;
  trlRange: string;
  manager: string;
  activeProjects: number;
  capital: string;
};

export type SeedInvestment = {
  id: string;
  startup: string;
  field: string;
  stage: "غربالگری" | "ارزیابی" | "ارزیابی موشکافانه" | "قرارداد" | "نظارت و راهبری" | "خروج";
  requested: string;
  approved?: string;
  equityPercent?: number;
  valuation?: string;
  kpiStatus?: string;
  exitPlan?: string;
};

export type RfpVendor = {
  id: string;
  name: string;
  bizScore?: number; // نمره کسب‌وکاری (از ۱۰۰)
  techScore?: number; // نمره فنی (از ۱۰۰)
  priceOpened?: boolean;
  price?: string;
  winner?: boolean;
};

export type RfpCall = {
  id: string;
  title: string;
  company: string;
  holding: string;
  stage: "انتشار فراخوان" | "دریافت مستندات" | "ارزیابی کسب‌وکاری" | "ارزیابی فنی" | "بازگشایی پاکات" | "فناور برتر انتخاب شد";
  deadline: string;
  vendors: RfpVendor[];
  channels: string[]; // محل‌های انتشار
};

export type SabbaticalReport = {
  no: 1 | 2 | 3;
  title: string;
  status: "در انتظار" | "ارسال به صنعت و داور" | "نیازمند اصلاح" | "تایید و پرداخت شد";
  paidAmount?: string;
};

export type Sabbatical = {
  id: string;
  professor: string;
  university: string;
  industry: string; // شرکت صنعتی میزبان
  topic: string;
  trlBefore: number;
  trlAfter?: number;
  contract: string;
  reports: SabbaticalReport[]; // ۳ گزارش: شناخت / راهکار / RFPها
  stage: "فراخوان" | "انتخاب استاد" | "قرارداد" | "در حال اجرا" | "کتابچه و ارائه نهایی" | "خاتمه";
};

export type TenderRecord = {
  id: string;
  title: string;
  method: "مناقصه عمومی" | "مناقصه محدود" | "مزایده" | "ترک تشریفات";
  stage: "انتشار آگهی" | "دریافت پاکات" | "کمیسیون معاملات" | "ابلاغ برنده" | "عقد قرارداد";
  participants: number;
  sessionDate?: string;
  winner?: string;
  note?: string;
};

export type PublicationIssue = {
  id: string;
  magazine: "ماهنامه بنیاد" | "نشریه بنیادتک";
  issueNo: number;
  title: string;
  season: string;
  stage: "گردآوری محتوا" | "ویراستاری" | "صفحه‌آرایی" | "چاپ و توزیع" | "منتشر شده";
  articles: number;
};

export type SupportedProduct = { id: string; name: string; company: string; trl: number; status: string };

export type SupportedVenture = { id: string; name: string; supportType: "قرارداد فناورانه" | "بذرمایه" | "سرمایه خطرپذیر"; field: string; year: string };

export type PartnerTechnologist = { id: string; name: string; expertise: string; projects: number; rating: number };

// ------------------- طرح‌های در دست بررسی (شیت کنترل پروژه) -------------------
export type PendingReviewItem = { id: string; topic: string; holding: string; company: string; mojri?: string; obstacles?: string; note?: string };

// ------------------- ریزوضعیت‌های هر گام صندوق نوآور (شیت Statuses) -------------------
export const nfSubStatuses: Record<string, string[]> = {
  "دریافت پروپوزال": [
    "دریافت طرح، تخصیص کد یکتا و ایجاد شناسنامه",
    "بررسی مستندات و اعلام اصلاحات — در انتظار طرح اصلاح‌شده",
    "دریافت طرح اصلاح‌شده",
    "تایید شکلی و ارجاع به کارشناس",
  ],
  "ارزیابی اولیه": [
    "اجرای پرامپت ارزیابی اولیه و آماده شدن گزارش",
    "نیاز به جلسه — در حال هماهنگی",
    "جلسه برگزار شد",
    "نیاز به اصلاح طرح",
    "مغایرت TRL با هدف صندوق — ارجاع به کمیته سرمایه‌گذاری",
    "کسب حد نصاب — ارسال به ارزیابی موشکافانه",
    "رد درخواست",
  ],
  "ارزیابی موشکافانه": [
    "در حال تعیین تیم داوری/راهبری/ناظر",
    "ارسال به داوران — تحت بررسی",
    "یادآوری به داور دارای تاخیر",
    "دریافت نتیجه تمامی داوران و جمع‌بندی",
    "ارسال گزارش به کارگروه ارزیابی صندوق",
    "نیاز به اصلاح",
    "تایید و آماده تصویب",
  ],
  "تصویب طرح": [
    "در دستور جلسه شورای راهبری",
    "تایید شورا — در دستور جلسه هیئت مدیره",
    "نیاز به اصلاح از نظر هیئت مدیره",
    "تصویب در هیئت مدیره",
    "رد در شورا/هیئت مدیره",
  ],
  "تنظیم قرارداد": [
    "تعیین تیپ قرارداد و ارسال به مجری",
    "در انتظار مشخصات از مجری/راهبر",
    "قرارداد تنظیم شد",
    "ارسال غیرحضوری برای امضای الکترونیکی — در انتظار امضای مجری",
    "امضای راهبر و صاحبین امضا",
    "همه امضاها اخذ شد — در انتظار شماره نامه",
    "تخصیص شماره و تحویل نسخه‌ها",
  ],
  "نظارت و راهبری": [
    "نیاز به پیش‌پرداخت — در انتظار تضامین",
    "تضامین دریافت شد — در انتظار دستور پرداخت پیش‌پرداخت",
    "دریافت گزارش پیشرفت و صورت‌وضعیت",
    "بررسی پیشرفت نیازمند جلسه دفاع",
    "گزارش نیازمند اصلاح",
    "گزارش مورد تایید صندوق — در انتظار دستور پرداخت",
    "دستور پرداخت صادر شد — در انتظار پرداخت واحد مالی",
    "پرداخت انجام شد — اسناد در جریان",
    "دریافت گزارش پیشرفت ماهانه اعضای تیم",
    "پایان زمان و نیاز به متمم قرارداد",
    "صدور معرفی‌نامه برای تیم مجری",
  ],
  "خروج از صندوق": [
    "تحویل گزارش نهایی مورد تایید راهبر",
    "جلسه دفاع اختتام",
    "صورت‌مجلس پایان پروژه",
    "پرداخت فاز نهایی — اسناد در جریان",
    "در انتظار آزادسازی حسن انجام کار",
    "جانمایی تیم در رویداد سرمایه‌گذاری",
    "ورود تیم به فاز شتابدهی / فروش محصول",
    "پروژه خاتمه یافته",
    "لغو در فازهای میانی",
  ],
};
