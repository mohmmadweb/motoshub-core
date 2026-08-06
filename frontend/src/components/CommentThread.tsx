import { useCallback, useEffect, useState } from "react";
import { Send, MessageCircle, Trash2 } from "lucide-react";
import { http, apiMessage, getUser } from "../lib/http";
import { relativeFa } from "../lib/jalali";
import Avatar from "./Avatar";
import Button from "./ui/Button";
import { useToast } from "./ui/ToastProvider";

type Comment = {
  id: string;
  body: string;
  when: string;
  author: string;
  authorId: string;
  avatarColor: string;
};

/**
 * Comments on any content item, backed by /comments (kind + object_id).
 *
 * The detail pages each had a comment box wired to nothing: you could type and
 * press «ارسال» and the text simply vanished. One component now serves all of
 * them so the box, the list and the delete all talk to the same endpoint.
 */
export default function CommentThread({
  kind,
  objectId,
  title = "نظرات",
  placeholder = "نظر خود را بنویسید…",
}: {
  kind: "news" | "blog" | "event" | "media" | "doc" | "forum";
  objectId: string;
  title?: string;
  placeholder?: string;
}) {
  const { notify } = useToast();
  const [items, setItems] = useState<Comment[]>([]);
  const [draft, setDraft] = useState("");
  const [sending, setSending] = useState(false);
  const me = getUser() as { id?: string } | null;

  const load = useCallback(
    () =>
      http<Record<string, unknown>[]>(`/comments?kind=${kind}&object_id=${objectId}&page_size=100`)
        .then((rows) =>
          setItems(
            rows.map((r) => {
              const author = (r.author ?? {}) as { id?: string; name?: string; avatar_color?: string };
              return {
                id: String(r.id),
                body: String(r.body ?? ""),
                when: relativeFa(r.created_at as string),
                author: author.name ?? "—",
                authorId: author.id ?? "",
                avatarColor: author.avatar_color ?? "#1f4f99",
              };
            }),
          ),
        )
        .catch(() => setItems([])),
    [kind, objectId],
  );

  useEffect(() => { load(); }, [load]);

  const send = async () => {
    if (!draft.trim()) {
      notify("متن نظر خالی است.", "warning");
      return;
    }
    setSending(true);
    try {
      await http("/comments", {
        method: "POST",
        body: JSON.stringify({ kind, object_id: objectId, body: draft.trim() }),
      });
      await load();
      setDraft("");
      notify("نظر شما ثبت شد.");
    } catch (err) {
      notify(apiMessage(err, "ثبت نظر ناموفق بود."), "warning");
    } finally {
      setSending(false);
    }
  };

  const remove = async (c: Comment) => {
    try {
      await http(`/comments/${c.id}`, { method: "DELETE" });
      await load();
      notify("نظر حذف شد.", "info");
    } catch (err) {
      notify(apiMessage(err, "حذف نظر ناموفق بود."), "warning");
    }
  };

  return (
    <div className="card p-4">
      <p className="text-xs font-semibold text-ink-600 mb-3 flex items-center gap-1.5">
        <MessageCircle size={13} /> {title}
        {items.length > 0 && <span className="text-ink-400">({items.length.toLocaleString("fa-IR")})</span>}
      </p>

      {items.length > 0 && (
        <div className="space-y-3 mb-4">
          {items.map((c) => (
            <div key={c.id} className="group flex items-start gap-2.5">
              <Avatar name={c.author} color={c.avatarColor} size={30} />
              <div className="min-w-0 flex-1">
                <p className="text-[11.5px] text-ink-500">
                  <span className="font-medium text-ink-800">{c.author}</span> · {c.when}
                </p>
                <p className="text-[13px] text-ink-700 leading-6 whitespace-pre-wrap mt-0.5">{c.body}</p>
              </div>
              {/* Only the writer may remove their own comment. */}
              {me?.id && c.authorId === me.id && (
                <button
                  onClick={() => remove(c)}
                  className="opacity-0 group-hover:opacity-100 p-1 text-ink-300 hover:text-rose-600 transition-opacity"
                  title="حذف نظر"
                >
                  <Trash2 size={13} />
                </button>
              )}
            </div>
          ))}
        </div>
      )}

      <div className="flex items-center gap-2">
        <input
          className="input-field flex-1"
          placeholder={placeholder}
          value={draft}
          onChange={(e) => setDraft(e.target.value)}
          onKeyDown={(e) => { if (e.key === "Enter") send(); }}
        />
        <Button variant="primary" icon={<Send size={14} />} onClick={send} disabled={sending}>
          ارسال
        </Button>
      </div>
    </div>
  );
}
