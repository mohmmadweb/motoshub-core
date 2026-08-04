import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import {
  Send, Reply, Pencil, Trash2, Pin, PinOff, Paperclip, Smile, X,
  ThumbsUp, Heart, CheckCircle2, CornerUpLeft, Search, Forward, BarChart3, Plus,
} from "lucide-react";
import { http, getUser } from "../lib/http";
import { openChannelSocket } from "../lib/ws";
import Avatar from "./Avatar";
import Button from "./ui/Button";
import EmptyState from "./ui/EmptyState";
import { useToast } from "./ui/ToastProvider";
import { useConfirm } from "./ui/ConfirmProvider";

/* eslint-disable @typescript-eslint/no-explicit-any */

export type GroupMessage = {
  id: string;
  author: { id: string; name: string; avatar_color?: string } | null;
  text: string;
  pinned: boolean;
  deleted: boolean;
  edited_at: string | null;
  forwarded_from: string;
  attachment: { id?: string; kind?: string; name?: string; size?: string; url?: string } | null;
  mentions: string[];
  reply_to: { id: string; author: { name: string } | null; text: string; deleted: boolean } | null;
  reactions: { icon: string; count: number; reactedByMe: boolean }[];
  created_at: string;
};

const REACTIONS: { icon: string; Cmp: typeof ThumbsUp; title: string }[] = [
  { icon: "ThumbsUp", Cmp: ThumbsUp, title: "پسندیدم" },
  { icon: "Heart", Cmp: Heart, title: "قلب" },
  { icon: "Smile", Cmp: Smile, title: "لبخند" },
  { icon: "CheckCircle2", Cmp: CheckCircle2, title: "تأیید" },
];
const ICONS: Record<string, typeof ThumbsUp> = { ThumbsUp, Heart, Smile, CheckCircle2 };

const time = (iso: string) =>
  new Date(iso).toLocaleTimeString("fa-IR", { hour: "2-digit", minute: "2-digit" });
const day = (iso: string) =>
  new Date(iso).toLocaleDateString("fa-IR", { day: "numeric", month: "long" });

/**
 * The group's conversation — a Telegram-grade chat: replies, reactions, edit,
 * soft-delete, pins, attachments, mentions, forwarding, search, typing and live
 * updates over the group's WebSocket channel.
 */
