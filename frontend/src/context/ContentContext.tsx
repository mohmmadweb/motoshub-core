import { createContext, useContext, useEffect, useMemo, useRef, useState, type ReactNode } from "react";
import { MessagesSquare, NotebookPen, CalendarDays, Image, BookOpen, Newspaper, Users } from "lucide-react";
import type { ForumTopic, BlogPost, EventItem, MediaItem, KnowledgeDoc, NewsItem, Group } from "../data/types";
import { http } from "../lib/http";
import {
  fromNews, toNews, fromBlog, toBlog, fromEvent, toEvent, fromMedia, toMedia,
  fromKnowledge, toKnowledge, fromForum, toForum, fromGroup, toGroup,
} from "../lib/adapters";

export type PublicFeedItem = {
  id: string;
  module: "انجمن" | "بلاگ" | "رویداد" | "رسانه" | "دانش" | "اخبار" | "گروه‌ها";
  icon: typeof MessagesSquare;
  title: string;
  meta: string;
  to: string;
};

type SetFn<T> = (updater: (prev: T[]) => T[]) => void;

type ContentValue = {
  forumTopics: ForumTopic[]; setForumTopics: SetFn<ForumTopic>;
  blogPosts: BlogPost[]; setBlogPosts: SetFn<BlogPost>;
  events: EventItem[]; setEvents: SetFn<EventItem>;
  mediaItems: MediaItem[]; setMediaItems: SetFn<MediaItem>;
  knowledgeDocs: KnowledgeDoc[]; setKnowledgeDocs: SetFn<KnowledgeDoc>;
  newsItems: NewsItem[]; setNewsItems: SetFn<NewsItem>;
  groups: Group[]; setGroups: SetFn<Group>;
};

const ContentContext = createContext<ContentValue | null>(null);

/* eslint-disable @typescript-eslint/no-explicit-any */
interface ResCfg { path: string; from: (x: any) => any; to: (x: any) => any; }

const CFG: Record<string, ResCfg> = {
  forumTopics: { path: "/forum/topics", from: fromForum, to: toForum },
  blogPosts: { path: "/blogs", from: fromBlog, to: toBlog },
  events: { path: "/events", from: fromEvent, to: toEvent },
  mediaItems: { path: "/media", from: fromMedia, to: toMedia },
  knowledgeDocs: { path: "/knowledge", from: fromKnowledge, to: toKnowledge },
  newsItems: { path: "/news", from: fromNews, to: toNews },
  groups: { path: "/groups", from: fromGroup, to: toGroup },
};

