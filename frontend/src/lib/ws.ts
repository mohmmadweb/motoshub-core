import { getToken } from "./http";

// Base for WebSocket connections. VITE_WS_BASE (e.g. ws://host:8015) or derive
// from the page origin (nginx proxies /ws to the ASGI backend in production).
const WS_BASE = (import.meta.env.VITE_WS_BASE as string) ||
  (typeof location !== "undefined" ? `${location.protocol === "https:" ? "wss" : "ws"}://${location.host}` : "");

/** Open a chat-channel socket (auth via ?token). Returns the WebSocket or null. */
export function openChannelSocket(channelId: string): WebSocket | null {
  const token = getToken();
  if (!token || !WS_BASE) return null;
  try {
    return new WebSocket(`${WS_BASE}/ws/chat/${channelId}/?token=${token}`);
  } catch {
    return null;
  }
}

/** Open the current user's DM socket (receives incoming DMs). */
export function openDmSocket(): WebSocket | null {
  const token = getToken();
  if (!token || !WS_BASE) return null;
  try {
    return new WebSocket(`${WS_BASE}/ws/dm/?token=${token}`);
  } catch {
    return null;
  }
}
