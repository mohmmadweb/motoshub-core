import { useState } from "react";
import { Crown, Shield, UserMinus, Ban, BellOff, Bell, Link2, RotateCcw, Timer } from "lucide-react";
import { http, getUser } from "../lib/http";
import Avatar from "./Avatar";
import Badge from "./ui/Badge";
import Button from "./ui/Button";
import { useToast } from "./ui/ToastProvider";
import { useConfirm } from "./ui/ConfirmProvider";

/* eslint-disable @typescript-eslint/no-explicit-any */

export type GroupMember = {
  id: string;
  user: { id: string; name: string; avatar_color?: string };
  name: string;
  title: string;
  presence: string;
  role: "owner" | "admin" | "member";
  muted: boolean;
  banned: boolean;
  can_moderate: boolean;
};

const ROLE_LABEL: Record<string, string> = { owner: "مالک", admin: "مدیر", member: "عضو" };

/** Member roster + moderation (promote, demote, mute, ban, remove) and the
 *  group's invite link and slow-mode setting. */
export default function GroupMembersPanel({
  groupId, members, setMembers, canModerate, slowMode, onSlowMode,
}: {
  groupId: string;
  members: GroupMember[];
  setMembers: (fn: (prev: GroupMember[]) => GroupMember[]) => void;
  canModerate: boolean;
  slowMode: number;
  onSlowMode: (seconds: number) => void;
}) {
  const me = getUser() as { id?: string } | null;
  const { notify } = useToast();
  const confirm = useConfirm();
  const [invite, setInvite] = useState<string | null>(null);

  const patch = (m: GroupMember, body: Record<string, unknown>, ok: string) =>
    http<GroupMember>(`/groups/${groupId}/members/${m.user.id}`, { method: "PATCH", body: JSON.stringify(body) })
      .then((u) => { setMembers((prev) => prev.map((x) => (x.id === u.id ? u : x))); notify(ok, "info"); })
      .catch((e: any) => notify(e?.error?.message ?? "این عملیات مجاز نیست.", "warning"));

  const remove = (m: GroupMember) =>
    confirm({
      title: `حذف «${m.name}» از گروه؟`,
      message: "این کاربر دیگر پیام‌های گروه را نمی‌بیند.",
      onConfirm: () => {
        http(`/groups/${groupId}/members/${m.user.id}`, { method: "DELETE" })
          .then(() => { setMembers((prev) => prev.filter((x) => x.id !== m.id)); notify(`«${m.name}» حذف شد.`, "info"); })
          .catch(() => notify("حذف عضو مجاز نیست.", "warning"));
      },
    });

  const loadInvite = (rotate = false) =>
    http<{ invite_code: string }>(`/groups/${groupId}/invite`, rotate ? { method: "POST" } : {})
      .then((d) => { setInvite(d.invite_code); if (rotate) notify("لینک دعوت جدید ساخته شد؛ لینک قبلی باطل است.", "info"); })
      .catch(() => notify("لینک دعوت فقط برای مدیران گروه است.", "warning"));

  return (
    <div className="space-y-4">
      {canModerate && (
        <div className="card p-4 space-y-3">
          <h3 className="text-sm font-bold text-ink-900">مدیریت گروه</h3>

          <div className="flex items-center gap-2 flex-wrap">
            <Button variant="secondary" size="sm" icon={<Link2 size={13} />} onClick={() => loadInvite(false)}>
              لینک دعوت
            </Button>
            {invite && (
              <>
                <code dir="ltr" className="text-[11px] bg-ink-50 border border-ink-100 rounded-lg px-2.5 py-1.5 select-all">
                  {invite}
                </code>
                <Button variant="ghost" size="sm" icon={<RotateCcw size={12} />} onClick={() => loadInvite(true)}>
                  چرخش
                </Button>
              </>
            )}
          </div>

          <div className="flex items-center gap-2 pt-2 border-t border-ink-100">
            <Timer size={14} className="text-ink-400 shrink-0" />
            <label className="text-[12px] text-ink-600 shrink-0">حالت آهسته:</label>
            <select
              value={slowMode}
              onChange={(e) => {
                const v = Number(e.target.value);
                http(`/groups/${groupId}/settings`, { method: "PATCH", body: JSON.stringify({ slow_mode_seconds: v }) })
                  .then(() => { onSlowMode(v); notify(v ? `اعضا هر ${v} ثانیه یک پیام می‌توانند بفرستند.` : "حالت آهسته خاموش شد.", "info"); })
                  .catch(() => notify("تغییر تنظیمات مجاز نیست.", "warning"));
              }}
              className="text-[12px] border border-ink-200 rounded-lg px-2 py-1.5 bg-white"
            >
              <option value={0}>خاموش</option>
              <option value={10}>۱۰ ثانیه</option>
              <option value={30}>۳۰ ثانیه</option>
              <option value={60}>۱ دقیقه</option>
              <option value={300}>۵ دقیقه</option>
            </select>
          </div>
        </div>
      )}

      <div className="card divide-y divide-ink-100">
        {members.map((m) => {
          const isMe = m.user.id === me?.id;
          return (
            <div key={m.id} className="p-3.5 flex items-center gap-3">
              <Avatar name={m.name} color={m.user.avatar_color} size={38} status={m.presence as any} />
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-ink-900 truncate flex items-center gap-1.5">
                  {m.name}
                  {m.role === "owner" && <Crown size={12} className="text-amber-500" />}
                  {m.role === "admin" && <Shield size={12} className="text-brand-600" />}
                  {isMe && <span className="text-[10px] text-ink-400">(شما)</span>}
                </p>
                <p className="text-[11.5px] text-ink-400 truncate">{m.title || "—"}</p>
              </div>

              <div className="flex items-center gap-1.5 shrink-0">
                {m.banned && <Badge tone="danger">محدود</Badge>}
                {m.muted && <BellOff size={12} className="text-ink-400" />}
                <Badge tone={m.role === "owner" ? "navy" : m.role === "admin" ? "brand" : "neutral"}>
                  {ROLE_LABEL[m.role]}
                </Badge>

                {isMe && (
                  <button onClick={() => patch(m, { muted: !m.muted }, m.muted ? "اعلان‌های گروه روشن شد." : "اعلان‌های گروه بی‌صدا شد.")}
                    title={m.muted ? "روشن‌کردن اعلان" : "بی‌صداکردن"} className="text-ink-400 hover:text-brand-600 p-1">
                    {m.muted ? <Bell size={13} /> : <BellOff size={13} />}
                  </button>
                )}

                {canModerate && m.role !== "owner" && (
                  <>
                    <button
                      onClick={() => patch(m, { role: m.role === "admin" ? "member" : "admin" },
                        m.role === "admin" ? `«${m.name}» به عضو عادی تغییر کرد.` : `«${m.name}» مدیر گروه شد.`)}
                      title={m.role === "admin" ? "تنزل به عضو" : "ارتقا به مدیر"}
                      className="text-ink-400 hover:text-brand-600 p-1"><Shield size={13} /></button>
                    <button
                      onClick={() => patch(m, { banned: !m.banned }, m.banned ? `محدودیت «${m.name}» برداشته شد.` : `«${m.name}» محدود شد.`)}
                      title={m.banned ? "رفع محدودیت" : "محدودکردن"}
                      className="text-ink-400 hover:text-amber-600 p-1"><Ban size={13} /></button>
                    <button onClick={() => remove(m)} title="حذف از گروه"
                      className="text-ink-400 hover:text-rose-600 p-1"><UserMinus size={13} /></button>
                  </>
                )}
              </div>
            </div>
          );
        })}
        {members.length === 0 && <p className="p-4 text-xs text-ink-400 text-center">عضوی ثبت نشده است.</p>}
      </div>
    </div>
  );
}
