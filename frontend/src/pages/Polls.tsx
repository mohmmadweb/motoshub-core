import { useEffect, useState } from "react";
import { useApiCollection } from "../lib/useApiCollection";
import { fromPoll, toPoll, fromQuiz, qzStatusApi } from "../lib/adapters";
import { http, apiMessage } from "../lib/http";
import { ListChecks, Plus, Timer, FileQuestion, CheckCircle2 } from "lucide-react";
import PageHeader from "../components/ui/PageHeader";
import Badge, { type BadgeTone } from "../components/ui/Badge";
import Button from "../components/ui/Button";
import Tabs from "../components/ui/Tabs";
import Modal from "../components/ui/Modal";
import RowActions from "../components/ui/RowActions";
import EmptyState from "../components/ui/EmptyState";
import { useToast } from "../components/ui/ToastProvider";
import { useConfirm } from "../components/ui/ConfirmProvider";
import { useTabParam } from "../lib/useTabParam";

// نظرسنجی (iisquestions/Poll) + آزمون و داوری (iispors/Quiz)
type Poll = {
  id: string;
  question: string;
  by: string;
  ends: string;
  options: { id: string; label: string; votes: number }[];
  myVote?: string;
};

type Quiz = {
  id: string;
  title: string;
  questions: number;
  minutes: number;
  deadline: string;
  status: "باز" | "در حال داوری" | "پایان‌یافته";
  myScore?: number;
  passing: number;
};

const quizTone: Record<Quiz["status"], BadgeTone> = { باز: "success", "در حال داوری": "warning", "پایان‌یافته": "neutral" };
const quizStatuses: Quiz["status"][] = ["باز", "در حال داوری", "پایان‌یافته"];