export default function GroupChat({
  groupId,
  channelId,
  canModerate,
  canPost,
  members,
}: {
  groupId: string;
  channelId?: string;
  canModerate: boolean;
  canPost: boolean;
  members: { user: { id: string }; name: string }[];
}) {
  const me = getUser() as { id?: string; name?: string } | null;
  const { notify } = useToast();
  const confirm = useConfirm();

  const [messages, setMessages] = useState<GroupMessage[]>([]);
  const [draft, setDraft] = useState("");
  const [replyTo, setReplyTo] = useState<GroupMessage | null>(null);
  const [editing, setEditing] = useState<GroupMessage | null>(null);
  const [forwarding, setForwarding] = useState<GroupMessage | null>(null);
  const [query, setQuery] = useState("");
  const [showPinned, setShowPinned] = useState(false);
  const [typingWho, setTypingWho] = useState<string | null>(null);
  const [mentionOpen, setMentionOpen] = useState(false);
  const [polls, setPolls] = useState<any[]>([]);
  const [pollOpen, setPollOpen] = useState(false);
  const [pollQ, setPollQ] = useState("");
  const [pollOpts, setPollOpts] = useState<string[]>(["", ""]);
  const scrollRef = useRef<HTMLDivElement>(null);
  const fileRef = useRef<HTMLInputElement>(null);
  const typingSent = useRef(0);

  const scrollDown = () =>
    requestAnimationFrame(() =>
      scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: "smooth" }));

  const load = useCallback(() => {
    http<GroupMessage[]>(`/groups/${groupId}/messages`)
      .then((rows) => { setMessages(rows); scrollDown(); })
      .catch(() => setMessages([]));
  }, [groupId]);

  useEffect(() => { load(); }, [load]);

  // In-group polls (Telegram-style): created in the conversation, voted inline.
  const loadPolls = useCallback(() => {
    http<any[]>(`/polls?group=${groupId}&page_size=20`).then(setPolls).catch(() => setPolls([]));
  }, [groupId]);
  useEffect(() => { loadPolls(); }, [loadPolls]);

  const createPoll = () => {
    const opts = pollOpts.map((o) => o.trim()).filter(Boolean);
    if (!pollQ.trim() || opts.length < 2) {
      notify("پرسش و حداقل دو گزینه لازم است.", "warning");
      return;
    }
    http<any>("/polls", { method: "POST", body: JSON.stringify({ question: pollQ.trim(), option_labels: opts, group: groupId }) })
      .then((p) => { setPolls((prev) => [p, ...prev]); setPollOpen(false); setPollQ(""); setPollOpts(["", ""]);
                     notify("نظرسنجی در گروه منتشر شد."); })
      .catch(() => notify("ایجاد نظرسنجی ناموفق بود.", "warning"));
  };

  const votePoll = (pollId: string, optionId: string) =>
    http<any>(`/polls/${pollId}/vote`, { method: "POST", body: JSON.stringify({ option_id: optionId }) })
      .then(() => loadPolls())
      .catch(() => notify("ثبت رأی ناموفق بود.", "warning"));

  // Live updates: the group's conversation is a channel, so we reuse its socket.
  useEffect(() => {
    if (!channelId) return;
    const sock = openChannelSocket(channelId);
    if (!sock) return;
    sock.onmessage = (ev) => {
      try {
        const data = JSON.parse(ev.data);
        if (data.type === "typing") {
          if (data.user_id === me?.id) return;
          setTypingWho(data.user);
          setTimeout(() => setTypingWho(null), 3000);
          return;
        }
        // Upsert: edits/deletes/pins arrive as the same message id.
        setMessages((prev) => {
          const i = prev.findIndex((m) => m.id === data.id);
          if (i === -1) return [...prev, data];
          const next = [...prev]; next[i] = data; return next;
        });
        scrollDown();
      } catch { /* ignore malformed frames */ }
    };
    return () => sock.close();
  }, [channelId, me?.id]);

  const pinned = useMemo(() => messages.filter((m) => m.pinned && !m.deleted), [messages]);
  const visible = useMemo(() => {
    const q = query.trim();
    return q ? messages.filter((m) => !m.deleted && m.text.includes(q)) : messages;
  }, [messages, query]);

  const pingTyping = () => {
    const now = Date.now();
    if (now - typingSent.current < 2000) return;   // throttle
    typingSent.current = now;
    http(`/groups/${groupId}/typing`, { method: "POST" }).catch(() => {});
  };

  const send = () => {
    const text = draft.trim();
    if (!text && !forwarding) return;

    if (editing) {
      http<GroupMessage>(`/groups/${groupId}/messages/${editing.id}`, {
        method: "PATCH", body: JSON.stringify({ text }),
      }).then((m) => setMessages((p) => p.map((x) => (x.id === m.id ? m : x))))
        .catch(() => notify("ویرایش ناموفق بود.", "warning"));
      setEditing(null); setDraft("");
      return;
    }

    const mentions = members
      .filter((mm) => text.includes(`@${mm.name}`))
      .map((mm) => mm.user.id);

    http<GroupMessage>(`/groups/${groupId}/messages`, {
      method: "POST",
      body: JSON.stringify({
        text, reply_to_id: replyTo?.id ?? null, mentions,
        forwarded_from: forwarding ? (forwarding.author?.name ?? "") : "",
      }),
    })
      .then((m) => { setMessages((p) => (p.some((x) => x.id === m.id) ? p : [...p, m])); scrollDown(); })
      .catch((e: any) => notify(e?.error?.message ?? "ارسال پیام ناموفق بود.", "warning"));

    setDraft(""); setReplyTo(null); setForwarding(null);
  };

  const [uploading, setUploading] = useState(false);

  /** Upload the file for real, then post a message that points at it. */
  const attach = (file: File) => {
    const form = new FormData();
    form.append("file", file);
    setUploading(true);
    http<{ id: string; name: string; kind: string; human_size: string; url: string }>(
      "/uploads", { method: "POST", body: form },
    )
      .then((att) =>
        http<GroupMessage>(`/groups/${groupId}/messages`, {
          method: "POST",
          body: JSON.stringify({
            text: draft.trim(),
            attachment: { id: att.id, kind: att.kind, name: att.name, size: att.human_size, url: att.url },
          }),
        }))
      .then((m) => { setMessages((p) => (p.some((x) => x.id === m.id) ? p : [...p, m])); setDraft(""); scrollDown(); })
      .catch((e: any) => notify(e?.error?.message ?? "بارگذاری فایل ناموفق بود.", "warning"))
      .finally(() => setUploading(false));
  };

  const react = (m: GroupMessage, icon: string) => {
    http(`/chat/messages/${m.id}/react`, { method: "POST", body: JSON.stringify({ icon }) })
      .then((r: any) => setMessages((p) => p.map((x) => (x.id === m.id ? { ...x, reactions: r.reactions } : x))))
      .catch(() => {});
  };

  const togglePin = (m: GroupMessage) =>
    http<GroupMessage>(`/groups/${groupId}/messages/${m.id}`, {
      method: "PATCH", body: JSON.stringify({ pinned: !m.pinned }),
    }).then((u) => { setMessages((p) => p.map((x) => (x.id === u.id ? u : x)));
                     notify(u.pinned ? "پیام سنجاق شد." : "سنجاق برداشته شد.", "info"); })
      .catch(() => notify("سنجاق‌کردن فقط برای مدیران گروه است.", "warning"));

  const remove = (m: GroupMessage) =>
    confirm({
      title: "حذف پیام؟",
      message: "این پیام برای همهٔ اعضا حذف می‌شود.",
      onConfirm: () => {
        http(`/groups/${groupId}/messages/${m.id}`, { method: "DELETE" })
          .then(() => setMessages((p) => p.map((x) => (x.id === m.id ? { ...x, deleted: true, text: "", pinned: false } : x))))
          .catch(() => notify("حذف ناموفق بود.", "warning"));
      },
    });

  const mentionCandidates = mentionOpen
    ? members.filter((mm) => mm.name.includes(draft.split("@").pop() ?? "")).slice(0, 5)
    : [];

  return (
    <div className="card flex flex-col h-[560px] overflow-hidden">
      {/* ── header: search + pinned ─────────────────────────────────────── */}
      <div className="flex items-center gap-2 px-3.5 py-2.5 border-b border-ink-100 shrink-0">
        <div className="relative flex-1">
          <Search size={13} className="absolute right-2.5 top-1/2 -translate-y-1/2 text-ink-400" />
          <input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="جستجو در گفتگو…"
            className="w-full text-[12px] bg-ink-50 border border-ink-100 rounded-lg pr-8 pl-2.5 py-1.5 focus:outline-none focus:border-brand-300"
          />
        </div>
        {pinned.length > 0 && (
          <button
            onClick={() => setShowPinned((v) => !v)}
            className={`flex items-center gap-1 text-[11.5px] rounded-lg px-2.5 py-1.5 border ${
              showPinned ? "bg-brand-50 border-brand-300 text-brand-700" : "border-ink-200 text-ink-500"}`}
          >
            <Pin size={12} /> {pinned.length.toLocaleString("fa-IR")} سنجاق‌شده
          </button>
        )}
      </div>

      {showPinned && pinned.length > 0 && (
        <div className="bg-brand-50/50 border-b border-brand-100 px-3.5 py-2 space-y-1.5 shrink-0 max-h-28 overflow-y-auto">
          {pinned.map((m) => (
            <div key={m.id} className="flex items-center gap-2 text-[11.5px] text-ink-700">
              <Pin size={11} className="text-brand-600 shrink-0" />
              <span className="flex-1 truncate">{m.text}</span>
              {canModerate && (
                <button onClick={() => togglePin(m)} title="برداشتن سنجاق" className="text-ink-400 hover:text-rose-600">
                  <PinOff size={12} />
                </button>
              )}
            </div>
          ))}
        </div>
      )}

      {/* ── messages ────────────────────────────────────────────────────── */}
      <div ref={scrollRef} className="flex-1 overflow-y-auto px-3.5 py-3 space-y-2.5 chat-surface">
        {visible.length === 0 && (
          <EmptyState icon={<Send size={18} />} title={query ? "نتیجه‌ای یافت نشد" : "هنوز پیامی نیست"}
                      description={query ? undefined : "اولین پیام گروه را شما بفرستید."} />
        )}
        {visible.map((m, i) => {
          const mine = m.author?.id === me?.id;
          const showDay = i === 0 || day(visible[i - 1].created_at) !== day(m.created_at);
          return (
            <div key={m.id}>
              {showDay && (
                <div className="flex justify-center my-3">
                  <span className="text-[10.5px] text-ink-500 bg-white/80 border border-ink-100 rounded-full px-2.5 py-0.5">
                    {day(m.created_at)}
                  </span>
                </div>
              )}
              <div className={`group flex gap-2 ${mine ? "justify-start" : "justify-end"}`}>
                {!mine && <Avatar name={m.author?.name ?? "?"} color={m.author?.avatar_color} size={30} />}
                <div className={`max-w-[78%] flex flex-col ${mine ? "items-start" : "items-end"}`}>
                  <div className={`rounded-xl px-3 py-2 ${mine ? "bg-brand-600 text-white" : "bg-white border border-ink-100"}`}>
                    {!mine && <p className="text-[11px] font-bold text-brand-700 mb-0.5">{m.author?.name}</p>}

                    {m.forwarded_from && !m.deleted && (
                      <p className={`text-[10.5px] mb-1 flex items-center gap-1 ${mine ? "text-white/70" : "text-ink-400"}`}>
                        <Forward size={10} /> هدایت‌شده از {m.forwarded_from}
                      </p>
                    )}

                    {m.reply_to && !m.deleted && (
                      <div className={`text-[11px] rounded-lg px-2 py-1 mb-1.5 border-r-2 ${
                        mine ? "bg-white/15 border-white/50" : "bg-ink-50 border-brand-400"}`}>
                        <span className="font-medium">{m.reply_to.author?.name ?? "—"}: </span>
                        <span className="opacity-80">{m.reply_to.deleted ? "پیام حذف‌شده" : m.reply_to.text.slice(0, 60)}</span>
                      </div>
                    )}

                    {m.deleted ? (
                      <p className={`text-[12px] italic ${mine ? "text-white/60" : "text-ink-400"}`}>این پیام حذف شد</p>
                    ) : (
                      <>
                        {m.attachment && (
                          m.attachment.kind === "photo" && m.attachment.url ? (
                            <a href={m.attachment.url} target="_blank" rel="noreferrer" className="block mb-1">
                              <img src={m.attachment.url} alt={m.attachment.name}
                                   className="rounded-lg max-h-56 w-auto object-cover" />
                            </a>
                          ) : (
                            <a href={m.attachment.url ?? "#"} target="_blank" rel="noreferrer"
                              className={`flex items-center gap-2 text-[11.5px] rounded-lg px-2 py-1.5 mb-1 hover:underline ${
                                mine ? "bg-white/15" : "bg-ink-50"}`}>
                              <Paperclip size={12} className="shrink-0" />
                              <span className="truncate font-medium">{m.attachment.name}</span>
                              <span className="opacity-70 shrink-0">{m.attachment.size}</span>
                            </a>
                          )
                        )}
                        {m.text && <p className="text-[13px] leading-6 whitespace-pre-wrap break-words">{m.text}</p>}
                      </>
                    )}

                    <div className={`flex items-center gap-1.5 mt-1 text-[10px] ${mine ? "text-white/60" : "text-ink-400"}`}>
                      <span>{time(m.created_at)}</span>
                      {m.edited_at && !m.deleted && <span>· ویرایش‌شده</span>}
                      {m.pinned && <Pin size={9} />}
                    </div>
                  </div>

                  {/* reactions */}
                  {m.reactions.length > 0 && (
                    <div className={`flex items-center gap-1 mt-1 flex-wrap ${mine ? "justify-start" : "justify-end"}`}>
                      {m.reactions.map((r) => {
                        const Icon = ICONS[r.icon] ?? ThumbsUp;
                        return (
                          <button key={r.icon} onClick={() => react(m, r.icon)}
                            className={`flex items-center gap-0.5 text-[10.5px] rounded-full border px-1.5 py-0.5 ${
                              r.reactedByMe ? "bg-brand-50 border-brand-300 text-brand-700" : "border-ink-200 text-ink-500"}`}>
                            <Icon size={10} /> {r.count.toLocaleString("fa-IR")}
                          </button>
                        );
                      })}
                    </div>
                  )}

                  {/* hover actions */}
                  {!m.deleted && (
                    <div className={`flex items-center gap-1 mt-1 opacity-0 group-hover:opacity-100 transition-opacity ${mine ? "justify-start" : "justify-end"}`}>
                      {REACTIONS.map(({ icon, Cmp, title }) => (
                        <button key={icon} onClick={() => react(m, icon)} title={title}
                          className="text-ink-400 hover:text-brand-600 p-0.5"><Cmp size={12} /></button>
                      ))}
                      <button onClick={() => { setReplyTo(m); setEditing(null); }} title="پاسخ"
                        className="text-ink-400 hover:text-brand-600 p-0.5"><Reply size={12} /></button>
                      <button onClick={() => { setForwarding(m); setDraft(m.text); }} title="هدایت"
                        className="text-ink-400 hover:text-brand-600 p-0.5"><Forward size={12} /></button>
                      {canModerate && (
                        <button onClick={() => togglePin(m)} title={m.pinned ? "برداشتن سنجاق" : "سنجاق"}
                          className="text-ink-400 hover:text-amber-600 p-0.5">
                          {m.pinned ? <PinOff size={12} /> : <Pin size={12} />}
                        </button>
                      )}
                      {mine && (
                        <button onClick={() => { setEditing(m); setDraft(m.text); setReplyTo(null); }} title="ویرایش"
                          className="text-ink-400 hover:text-brand-600 p-0.5"><Pencil size={12} /></button>
                      )}
                      {(mine || canModerate) && (
                        <button onClick={() => remove(m)} title="حذف"
                          className="text-ink-400 hover:text-rose-600 p-0.5"><Trash2 size={12} /></button>
                      )}
                    </div>
                  )}
                </div>
              </div>
            </div>
          );
        })}
        {typingWho && (
          <p className="text-[11px] text-ink-400 pr-10">{typingWho} در حال نوشتن…</p>
        )}
      </div>

      {/* ── in-group polls ──────────────────────────────────────────────── */}
      {polls.length > 0 && (
        <div className="border-t border-ink-100 px-3.5 py-2.5 space-y-2 shrink-0 max-h-44 overflow-y-auto bg-ink-50/40">
          {polls.map((p) => {
            const total = p.options.reduce((s: number, o: any) => s + o.votes, 0);
            return (
              <div key={p.id} className="rounded-lg border border-ink-100 bg-white p-2.5">
                <p className="text-[12px] font-bold text-ink-900 mb-1.5 flex items-center gap-1.5">
                  <BarChart3 size={12} className="text-brand-600" /> {p.question}
                </p>
                <div className="space-y-1">
                  {p.options.map((o: any) => {
                    const pct = total ? Math.round((o.votes / total) * 100) : 0;
                    const mineVote = p.my_vote === o.id;
                    return (
                      <button key={o.id} onClick={() => votePoll(p.id, o.id)}
                        className="w-full text-right relative rounded-md border border-ink-100 px-2 py-1 overflow-hidden hover:border-brand-300">
                        <span className={`absolute inset-y-0 right-0 ${mineVote ? "bg-brand-100" : "bg-ink-100"}`}
                              style={{ width: `${pct}%` }} />
                        <span className="relative flex items-center justify-between text-[11.5px]">
                          <span className={mineVote ? "font-bold text-brand-700" : "text-ink-700"}>{o.label}</span>
                          <span className="text-ink-400">{pct.toLocaleString("fa-IR")}٪</span>
                        </span>
                      </button>
                    );
                  })}
                </div>
                <p className="text-[10.5px] text-ink-400 mt-1">{total.toLocaleString("fa-IR")} رأی</p>
              </div>
            );
          })}
        </div>
      )}

      {pollOpen && (
        <div className="border-t border-ink-100 px-3.5 py-2.5 space-y-2 shrink-0 bg-white">
          <input value={pollQ} onChange={(e) => setPollQ(e.target.value)} placeholder="پرسش نظرسنجی…"
            className="w-full text-[12px] border border-ink-200 rounded-lg px-2.5 py-1.5 focus:outline-none focus:border-brand-300" />
          {pollOpts.map((o, i) => (
            <input key={i} value={o} placeholder={`گزینه ${(i + 1).toLocaleString("fa-IR")}`}
              onChange={(e) => setPollOpts((prev) => prev.map((x, j) => (j === i ? e.target.value : x)))}
              className="w-full text-[12px] border border-ink-200 rounded-lg px-2.5 py-1.5 focus:outline-none focus:border-brand-300" />
          ))}
          <div className="flex items-center gap-2">
            <Button variant="ghost" size="sm" icon={<Plus size={12} />} onClick={() => setPollOpts((p) => [...p, ""])}>
              گزینه
            </Button>
            <Button variant="primary" size="sm" onClick={createPoll}>انتشار</Button>
            <Button variant="secondary" size="sm" onClick={() => setPollOpen(false)}>انصراف</Button>
          </div>
        </div>
      )}

      {/* ── composer ────────────────────────────────────────────────────── */}
      {canPost ? (
        <div className="border-t border-ink-100 shrink-0">
          {(replyTo || editing || forwarding) && (
            <div className="flex items-center gap-2 px-3.5 py-1.5 bg-ink-50 border-b border-ink-100 text-[11.5px]">
              {editing ? <Pencil size={12} className="text-brand-600" />
                : forwarding ? <Forward size={12} className="text-brand-600" />
                : <CornerUpLeft size={12} className="text-brand-600" />}
              <span className="text-ink-500 shrink-0">
                {editing ? "ویرایش:" : forwarding ? "هدایت:" : `پاسخ به ${replyTo?.author?.name}:`}
              </span>
              <span className="flex-1 truncate text-ink-700">
                {(editing ?? forwarding ?? replyTo)?.text || "پیام رسانه‌ای"}
              </span>
              <button onClick={() => { setReplyTo(null); setEditing(null); setForwarding(null); setDraft(""); }}
                className="text-ink-400 hover:text-ink-700"><X size={13} /></button>
            </div>
          )}

          {mentionCandidates.length > 0 && (
            <div className="px-3.5 py-1.5 border-b border-ink-100 flex items-center gap-1.5 flex-wrap">
              {mentionCandidates.map((mm) => (
                <button key={mm.user.id}
                  onClick={() => { setDraft((d) => `${d.slice(0, d.lastIndexOf("@"))}@${mm.name} `); setMentionOpen(false); }}
                  className="text-[11px] rounded-full border border-ink-200 px-2 py-0.5 hover:border-brand-300 hover:text-brand-700">
                  @{mm.name}
                </button>
              ))}
            </div>
          )}

          <div className="flex items-end gap-2 px-3 py-2.5">
            <input ref={fileRef} type="file" className="hidden"
              onChange={(e) => { const f = e.target.files?.[0]; if (f) attach(f); e.target.value = ""; }} />
            <button onClick={() => setPollOpen((v) => !v)} title="نظرسنجی"
              className="text-ink-400 hover:text-brand-600 p-1.5 shrink-0"><BarChart3 size={17} /></button>
            <button onClick={() => fileRef.current?.click()} title="پیوست فایل" disabled={uploading}
              className="text-ink-400 hover:text-brand-600 p-1.5 shrink-0 disabled:opacity-40">
              <Paperclip size={17} className={uploading ? "animate-pulse" : ""} /></button>
            <textarea
              value={draft}
              onChange={(e) => {
                setDraft(e.target.value);
                setMentionOpen(/@[^\s]*$/.test(e.target.value));
                pingTyping();
              }}
              onKeyDown={(e) => { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); send(); } }}
              rows={1}
              placeholder="پیام خود را بنویسید… (@ برای منشن)"
              className="flex-1 resize-none text-[13px] leading-6 bg-ink-50 border border-ink-100 rounded-xl px-3 py-2 max-h-28 focus:outline-none focus:border-brand-300"
            />
            <Button variant="primary" size="sm" icon={<Send size={14} />} onClick={send} className="shrink-0">
              ارسال
            </Button>
          </div>
        </div>
      ) : (
        <div className="border-t border-ink-100 px-4 py-3 text-center shrink-0">
          <p className="text-xs text-ink-400">برای ارسال پیام باید عضو گروه باشید.</p>
        </div>
      )}
    </div>
  );
}
