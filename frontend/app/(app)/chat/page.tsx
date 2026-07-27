"use client";
import { useQuery } from "@tanstack/react-query";
import { Send } from "lucide-react";
import { useEffect, useRef, useState } from "react";

import Button from "@/components/ui/Button";
import Card from "@/components/ui/Card";
import Input from "@/components/ui/Input";
import { api, type Envelope } from "@/lib/api";
import { faDateTime } from "@/lib/format";
import { useAuthStore } from "@/store/auth";
import type { Channel, ChatMessage } from "@/types";

export default function ChatPage() {
  const access = useAuthStore((s) => s.access);
  const [activeId, setActiveId] = useState<string | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [draft, setDraft] = useState("");
  const wsRef = useRef<WebSocket | null>(null);
  const scrollRef = useRef<HTMLDivElement>(null);

  const { data: channelsEnv } = useQuery({
    queryKey: ["chat/channels"],
    queryFn: async () => (await api.get<Envelope<Channel[]>>("/chat/channels")).data,
  });
  const channels = channelsEnv?.data ?? [];

  useEffect(() => {
    if (!activeId && channels.length) setActiveId(channels[0].id);
  }, [channels, activeId]);

  // Load history + open the WebSocket when the active channel changes.
  useEffect(() => {
    if (!activeId) return;
    let ws: WebSocket | null = null;
    (async () => {
      const hist = await api.get<ChatMessage[] | Envelope<ChatMessage[]>>(`/chat/channels/${activeId}/messages`);
      const list = Array.isArray(hist.data) ? hist.data : hist.data.data;
      setMessages(list);
      const proto = window.location.protocol === "https:" ? "wss" : "ws";
      ws = new WebSocket(`${proto}://${window.location.host}/ws/chat/${activeId}/?token=${access}`);
      ws.onmessage = (e) => setMessages((prev) => [...prev, JSON.parse(e.data)]);
      wsRef.current = ws;
    })();
    return () => ws?.close();
  }, [activeId, access]);

  useEffect(() => { scrollRef.current?.scrollTo(0, scrollRef.current.scrollHeight); }, [messages]);

  const send = () => {
    const text = draft.trim();
    if (!text || !wsRef.current || wsRef.current.readyState !== WebSocket.OPEN) return;
    wsRef.current.send(JSON.stringify({ text }));
    setDraft("");
  };

  return (
    <div className="flex h-[calc(100vh-8rem)] gap-4">
      {/* channels */}
      <Card className="hidden w-56 shrink-0 overflow-y-auto p-2 sm:block">
        {channels.map((ch) => (
          <button key={ch.id} onClick={() => setActiveId(ch.id)}
            className={`mb-1 block w-full rounded-lg px-3 py-2 text-right text-sm ${activeId === ch.id ? "bg-brand-50 font-semibold text-brand-700" : "text-ink-600 hover:bg-ink-100"}`}>
            # {ch.name}
          </button>
        ))}
        {channels.length === 0 && <p className="p-3 text-xs text-ink-400">کانالی نیست.</p>}
      </Card>

      {/* messages */}
      <Card className="flex min-w-0 flex-1 flex-col">
        <div ref={scrollRef} className="flex-1 space-y-3 overflow-y-auto p-4">
          {messages.map((m) => (
            <div key={m.id} className="flex flex-col">
              <span className="text-xs text-ink-400">{m.author?.name ?? "—"} · {faDateTime(m.created_at)}</span>
              <span className="mt-0.5 rounded-lg bg-ink-100 px-3 py-2 text-sm text-ink-800">{m.text}</span>
            </div>
          ))}
          {messages.length === 0 && <p className="py-8 text-center text-sm text-ink-400">هنوز پیامی نیست.</p>}
        </div>
        <div className="flex items-center gap-2 border-t border-ink-200 p-3">
          <Input value={draft} onChange={(e) => setDraft(e.target.value)} onKeyDown={(e) => e.key === "Enter" && send()} placeholder="پیام بنویسید…" />
          <Button icon={<Send size={16} />} onClick={send}>ارسال</Button>
        </div>
      </Card>
    </div>
  );
}
