import { useCallback, useEffect, useState } from "react";
import { fromTicket, tPrioApi } from "../lib/adapters";
import { http, apiMessage } from "../lib/http";
import { LifeBuoy, Plus, Send, Clock3, CheckCircle2, MessageSquareText, RotateCcw, Pencil, Trash2, X } from "lucide-react";
import PageHeader from "../components/ui/PageHeader";
import Badge, { type BadgeTone } from "../components/ui/Badge";
import Button from "../components/ui/Button";
import Modal from "../components/ui/Modal";
import Drawer from "../components/ui/Drawer";
import DataTable, { type Column } from "../components/ui/DataTable";
import { useToast } from "../components/ui/ToastProvider";
import { useConfirm } from "../components/ui/ConfirmProvider";

// تیکت پشتیبانی — معادل iisticketing (تیکت + دسته + پاسخ‌گویی)
type TicketMsg = { id: string; from: "me" | "support"; text: string; time: string };
type Ticket = {
  id: string;
  no: string;
  subject: string;
  category: string;
  priority: "کم" | "متوسط" | "فوری";
  status: "باز" | "در حال بررسی" | "پاسخ داده شد" | "بسته";
  updated: string;
  messages: TicketMsg[];
};

const categories = ["فنی و سامانه", "دسترسی و نقش‌ها", "مالی و پرداخت", "پیشنهاد و انتقاد"];

const statusTone: Record<Ticket["status"], BadgeTone> = { باز: "brand", "در حال بررسی": "warning", "پاسخ داده شد": "success", بسته: "neutral" };
const prioTone: Record<Ticket["priority"], BadgeTone> = { کم: "neutral", متوسط: "warning", فوری: "danger" };

