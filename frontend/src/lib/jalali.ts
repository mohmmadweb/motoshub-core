// Minimal, dependency-free Gregorian → Jalali conversion + Persian formatting.
const FA = "۰۱۲۳۴۵۶۷۸۹";
export const toFaDigits = (s: string | number) => String(s).replace(/[0-9]/g, (d) => FA[+d]);

function gregToJalali(gy: number, gm: number, gd: number): [number, number, number] {
  const gdm = [0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334];
  let jy = gy <= 1600 ? 0 : 979;
  gy -= gy <= 1600 ? 621 : 1600;
  const gy2 = gm > 2 ? gy + 1 : gy;
  let days = 365 * gy + Math.floor((gy2 + 3) / 4) - Math.floor((gy2 + 99) / 100) + Math.floor((gy2 + 399) / 400) - 80 + gd + gdm[gm - 1];
  jy += 33 * Math.floor(days / 12053);
  days %= 12053;
  jy += 4 * Math.floor(days / 1461);
  days %= 1461;
  jy += Math.floor((days - 1) / 365);
  if (days > 365) days = (days - 1) % 365;
  const jm = days < 186 ? 1 + Math.floor(days / 31) : 7 + Math.floor((days - 186) / 30);
  const jd = 1 + (days < 186 ? days % 31 : (days - 186) % 30);
  return [jy, jm, jd];
}

export function toJalali(iso: string | null | undefined): string {
  if (!iso) return "";
  const d = new Date(iso);
  if (isNaN(d.getTime())) return "";
  const [jy, jm, jd] = gregToJalali(d.getFullYear(), d.getMonth() + 1, d.getDate());
  return toFaDigits(`${jy}/${String(jm).padStart(2, "0")}/${String(jd).padStart(2, "0")}`);
}

export function toTime(iso: string | null | undefined): string {
  if (!iso) return "";
  const d = new Date(iso);
  return toFaDigits(`${String(d.getHours()).padStart(2, "0")}:${String(d.getMinutes()).padStart(2, "0")}`);
}

export function relativeFa(iso: string | null | undefined): string {
  if (!iso) return "";
  const diff = (Date.now() - new Date(iso).getTime()) / 1000;
  if (diff < 60) return "چند لحظه پیش";
  if (diff < 3600) return `${toFaDigits(Math.floor(diff / 60))} دقیقه پیش`;
  if (diff < 86400) return `${toFaDigits(Math.floor(diff / 3600))} ساعت پیش`;
  if (diff < 2592000) return `${toFaDigits(Math.floor(diff / 86400))} روز پیش`;
  return toJalali(iso);
}

export const visToFa = (v: string) => (v === "public" ? "عمومی" : "خصوصی");
export const visToApi = (v: string) => (v === "عمومی" ? "public" : "private");

export const faMoney = (n: number | string) => `${Number(n || 0).toLocaleString("fa-IR")} ریال`;
export const faToNumber = (s: string | number): number => {
  if (typeof s === "number") return s;
  const latin = String(s).replace(/[۰-۹]/g, (d) => String("۰۱۲۳۴۵۶۷۸۹".indexOf(d)));
  return Number(latin.replace(/[^0-9.]/g, "")) || 0;
};

/**
 * A Jalali date string as a sortable/comparable integer: ۱۴۰۵/۰۵/۱۳ → 14050513.
 * Persian digits are accepted, since that is how dates travel through the UI.
 */
export const jalaliKey = (jalali: string): number => {
  const [y, m, d] = (jalali || "").split("/").map(faToNumber);
  return (y || 0) * 10000 + (m || 0) * 100 + (d || 0);
};

/** Today's Jalali date in the same integer form — the real today, not a fixed one. */
export const todayJalaliKey = (): number => jalaliKey(toJalali(new Date().toISOString()));
