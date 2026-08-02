import Link from "next/link";

export default function NotFound() {
  return (
    <main dir="rtl" className="flex min-h-screen flex-col items-center justify-center bg-ink-50 px-4 text-center">
      <p className="text-6xl font-bold text-brand-600">۴۰۴</p>
      <h1 className="mt-3 text-lg font-bold text-ink-900">صفحه یافت نشد</h1>
      <p className="mt-1 text-sm text-ink-500">نشانی‌ای که دنبالش بودید وجود ندارد یا جابه‌جا شده است.</p>
      <Link href="/dashboard" className="mt-5 rounded-lg bg-brand-600 px-4 py-2 text-sm font-medium text-white hover:bg-brand-700">
        بازگشت به داشبورد
      </Link>
    </main>
  );
}
