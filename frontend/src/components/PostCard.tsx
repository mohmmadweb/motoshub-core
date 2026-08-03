import { useState } from "react";
import { Heart, MessageCircle, Share2, BarChart3, FileText, Pin } from "lucide-react";
import Avatar from "./Avatar";
import Badge from "./ui/Badge";
import { type Post } from "../data/mock";
import { http } from "../lib/http";

// Real posts carry their author/group/like-state inline (see fromPost).
type FeedPost = Post & { _authorName?: string; _authorColor?: string; _groupName?: string; _myLike?: boolean };

export default function PostCard({ post }: { post: FeedPost }) {
  const [likes, setLikes] = useState(post.likes);
  const [mine, setMine] = useState(!!post._myLike);

  const toggleLike = () => {
    setLikes((n) => n + (mine ? -1 : 1));
    setMine((v) => !v);
    http<{ likes: number; my_like: boolean }>(`/posts/${post.id}/like`, { method: "POST" })
      .then((r) => { setLikes(r.likes); setMine(r.my_like); })
      .catch(() => {});
  };

  return (
    <article className="card p-4">
      <div className="flex items-start gap-3">
        <Avatar name={post._authorName ?? "?"} color={post._authorColor} />
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 text-sm flex-wrap">
            <span className="font-semibold text-ink-900">{post._authorName}</span>
            {post._groupName && (
              <>
                <span className="text-ink-300">در</span>
                <span className="text-brand-600 font-medium">{post._groupName}</span>
              </>
            )}
            {post.pinned && (
              <Badge tone="brand" icon={<Pin size={11} />}>
                سنجاق‌شده
              </Badge>
            )}
          </div>
          <p className="text-xs text-ink-400 mt-0.5">{post.time}</p>

          <p className="mt-3 text-sm leading-7 text-ink-800">{post.content}</p>

          {post.attachment?.type === "poll" && (
            <div className="mt-3 rounded-lg border border-ink-200 p-3 bg-ink-50 text-sm">
              <p className="font-medium mb-2 flex items-center gap-1.5 text-ink-800">
                <BarChart3 size={14} className="text-brand-600" /> نظرسنجی: {post.attachment.label}
              </p>
              <div className="space-y-1.5">
                <div className="h-1.5 rounded-full bg-ink-200 overflow-hidden">
                  <div className="h-full bg-brand-500" style={{ width: "62%" }} />
                </div>
                <p className="text-xs text-ink-400">۶۲٪ از ۴۸ رأی</p>
              </div>
            </div>
          )}

          {post.attachment?.type === "doc" && (
            <div className="mt-3 flex items-center gap-2 rounded-lg border border-ink-200 p-3 bg-ink-50 text-sm">
              <FileText size={16} className="text-ink-500" />
              <span className="font-medium">{post.attachment.label}</span>
            </div>
          )}

          <div className="mt-3 flex items-center gap-1.5 flex-wrap">
            {post.tags.map((t) => (
              <Badge key={t} tone="neutral">
                #{t}
              </Badge>
            ))}
          </div>

          <div className="mt-3 flex items-center gap-5 text-ink-400 text-xs border-t border-ink-100 pt-3">
            <button onClick={toggleLike} className={`flex items-center gap-1.5 hover:text-rose-600 ${mine ? "text-rose-600" : ""}`}>
              <Heart size={14} fill={mine ? "currentColor" : "none"} /> {likes.toLocaleString("fa-IR")}
            </button>
            <button className="flex items-center gap-1.5 hover:text-brand-600">
              <MessageCircle size={14} /> {post.comments}
            </button>
            <button className="flex items-center gap-1.5 hover:text-ink-700">
              <Share2 size={14} /> اشتراک‌گذاری
            </button>
          </div>
        </div>
      </div>
    </article>
  );
}