export default function Polls() {
  const [tab, setTab] = useTabParam<"polls" | "quiz">("polls", ["polls", "quiz"]);
  const [polls, setPolls] = useApiCollection<Poll>("/polls", fromPoll as any, toPoll as any);
  const [quizzes, setQuizzes] = useState<Quiz[]>([]);
  const [open, setOpen] = useState(false);
  const [question, setQuestion] = useState("");
  const [optionsText, setOptionsText] = useState("");
  const [editingPollId, setEditingPollId] = useState<string | null>(null);
  const [quizOpen, setQuizOpen] = useState(false);
  const [editingQuizId, setEditingQuizId] = useState<string | null>(null);
  const [quizForm, setQuizForm] = useState({ title: "", questions: "", minutes: "", deadline: "", passing: "", status: "باز" as Quiz["status"] });
  const { notify } = useToast();
  const confirm = useConfirm();

  const loadQuizzes = () =>
    http<any[]>("/quizzes?page_size=100").then((rows) => setQuizzes(rows.map(fromQuiz) as Quiz[]));

  useEffect(() => { loadQuizzes().catch(() => {}); }, []);

  // ── polls ─────────────────────────────────────────────────────────────────
  const vote = (pollId: string, optId: string) => {
    setPolls((prev) =>
      prev.map((p) => {
        if (p.id !== pollId) return p;
        if (p.myVote === optId) return p;
        return {
          ...p,
          myVote: optId,
          options: p.options.map((o) => ({
            ...o,
            votes: o.votes + (o.id === optId ? 1 : 0) - (o.id === p.myVote ? 1 : 0),
          })),
        };
      })
    );
    http(`/polls/${pollId}/vote`, { method: "POST", body: JSON.stringify({ option_id: optId }) })
      .then(() => notify("رأی شما ثبت شد.", "success"))
      .catch((err) => notify(apiMessage(err, "ثبت رأی ناموفق بود."), "warning"));
  };

  const openPollModal = (p?: Poll) => {
    if (p) {
      setEditingPollId(p.id);
      setQuestion(p.question);
      setOptionsText(p.options.map((o) => o.label).join("، "));
    } else {
      setEditingPollId(null);
      setQuestion("");
      setOptionsText("");
    }
    setOpen(true);
  };

  const createPoll = () => {
    const opts = optionsText.split("،").map((s) => s.trim()).filter(Boolean);
    if (!question.trim() || opts.length < 2) {
      notify("سوال و حداقل دو گزینه (جداشده با «،») الزامی است.", "warning");
      return;
    }
    if (editingPollId) {
      // Options belong to the ballots already cast, so editing only retitles.
      setPolls((prev) => prev.map((p) => (p.id === editingPollId ? { ...p, question: question.trim() } : p)));
      notify("نظرسنجی ویرایش شد.");
    } else {
      setPolls((prev) => [
        { id: `pl-${Date.now()}`, question: question.trim(), by: "شما", ends: "", options: opts.map((label, i) => ({ id: `o${i}`, label, votes: 0 })) },
        ...prev,
      ]);
      notify("نظرسنجی منتشر شد.");
    }
    setOpen(false);
    setEditingPollId(null);
    setQuestion("");
    setOptionsText("");
  };

  const removePoll = (p: Poll) =>
    confirm({
      title: `حذف نظرسنجی «${p.question}»؟`,
      message: `${p.options.reduce((s, o) => s + o.votes, 0).toLocaleString("fa-IR")} رأی ثبت‌شده نیز حذف می‌شود.`,
      onConfirm: () => {
        setPolls((prev) => prev.filter((x) => x.id !== p.id));
        notify("نظرسنجی حذف شد.", "info");
      },
    });

  // ── quizzes ───────────────────────────────────────────────────────────────
  const openQuizModal = (q?: Quiz) => {
    if (q) {
      setEditingQuizId(q.id);
      setQuizForm({ title: q.title, questions: String(q.questions), minutes: String(q.minutes), deadline: q.deadline, passing: String(q.passing), status: q.status });
    } else {
      setEditingQuizId(null);
      setQuizForm({ title: "", questions: "", minutes: "", deadline: "", passing: "", status: "باز" });
    }
    setQuizOpen(true);
  };

  const submitQuiz = async () => {
    if (!quizForm.title.trim()) {
      notify("عنوان آزمون الزامی است.", "warning");
      return;
    }
    const body = {
      title: quizForm.title.trim(),
      questions: Number(quizForm.questions) || 0,
      minutes: Number(quizForm.minutes) || 0,
      deadline: quizForm.deadline.trim(),
      passing: Number(quizForm.passing) || 60,
      status: qzStatusApi[quizForm.status] ?? "open",
    };
    try {
      if (editingQuizId) {
        await http(`/quizzes/${editingQuizId}`, { method: "PATCH", body: JSON.stringify(body) });
        notify("آزمون ویرایش شد.");
      } else {
        await http("/quizzes", { method: "POST", body: JSON.stringify(body) });
        notify("آزمون ایجاد شد.");
      }
      await loadQuizzes();
      setQuizOpen(false);
      setEditingQuizId(null);
    } catch (err) {
      notify(apiMessage(err, "ثبت آزمون ناموفق بود."), "warning");
    }
  };

  const removeQuiz = (q: Quiz) =>
    confirm({
      title: `حذف آزمون «${q.title}»؟`,
      message: "کارنامه‌ها و پاسخ‌های ثبت‌شده‌ی این آزمون نیز حذف می‌شود.",
      onConfirm: async () => {
        try {
          await http(`/quizzes/${q.id}`, { method: "DELETE" });
          await loadQuizzes();
          notify("آزمون حذف شد.", "info");
        } catch (err) {
          notify(apiMessage(err, "حذف آزمون ناموفق بود."), "warning");
        }
      },
    });

  return (
    <div>
      <PageHeader
        title="نظرسنجی و آزمون"
        description="نظرسنجی‌های سازمانی با نتایج زنده، و آزمون‌های دوره‌ای با داوری و کارنامه"
        icon={<ListChecks size={18} />}
        actions={
          <Button variant="primary" icon={<Plus size={15} />} onClick={() => (tab === "polls" ? openPollModal() : openQuizModal())}>
            {tab === "polls" ? "نظرسنجی جدید" : "آزمون جدید"}
          </Button>
        }
      />
      <Tabs
        tabs={[
          { id: "polls", label: "نظرسنجی‌ها", count: polls.length },
          { id: "quiz", label: "آزمون‌ها و داوری", count: quizzes.length },
        ]}
        active={tab}
        onChange={setTab}
      />

      {tab === "polls" && polls.length === 0 && <EmptyState icon={<ListChecks size={20} />} title="هنوز نظرسنجی‌ای ایجاد نشده" />}

      {tab === "polls" && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          {polls.map((p) => {
            const total = p.options.reduce((s, o) => s + o.votes, 0);
            return (
              <div key={p.id} className="card p-4">
                <div className="flex items-start justify-between gap-2">
                  <p className="text-sm font-bold text-ink-900 leading-6">{p.question}</p>
                  <RowActions onEdit={() => openPollModal(p)} onDelete={() => removePoll(p)} size={13} />
                </div>
                <p className="text-[11px] text-ink-400 mt-0.5 mb-3">
                  توسط {p.by}{p.ends ? ` · مهلت رأی: ${p.ends}` : ""} · {total.toLocaleString("fa-IR")} رأی
                </p>
                <div className="space-y-2">
                  {p.options.map((o) => {
                    const pct = total ? Math.round((o.votes / total) * 100) : 0;
                    const mine = p.myVote === o.id;
                    return (
                      <button
                        key={o.id}
                        onClick={() => vote(p.id, o.id)}
                        className={`w-full text-right relative overflow-hidden rounded-lg border px-3 py-2 transition-colors ${
                          mine ? "border-brand-400 bg-brand-50" : "border-ink-200 hover:border-brand-300"
                        }`}
                      >
                        <span className="absolute inset-y-0 right-0 bg-brand-100/70 transition-all" style={{ width: `${p.myVote ? pct : 0}%` }} />
                        <span className="relative flex items-center justify-between gap-2 text-[12.5px]">
                          <span className={`flex items-center gap-1.5 ${mine ? "font-bold text-brand-700" : "text-ink-800"}`}>
                            {mine && <CheckCircle2 size={13} />} {o.label}
                          </span>
                          {p.myVote && <span className="text-ink-500 font-medium">{pct.toLocaleString("fa-IR")}٪</span>}
                        </span>
                      </button>
                    );
                  })}
                </div>
              </div>
            );
          })}
        </div>
      )}

      {tab === "quiz" && (
        <div className="card divide-y divide-ink-100">
          {quizzes.length === 0 && <p className="p-6 text-center text-sm text-ink-400">هنوز آزمونی تعریف نشده است.</p>}
          {quizzes.map((q) => (
            <div key={q.id} className="p-4 flex items-center justify-between gap-3 flex-wrap">
              <div className="min-w-0">
                <p className="text-sm font-medium text-ink-900 flex items-center gap-1.5">
                  <FileQuestion size={14} className="text-brand-600 shrink-0" /> {q.title}
                </p>
                <p className="text-[11.5px] text-ink-400 mt-1 flex items-center gap-2 flex-wrap">
                  {q.questions.toLocaleString("fa-IR")} سوال
                  <span className="flex items-center gap-1"><Timer size={11} /> {q.minutes.toLocaleString("fa-IR")} دقیقه</span>
                  {q.deadline ? `· مهلت ${q.deadline} ` : ""}· حدنصاب {q.passing.toLocaleString("fa-IR")}
                </p>
              </div>
              <div className="flex items-center gap-2 shrink-0">
                {q.myScore !== undefined && (
                  <Badge tone={q.myScore >= q.passing ? "success" : "danger"}>نمره شما: {q.myScore.toLocaleString("fa-IR")}</Badge>
                )}
                <Badge tone={quizTone[q.status]}>{q.status}</Badge>
                <RowActions onEdit={() => openQuizModal(q)} onDelete={() => removeQuiz(q)} />
              </div>
            </div>
          ))}
          <p className="p-3.5 text-[11px] text-ink-400 leading-5">
            روند: شرکت در آزمون ← تصحیح خودکار سوالات تستی ← داوری سوالات تشریحی توسط داور ← انتشار کارنامه و درج در شناسنامه آموزشی.
          </p>
        </div>
      )}

      <Modal open={open} onClose={() => setOpen(false)} title={editingPollId ? "ویرایش نظرسنجی" : "ایجاد نظرسنجی جدید"}>
        <div className="space-y-3">
          <div>
            <label className="text-xs font-medium text-ink-600 block mb-1.5">سوال نظرسنجی <span className="text-rose-500">*</span></label>
            <input value={question} onChange={(e) => setQuestion(e.target.value)} placeholder="مثلاً: موضوع کارگاه بعدی چه باشد؟" className="input-field" />
          </div>
          <div>
            <label className="text-xs font-medium text-ink-600 block mb-1.5">گزینه‌ها (با «،» جدا کنید) <span className="text-rose-500">*</span></label>
            <textarea
              value={optionsText}
              onChange={(e) => setOptionsText(e.target.value)}
              placeholder="گزینه یک، گزینه دو، گزینه سه"
              className="input-field min-h-16"
              disabled={!!editingPollId}
            />
            {editingPollId && (
              <p className="text-[10.5px] text-ink-400 mt-1 leading-4">
                گزینه‌ها پس از ثبت رأی قابل تغییر نیستند؛ برای تغییر گزینه‌ها نظرسنجی تازه‌ای بسازید.
              </p>
            )}
          </div>
          <div className="flex items-center gap-2 pt-2">
            <Button variant="primary" className="flex-1 justify-center" onClick={createPoll}>
              {editingPollId ? "ذخیره تغییرات" : "انتشار نظرسنجی"}
            </Button>
            <Button variant="secondary" onClick={() => setOpen(false)}>انصراف</Button>
          </div>
        </div>
      </Modal>

      <Modal open={quizOpen} onClose={() => setQuizOpen(false)} title={editingQuizId ? "ویرایش آزمون" : "ایجاد آزمون جدید"}>
        <div className="space-y-3">
          <div>
            <label className="text-xs font-medium text-ink-600 block mb-1.5">عنوان آزمون <span className="text-rose-500">*</span></label>
            <input value={quizForm.title} onChange={(e) => setQuizForm((f) => ({ ...f, title: e.target.value }))} className="input-field" />
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="text-xs font-medium text-ink-600 block mb-1.5">تعداد سوال</label>
              <input value={quizForm.questions} onChange={(e) => setQuizForm((f) => ({ ...f, questions: e.target.value }))} className="input-field" placeholder="۲۰" />
            </div>
            <div>
              <label className="text-xs font-medium text-ink-600 block mb-1.5">مدت (دقیقه)</label>
              <input value={quizForm.minutes} onChange={(e) => setQuizForm((f) => ({ ...f, minutes: e.target.value }))} className="input-field" placeholder="۳۰" />
            </div>
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="text-xs font-medium text-ink-600 block mb-1.5">مهلت</label>
              <input value={quizForm.deadline} onChange={(e) => setQuizForm((f) => ({ ...f, deadline: e.target.value }))} className="input-field" placeholder="۱۴۰۵/۰۵/۱۰" />
            </div>
            <div>
              <label className="text-xs font-medium text-ink-600 block mb-1.5">حدنصاب قبولی</label>
              <input value={quizForm.passing} onChange={(e) => setQuizForm((f) => ({ ...f, passing: e.target.value }))} className="input-field" placeholder="۷۰" />
            </div>
          </div>
          <div>
            <label className="text-xs font-medium text-ink-600 block mb-1.5">وضعیت</label>
            <select value={quizForm.status} onChange={(e) => setQuizForm((f) => ({ ...f, status: e.target.value as Quiz["status"] }))} className="input-field">
              {quizStatuses.map((s) => <option key={s}>{s}</option>)}
            </select>
          </div>
          <div className="flex items-center gap-2 pt-2">
            <Button variant="primary" className="flex-1 justify-center" onClick={submitQuiz}>{editingQuizId ? "ذخیره تغییرات" : "ایجاد آزمون"}</Button>
            <Button variant="secondary" onClick={() => setQuizOpen(false)}>انصراف</Button>
          </div>
        </div>
      </Modal>
    </div>
  );
}
