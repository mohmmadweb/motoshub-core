import type { Field } from "@/components/common/CreateForm";

const vis: Field = { name: "visibility", label: "دسترسی", type: "select", default: "private",
  options: [{ value: "private", label: "خصوصی" }, { value: "public", label: "عمومی" }] };

export const fields: Record<string, Field[]> = {
  projects: [
    { name: "name", label: "نام پروژه", required: true },
    { name: "client", label: "کارفرما" },
    { name: "health", label: "سلامت", type: "select", default: "green", options: [
      { value: "green", label: "سالم" }, { value: "yellow", label: "نیازمند توجه" }, { value: "red", label: "در خطر" }] },
    { name: "progress", label: "پیشرفت (٪)", type: "number", default: 0 },
  ],
  contracts: [
    { name: "title", label: "عنوان", required: true },
    { name: "vendor", label: "طرف قرارداد" },
    { name: "contract_type", label: "نوع", type: "select", default: "service", options: [
      { value: "tech", label: "فناورانه" }, { value: "research", label: "پژوهشی" }, { value: "construction", label: "عمرانی" }, { value: "service", label: "خدماتی" }] },
    { name: "method", label: "روش", type: "select", default: "public_call", options: [
      { value: "public_call", label: "فراخوان عمومی" }, { value: "limited", label: "استعلام محدود" }, { value: "no_tender", label: "ترک تشریفات" }] },
    { name: "value", label: "مبلغ (ریال)", type: "number", default: 0 },
  ],
  groups: [
    { name: "name", label: "نام گروه", required: true },
    { name: "description", label: "توضیح", type: "textarea" },
    { name: "privacy", label: "حریم", type: "select", default: "public", options: [
      { value: "public", label: "عمومی" }, { value: "private", label: "خصوصی" }] },
    { name: "category", label: "دسته" },
  ],
  training: [
    { name: "title", label: "عنوان دوره", required: true },
    { name: "instructor", label: "مدرس" },
    { name: "hours", label: "ساعت", type: "number", default: 0 },
    { name: "capacity", label: "ظرفیت", type: "number", default: 0 },
  ],
  research: [
    { name: "title", label: "عنوان", required: true },
    { name: "field", label: "حوزه" },
    { name: "supervisor", label: "ناظر" },
    { name: "budget", label: "بودجه (ریال)", type: "number", default: 0 },
  ],
  media: [
    { name: "title", label: "عنوان", required: true },
    { name: "album", label: "آلبوم" },
    { name: "kind", label: "نوع", type: "select", default: "photo", options: [
      { value: "photo", label: "تصویر" }, { value: "video", label: "ویدیو" }] },
    vis,
  ],
  funds: [
    { name: "code", label: "کد طرح", required: true, placeholder: "NF-1405-0001" },
    { name: "title_fa", label: "عنوان", required: true },
    { name: "field", label: "حوزه" },
    { name: "budget", label: "بودجه (ریال)", type: "number", default: 0 },
  ],
};