export default function Tickets() {
  const [tickets, setTickets] = useState<Ticket[]>([]);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [open, setOpen] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [subject, setSubject] = useState("");
  const [category, setCategory] = useState(categories[0]);
  const [priority, setPriority] = useState<Ticket["priority"]>("متوسط");
  const [body, setBody] = useState("");
  const [reply, setReply] = useState("");
  const { notify } = useToast();
  const confirm = useConfirm();

  const load = useCallback(
    () => http<any[]>("/tickets?page_size=100").then((rows) => setTickets(rows.map(fromTicket) as Ticket[])),
    []
  );
  useEffect(() => { load().catch(() => {}); }, [load]);

  // Read the open ticket out of the list so the drawer always shows the state
  // the server last confirmed, rather than a copy that drifts from it.
  const selected = tickets.find((t) => t.id === selectedId) ?? null;
  const openCount = tickets.filter((t) => t.status === "باز" || t.status === "در حال بررسی").length;

  const openModal = (t?: Ticket) => {
    if (t) {
      setEditingId(t.id);
      setSubject(t.subject);
      setCategory(t.category || categories[0]);
      setPriority(t.priority);
      setBody("");
    } else {
      setEditingId(null);
      setSubject("");
      setCategory(categories[0]);
      setPriority("متوسط");
      setBody("");
    }
    setOpen(true);
  };

  const submit = async () => {
    if (!subject.trim() || (!editingId && !body.trim())) {
      notify("موضوع و شرح تیکت الزامی است.", "warning");
      return;
    }
    try {
      if (editingId) {
        await http(`/tickets/${editingId}`, {
          method: "PATCH",
          body: JSON.stringify({ subject: subject.trim(), category, priority: tPrioApi[priority] ?? "medium" }),
        });
        notify("تیکت ویرایش شد.");
      } else {
        const t = await http<any>("/tickets", {
          method: "POST",
          body: JSON.stringify({ subject: subject.trim(), category, priority: tPrioApi[priority] ?? "medium", body: body.trim() }),
        });
        notify(`تیکت «${t.number}» ثبت شد؛ پاسخ از طریق اعلان به شما اطلاع داده می‌شود.`);
      }
      await load();
      setOpen(false);
      setEditingId(null);
      setSubject("");
      setBody("");
    } catch (err) {
      notify(apiMessage(err, "ثبت تیکت ناموفق بود."), "warning");
    }
  };

  const removeTicket = (t: Ticket) =>
    confirm({
      title: `حذف تیکت «${t.no}»؟`,
      message: "کل گفتگوی این تیکت حذف می‌شود و قابل بازیابی نیست.",
      onConfirm: async () => {
        try {
          await http(`/tickets/${t.id}`, { method: "DELETE" });
          await load();
          setSelectedId(null);
          notify("تیکت حذف شد.", "info");
        } catch (err) {
          notify(apiMessage(err, "حذف تیکت ناموفق بود."), "warning");
        }
      },
    });

  const sendReply = async () => {
    if (!reply.trim() || !selected) return;
    try {
      await http(`/tickets/${selected.id}/reply`, { method: "POST", body: JSON.stringify({ body: reply.trim() }) });
      await load();
      setReply("");
      notify("پاسخ شما ثبت شد.");
    } catch (err) {
      notify(apiMessage(err, "ثبت پاسخ ناموفق بود."), "warning");
    }
  };

  const removeMessage = (m: TicketMsg) =>
    confirm({
      title: "حذف این پیام؟",
      message: "پیام از گفتگوی تیکت حذف می‌شود.",
      onConfirm: async () => {
        if (!selected) return;
        try {
          await http(`/tickets/${selected.id}/messages/${m.id}`, { method: "DELETE" });
          await load();
          notify("پیام حذف شد.", "info");
        } catch (err) {
          notify(apiMessage(err, "حذف پیام ناموفق بود."), "warning");
        }
      },
    });

  const setTicketState = async (action: "close" | "reopen") => {
    if (!selected) return;
    try {
      await http(`/tickets/${selected.id}/${action}`, { method: "POST" });
      await load();
      notify(
        action === "close" ? "تیکت بسته شد. در صورت نیاز می‌توانید تیکت جدیدی ثبت کنید." : "تیکت دوباره باز شد.",
        "info"
      );
    } catch (err) {
      notify(apiMessage(err, "تغییر وضعیت تیکت ناموفق بود."), "warning");
    }
  };

  const columns: Column<Ticket>[] = [
    { key: "no", label: "شماره", render: (t) => <span className="font-mono text-[11px] text-ink-700" dir="ltr">{t.no}</span> },
    { key: "subject", label: "موضوع", render: (t) => <span className="font-medium text-ink-900">{t.subject}</span> },
    { key: "category", label: "دسته" },
    { key: "priority", label: "اولویت", render: (t) => <Badge tone={prioTone[t.priority]}>{t.priority}</Badge> },
    { key: "status", label: "وضعیت", render: (t) => <Badge tone={statusTone[t.status]}>{t.status}</Badge> },
    { key: "updated", label: "آخرین به‌روزرسانی" },
  ];

  return (
    <div>
      <PageHeader
        title="تیکت پشتیبانی"
        description={`ثبت و پیگیری درخواست‌های پشتیبانی — ${openCount.toLocaleString("fa-IR")} تیکت باز`}
        icon={<LifeBuoy size={18} />}
        actions={
          <Button variant="primary" icon={<Plus size={15} />} onClick={() => openModal()}>تیکت جدید</Button>
        }
      />

      <DataTable
        columns={columns}
        rows={tickets}
        searchKeys={["subject", "no"]}
        searchPlaceholder="جستجو در موضوع یا شماره تیکت…"
        onRowClick={(t) => setSelectedId(t.id)}
      />

      <Modal open={open} onClose={() => setOpen(false)} title={editingId ? "ویرایش تیکت" : "ثبت تیکت پشتیبانی جدید"}>
        <div className="space-y-3">
          <div>
            <label className="text-xs font-medium text-ink-600 block mb-1.5">موضوع <span className="text-rose-500">*</span></label>
            <input value={subject} onChange={(e) => setSubject(e.target.value)} placeholder="خلاصه‌ی یک‌خطی مشکل یا درخواست" className="input-field" />
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="text-xs font-medium text-ink-600 block mb-1.5">دسته</label>
              <select value={category} onChange={(e) => setCategory(e.target.value)} className="input-field">
                {categories.map((c) => <option key={c}>{c}</option>)}
                {/* A ticket filed from elsewhere (e.g. گزارش تخلف) keeps its own category. */}
                {category && !categories.includes(category) && <option>{category}</option>}
              </select>
            </div>
            <div>
              <label className="text-xs font-medium text-ink-600 block mb-1.5">اولویت</label>
              <select value={priority} onChange={(e) => setPriority(e.target.value as Ticket["priority"])} className="input-field">
                <option>کم</option><option>متوسط</option><option>فوری</option>
              </select>
            </div>
          </div>
          {!editingId && (
            <div>
              <label className="text-xs font-medium text-ink-600 block mb-1.5">شرح کامل <span className="text-rose-500">*</span></label>
              <textarea value={body} onChange={(e) => setBody(e.target.value)} className="input-field min-h-24" placeholder="جزئیات، مراحل بازتولید مشکل، اسکرین‌شات…" />
            </div>
          )}
          <div className="flex items-center gap-2 pt-2">
            <Button variant="primary" className="flex-1 justify-center" onClick={submit}>{editingId ? "ذخیره تغییرات" : "ثبت تیکت"}</Button>
            <Button variant="secondary" onClick={() => setOpen(false)}>انصراف</Button>
          </div>
        </div>
      </Modal>

      <Drawer open={selected !== null} onClose={() => setSelectedId(null)} title={selected ? `تیکت ${selected.no}` : ""}>
        {selected && (
          <div className="flex flex-col h-full">
            <div className="pb-3 border-b border-ink-100">
              <div className="flex items-start justify-between gap-2">
                <p className="text-sm font-bold text-ink-900 leading-6">{selected.subject}</p>
                <div className="flex items-center gap-1 shrink-0">
                  <button onClick={() => openModal(selected)} className="p-1.5 rounded-md text-ink-400 hover:text-brand-600 hover:bg-ink-50" title="ویرایش تیکت">
                    <Pencil size={14} />
                  </button>
                  <button onClick={() => removeTicket(selected)} className="p-1.5 rounded-md text-ink-400 hover:text-rose-600 hover:bg-rose-50" title="حذف تیکت">
                    <Trash2 size={14} />
                  </button>
                </div>
              </div>
              <div className="flex items-center gap-2 mt-2 flex-wrap">
                <Badge tone={statusTone[selected.status]}>{selected.status}</Badge>
                <Badge tone={prioTone[selected.priority]}>{selected.priority}</Badge>
                <Badge tone="neutral">{selected.category}</Badge>
              </div>
            </div>
            <div className="flex-1 overflow-y-auto py-4 space-y-3">
              {selected.messages.map((m) => (
                <div key={m.id} className={`group flex items-center gap-1 ${m.from === "me" ? "justify-start" : "justify-end"}`}>
                  {m.from === "me" && (
                    <button
                      onClick={() => removeMessage(m)}
                      className="opacity-0 group-hover:opacity-100 p-1 text-ink-300 hover:text-rose-600 transition-opacity"
                      title="حذف پیام"
                    >
                      <X size={12} />
                    </button>
                  )}
                  <div className={`max-w-[85%] rounded-xl px-3 py-2 text-[12.5px] leading-6 ${m.from === "me" ? "bg-brand-600 text-white" : "bg-ink-50 border border-ink-100 text-ink-800"}`}>
                    {m.from === "support" && <p className="text-[10.5px] font-bold text-brand-600 mb-0.5 flex items-center gap-1"><MessageSquareText size={11} /> پشتیبانی</p>}
                    <p>{m.text}</p>
                    <p className={`text-[10px] mt-1 flex items-center gap-1 ${m.from === "me" ? "text-white/70" : "text-ink-400"}`}><Clock3 size={10} /> {m.time}</p>
                  </div>
                </div>
              ))}
            </div>
            {selected.status !== "بسته" ? (
              <div className="pt-3 border-t border-ink-100 space-y-2">
                <div className="flex items-center gap-2">
                  <input
                    value={reply}
                    onChange={(e) => setReply(e.target.value)}
                    onKeyDown={(e) => e.key === "Enter" && sendReply()}
                    placeholder="پاسخ خود را بنویسید…"
                    className="input-field flex-1"
                  />
                  <Button variant="primary" icon={<Send size={14} />} onClick={sendReply}>ارسال</Button>
                </div>
                <button onClick={() => setTicketState("close")} className="text-[11.5px] text-ink-500 hover:text-emerald-600 flex items-center gap-1.5">
                  <CheckCircle2 size={13} /> مشکل حل شد — بستن تیکت
                </button>
              </div>
            ) : (
              <div className="pt-3 border-t border-ink-100 flex items-center justify-between gap-2">
                <p className="text-[11.5px] text-ink-400">این تیکت بسته شده است.</p>
                <Button variant="secondary" size="sm" icon={<RotateCcw size={13} />} onClick={() => setTicketState("reopen")}>
                  بازگشایی تیکت
                </Button>
              </div>
            )}
          </div>
        )}
      </Drawer>
    </div>
  );
}
