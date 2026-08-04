import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { Flag, UserPlus, FileText, MessagesSquare } from "lucide-react";
import { type Post } from "../data/types";
import { http } from "../lib/http";
import { fromPost } from "../lib/adapters";
import { useContent } from "../context/ContentContext";
import PostCard from "../components/PostCard";
import Tabs from "../components/ui/Tabs";
import Button from "../components/ui/Button";
import EmptyState from "../components/ui/EmptyState";
import { VisibilityBadge, VisibilityToggle } from "../components/ui/VisibilityControl";
import { useToast } from "../components/ui/ToastProvider";
import GroupChat from "../components/GroupChat";
import GroupMembersPanel, { type GroupMember } from "../components/GroupMembersPanel";
import { getUser } from "../lib/http";

type TabId = "chat" | "posts" | "forum" | "members" | "docs";

export default function GroupDetail() {
  const { id } = useParams();
  const { groups, setGroups } = useContent();
  const { notify } = useToast();
  const group = groups.find((g) => g.id === id);
  const [tab, setTab] = useState<TabId>("chat");
  const [groupPosts, setGroupPosts] = useState<Post[]>([]);
  const [members, setMembers] = useState<GroupMember[]>([]);
  const [channelId, setChannelId] = useState<string | undefined>();
  const [slowMode, setSlowMode] = useState(0);
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
  const canModerate = !!myMembership?.can_moderate;
  const canPost = !!myMembership && !myMembership.banned;

  const togglePrivacy = () => {
    const next = group.privacy === "عمومی" ? "خصوصی" : "عمومی";
    setGroups((prev) => prev.map((g) => (g.id === group.id ? { ...g, privacy: next } : g)));
    notify(`گروه «${group.name}» به ${next} تغییر یافت.`, next === "عمومی" ? "success" : "info");
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
          <VisibilityToggle visibility={group.privacy} onChange={togglePrivacy} size="sm" />
          <Button variant="secondary" size="sm" icon={<Flag size={13} />}>
            گزارش تخلف
          </Button>
          <Button variant="primary" size="sm" icon={<UserPlus size={13} />}>
            عضو شده‌اید
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
    </div>
  );
}
