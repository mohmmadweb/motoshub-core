import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { Flag, UserPlus, UserMinus, FileText, MessagesSquare, Pencil, Trash2 } from "lucide-react";
import { type Post } from "../data/types";
import { http, apiMessage } from "../lib/http";
import { fromPost } from "../lib/adapters";
import { useContent } from "../context/ContentContext";
import PostCard from "../components/PostCard";
import Tabs from "../components/ui/Tabs";
import Button from "../components/ui/Button";
import Modal from "../components/ui/Modal";
import EmptyState from "../components/ui/EmptyState";
import { VisibilityBadge, VisibilityToggle, VisibilityPicker } from "../components/ui/VisibilityControl";
import { useToast } from "../components/ui/ToastProvider";
import { useConfirm } from "../components/ui/ConfirmProvider";
import GroupChat from "../components/GroupChat";
import GroupMembersPanel, { type GroupMember } from "../components/GroupMembersPanel";
import { getUser } from "../lib/http";
import { useTenancy } from "../context/TenancyContext";

type TabId = "chat" | "posts" | "forum" | "members" | "docs";

export default function GroupDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { groups, setGroups } = useContent();
  const { notify } = useToast();
  const confirm = useConfirm();
  const { canModerateGroup } = useTenancy();
  const group = groups.find((g) => g.id === id);
  const [tab, setTab] = useState<TabId>("chat");
  const [groupPosts, setGroupPosts] = useState<Post[]>([]);
  const [members, setMembers] = useState<GroupMember[]>([]);
  const [channelId, setChannelId] = useState<string | undefined>();
  const [slowMode, setSlowMode] = useState(0);
  const [editOpen, setEditOpen] = useState(false);
  const [form, setForm] = useState({ name: "", description: "", category: "", privacy: "عمومی" as "عمومی" | "خصوصی" });
  const [reportOpen, setReportOpen] = useState(false);
  const [reportText, setReportText] = useState("");
  const me = getUser() as { id?: string } | null;

  useEffect(() => {
    if (!id) return;
    http<any[]>(`/posts?group=${id}&page_size=20`).then((r) => setGroupPosts(r.map(fromPost) as Post[])).catch(() => {});
    http<GroupMember[]>(`/groups/${id}/members`).then(setMembers).catch(() => setMembers([]));
    // The group's conversation lives on its own channel — first message id gives it away,
    // and the group payload carries slow mode.
    http<any>(`/groups/${id}`).then((g) => setSlowMode(g.slow_mode_seconds ?? 0)).catch(() => {});
    http<any[]>(`/groups/${id}/messages`).then((rows) => {
      if (rows.length) setChannelId(rows[0].channel);
    }).catch(() => {});
  }, [id]);

  if (!group) return <p>گروه پیدا نشد.</p>;

  const myMembership = members.find((m) => m.user.id === me?.id);
  // Moderation authority is either granted inside the group, or carried in from
  // a system/holding role — the API applies the same two rules.
  const canModerate = !!myMembership?.can_moderate || (group ? canModerateGroup(group) : false);
  const canPost = !!myMembership && !myMembership.banned;

  const togglePrivacy = () => {
    const next = group.privacy === "عمومی" ? "خصوصی" : "عمومی";
    setGroups((prev) => prev.map((g) => (g.id === group.id ? { ...g, privacy: next } : g)));
    notify(`گروه «${group.name}» به ${next} تغییر یافت.`, next === "عمومی" ? "success" : "info");
  };

  const openEdit = () => {
    setForm({ name: group.name, description: group.description, category: group.category, privacy: group.privacy });
    setEditOpen(true);
  };

  const saveEdit = () => {
    if (!form.name.trim() || !form.category.trim()) {
      notify("نام گروه و دسته‌بندی الزامی است.", "warning");
      return;
    }
    setGroups((prev) =>
      prev.map((g) =>
        g.id === group.id
          ? { ...g, name: form.name.trim(), description: form.description.trim() || "بدون توضیحات", category: form.category.trim(), privacy: form.privacy }
          : g
      )
    );
    notify(`گروه «${form.name.trim()}» ویرایش شد.`);
    setEditOpen(false);
  };

  const removeGroup = () =>
    confirm({
      title: `حذف گروه «${group.name}»؟`,
      message: `${group.members.toLocaleString("fa-IR")} عضو از این گروه خارج می‌شوند و گفتگوها و اسناد گروه در دسترس نخواهد بود.`,
      onConfirm: () => {
        setGroups((prev) => prev.filter((g) => g.id !== group.id));
        notify(`گروه «${group.name}» حذف شد.`, "info");
        navigate("/dashboard/groups");
      },
    });

  const toggleMembership = async () => {
    const joining = !myMembership;
    try {
      await http(`/groups/${group.id}/${joining ? "join" : "leave"}`, { method: "POST" });
      const rows = await http<GroupMember[]>(`/groups/${group.id}/members`);
      setMembers(rows);
      setGroups((prev) => prev.map((g) => (g.id === group.id ? { ...g, members: rows.length } : g)));
      notify(joining ? `به گروه «${group.name}» پیوستید.` : `از گروه «${group.name}» خارج شدید.`, "info");
    } catch (err) {
      notify(apiMessage(err, joining ? "عضویت ناموفق بود." : "خروج از گروه ناموفق بود."), "warning");
    }
  };

  // A report has to reach someone. It opens a real support ticket rather than
  // showing a toast and vanishing.
  const sendReport = async () => {
    if (!reportText.trim()) {
      notify("شرح تخلف الزامی است.", "warning");
      return;
    }
    try {
      await http("/tickets", {
        method: "POST",
        body: JSON.stringify({
          subject: `گزارش تخلف در گروه «${group.name}»`,
          category: "گزارش تخلف",
          priority: "urgent",
          body: reportText.trim(),
        }),
      });
      notify("گزارش شما برای ناظمان ارسال شد.");
      setReportOpen(false);
      setReportText("");
    } catch (err) {
      notify(apiMessage(err, "ارسال گزارش ناموفق بود."), "warning");
    }
  };

  return (
    <div>
      <div className="rounded-lg border border-ink-200 bg-navy-900 p-6 mb-5 flex items-center justify-between flex-wrap gap-4">
        <div className="flex items-center gap-4">
          <span className="w-14 h-14 rounded-lg flex items-center justify-center text-white font-bold text-xl shrink-0" style={{ backgroundColor: group.color }}>
            {group.name.slice(0, 1)}
          </span>
          <div>
            <div className="flex items-center gap-2 mb-1">
              <h1 className="text-lg font-bold text-white">{group.name}</h1>
              <VisibilityBadge visibility={group.privacy} />
            </div>
            <p className="text-sm text-navy-200">{group.description}</p>
            <p className="text-xs text-navy-300 mt-2">{group.members.toLocaleString("fa-IR")} عضو · دسته‌بندی: {group.category}</p>
          </div>
        </div>
        <div className="flex items-center gap-2 flex-wrap">
          {canModerate && <VisibilityToggle visibility={group.privacy} onChange={togglePrivacy} size="sm" />}
          {canModerate && (
            <Button variant="secondary" size="sm" icon={<Pencil size={13} />} onClick={openEdit}>
              ویرایش گروه
            </Button>
          )}
          {canModerate && (
            <Button variant="secondary" size="sm" icon={<Trash2 size={13} />} onClick={removeGroup}>
              حذف گروه
            </Button>
          )}
          <Button variant="secondary" size="sm" icon={<Flag size={13} />} onClick={() => setReportOpen(true)}>
            گزارش تخلف
          </Button>
          <Button
            variant={myMembership ? "secondary" : "primary"}
            size="sm"
            icon={myMembership ? <UserMinus size={13} /> : <UserPlus size={13} />}
            onClick={toggleMembership}
          >
            {myMembership ? "خروج از گروه" : "پیوستن به گروه"}
          </Button>
        </div>
      </div>

      <Tabs<TabId>
        tabs={[
          { id: "chat", label: "گفتگوی گروه" },
          { id: "posts", label: "پست‌ها", count: groupPosts.length },
          { id: "forum", label: "انجمن گروه" },
          { id: "members", label: "اعضا و ناظمان", count: members.length },
          { id: "docs", label: "اسناد گروه" },
        ]}
        active={tab}
        onChange={setTab}
      />

      {tab === "chat" && (
        <GroupChat
          groupId={id!}
          channelId={channelId}
          canModerate={canModerate}
          canPost={canPost}
          members={members.map((m) => ({ user: { id: m.user.id }, name: m.name }))}
        />
      )}

      {tab === "posts" && (
        <div className="space-y-4">
          {groupPosts.length === 0 ? (
            <EmptyState title="هنوز پستی در این گروه ثبت نشده" />
          ) : (
            groupPosts.map((p) => <PostCard key={p.id} post={p} />)
          )}
        </div>
      )}

      {tab === "forum" && (
        <EmptyState icon={<MessagesSquare size={20} />} title="تالار گفتگوی این گروه" description="موضوعات این گروه از ماژول انجمن سراسری فیلتر و این‌جا نمایش داده می‌شود." />
      )}

      {tab === "members" && (
        <GroupMembersPanel
          groupId={id!}
          members={members}
          setMembers={setMembers}
          canModerate={canModerate}
          slowMode={slowMode}
          onSlowMode={setSlowMode}
        />
      )}

      {tab === "docs" && (
        <EmptyState icon={<FileText size={20} />} title="اسناد گروه" description="اسناد بارگذاری‌شده در این گروه، از ماژول مدیریت دانش با دسته‌بندی این گروه نمایش داده می‌شود." />
      )}

      <Modal open={editOpen} onClose={() => setEditOpen(false)} title="ویرایش گروه" description="تغییرات برای همه‌ی اعضای گروه اعمال می‌شود.">
        <div className="space-y-3">
          <div>
            <label className="text-xs font-medium text-ink-600 block mb-1.5">نام گروه <span className="text-rose-500">*</span></label>
            <input value={form.name} onChange={(e) => setForm((f) => ({ ...f, name: e.target.value }))} className="input-field" />
          </div>
          <div>
            <label className="text-xs font-medium text-ink-600 block mb-1.5">توضیحات</label>
            <textarea value={form.description} onChange={(e) => setForm((f) => ({ ...f, description: e.target.value }))} className="input-field min-h-20" />
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="text-xs font-medium text-ink-600 block mb-1.5">دسته‌بندی <span className="text-rose-500">*</span></label>
              <input value={form.category} onChange={(e) => setForm((f) => ({ ...f, category: e.target.value }))} className="input-field" />
            </div>
          </div>
          <VisibilityPicker value={form.privacy} onChange={(v) => setForm((f) => ({ ...f, privacy: v }))} />
          <div className="flex items-center gap-2 pt-1">
            <Button variant="primary" className="flex-1 justify-center" onClick={saveEdit}>ذخیره تغییرات</Button>
            <Button variant="secondary" onClick={() => setEditOpen(false)}>انصراف</Button>
          </div>
        </div>
      </Modal>

      <Modal open={reportOpen} onClose={() => setReportOpen(false)} title={`گزارش تخلف — ${group.name}`} description="گزارش شما به‌صورت یک تیکت فوری برای ناظمان ثبت می‌شود.">
        <div className="space-y-3">
          <div>
            <label className="text-xs font-medium text-ink-600 block mb-1.5">شرح تخلف <span className="text-rose-500">*</span></label>
            <textarea value={reportText} onChange={(e) => setReportText(e.target.value)} className="input-field min-h-28" placeholder="چه چیزی را گزارش می‌کنید؟" />
          </div>
          <div className="flex items-center gap-2 pt-1">
            <Button variant="primary" className="flex-1 justify-center" onClick={sendReport}>ارسال گزارش</Button>
            <Button variant="secondary" onClick={() => setReportOpen(false)}>انصراف</Button>
          </div>
        </div>
      </Modal>
    </div>
  );
}
