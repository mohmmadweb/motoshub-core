export const NF_STAGES: { key: string; label: string }[] = [
  { key: "proposal", label: "دریافت پروپوزال" },
  { key: "screening", label: "ارزیابی اولیه" },
  { key: "jury", label: "ارزیابی موشکافانه" },
  { key: "approval", label: "تصویب طرح" },
  { key: "contract", label: "تنظیم قرارداد" },
  { key: "monitoring", label: "نظارت و راهبری" },
  { key: "exit", label: "خروج از صندوق" },
];
export const stageLabel = (k: string) => NF_STAGES.find((s) => s.key === k)?.label ?? k;