export function ContentProvider({ children }: { children: ReactNode }) {
  const [forumTopics, setForumTopicsRaw] = useState<ForumTopic[]>([]);
  const [blogPosts, setBlogPostsRaw] = useState<BlogPost[]>([]);
  const [events, setEventsRaw] = useState<EventItem[]>([]);
  const [mediaItems, setMediaItemsRaw] = useState<MediaItem[]>([]);
  const [knowledgeDocs, setKnowledgeDocsRaw] = useState<KnowledgeDoc[]>([]);
  const [newsItems, setNewsItemsRaw] = useState<NewsItem[]>([]);
  const [groups, setGroupsRaw] = useState<Group[]>([]);

  // Latest state snapshot so the diffing setters always see current values.
  const cur = useRef<Record<string, any[]>>({});
  cur.current = { forumTopics, blogPosts, events, mediaItems, knowledgeDocs, newsItems, groups };

  const rawSetters: Record<string, (v: any[]) => void> = {
    forumTopics: setForumTopicsRaw, blogPosts: setBlogPostsRaw, events: setEventsRaw,
    mediaItems: setMediaItemsRaw, knowledgeDocs: setKnowledgeDocsRaw, newsItems: setNewsItemsRaw, groups: setGroupsRaw,
  };

  // Load every collection from the real API on mount.
  useEffect(() => {
    let cancelled = false;
    (async () => {
      await Promise.all(Object.keys(CFG).map(async (key) => {
        try {
          const rows = await http<any[]>(`${CFG[key].path}?page_size=100`);
          if (!cancelled) rawSetters[key](rows.map(CFG[key].from));
        } catch { /* leave empty on failure */ }
      }));
    })();
    return () => { cancelled = true; };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  /** set* that mirrors the update locally AND persists the diff to the API. */
  function makeSetter(key: string): SetFn<any> {
    const { path, to, from } = CFG[key];
    return (updater) => {
      const prev = cur.current[key] as any[];
      const next = updater(prev);
      rawSetters[key](next);
      const prevById = new Map(prev.map((x) => [x.id, x]));
      const nextById = new Map(next.map((x) => [x.id, x]));
      next.filter((x) => !prevById.has(x.id)).forEach((item) => {
        http(path, { method: "POST", body: JSON.stringify(to(item)) })
          .then((created: any) => rawSetters[key]((cur.current[key] as any[]).map((c) => (c.id === item.id ? from(created) : c))))
          .catch(() => {});
      });
      prev.filter((x) => !nextById.has(x.id)).forEach((item) => {
        http(`${path}/${item.id}`, { method: "DELETE" }).catch(() => {});
      });
      next.filter((x) => prevById.has(x.id) && JSON.stringify(x) !== JSON.stringify(prevById.get(x.id))).forEach((item) => {
        http(`${path}/${item.id}`, { method: "PATCH", body: JSON.stringify(to(item)) }).catch(() => {});
      });
    };
  }

  const value = useMemo<ContentValue>(() => ({
    forumTopics, setForumTopics: makeSetter("forumTopics"),
    blogPosts, setBlogPosts: makeSetter("blogPosts"),
    events, setEvents: makeSetter("events"),
    mediaItems, setMediaItems: makeSetter("mediaItems"),
    knowledgeDocs, setKnowledgeDocs: makeSetter("knowledgeDocs"),
    newsItems, setNewsItems: makeSetter("newsItems"),
    groups, setGroups: makeSetter("groups"),
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }), [forumTopics, blogPosts, events, mediaItems, knowledgeDocs, newsItems, groups]);

  return <ContentContext.Provider value={value}>{children}</ContentContext.Provider>;
}

export function useContent() {
  const ctx = useContext(ContentContext);
  if (!ctx) throw new Error("useContent must be used within ContentProvider");
  return ctx;
}

export function usePublicFeed(): PublicFeedItem[] {
  const { forumTopics, blogPosts, events, mediaItems, knowledgeDocs, newsItems, groups } = useContent();
  return useMemo(() => {
    const items: PublicFeedItem[] = [];
    forumTopics.filter((t) => t.visibility === "عمومی").forEach((t) => items.push({ id: `forum-${t.id}`, module: "انجمن", icon: MessagesSquare, title: t.title, meta: `توسط ${t.author} · دسته: ${t.category}`, to: `/dashboard/forum/${t.id}` }));
    blogPosts.filter((b) => b.visibility === "عمومی").forEach((b) => items.push({ id: `blog-${b.id}`, module: "بلاگ", icon: NotebookPen, title: b.title, meta: `${b.author} · ${b.date}`, to: "/dashboard/blog" }));
    events.filter((e) => e.visibility === "عمومی").forEach((e) => items.push({ id: `event-${e.id}`, module: "رویداد", icon: CalendarDays, title: e.title, meta: `${e.jalaliDate} · ${e.location}`, to: "/dashboard/events" }));
    mediaItems.filter((m) => m.visibility === "عمومی").forEach((m) => items.push({ id: `media-${m.id}`, module: "رسانه", icon: Image, title: m.title, meta: `${m.album} · ${m.uploadedBy}`, to: "/dashboard/media" }));
    knowledgeDocs.filter((d) => d.visibility === "عمومی").forEach((d) => items.push({ id: `doc-${d.id}`, module: "دانش", icon: BookOpen, title: d.title, meta: `${d.owner} · ${d.updatedAt}`, to: "/dashboard/knowledge" }));
    newsItems.filter((n) => n.visibility === "عمومی").forEach((n) => items.push({ id: `news-${n.id}`, module: "اخبار", icon: Newspaper, title: n.title, meta: n.date, to: "/dashboard/news" }));
    groups.filter((g) => g.privacy === "عمومی").forEach((g) => items.push({ id: `group-${g.id}`, module: "گروه‌ها", icon: Users, title: g.name, meta: `${g.members.toLocaleString("fa-IR")} عضو · ${g.category}`, to: "/dashboard/groups" }));
    return items;
  }, [forumTopics, blogPosts, events, mediaItems, knowledgeDocs, newsItems, groups]);
}
