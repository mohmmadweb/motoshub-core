// @vitest-environment jsdom
import { beforeEach, describe, expect, it, vi } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";

// The component pulls in toast/confirm providers and a WebSocket; stub the
// boundaries so the test exercises GroupChat's own rendering logic.
vi.mock("../ui/ToastProvider", () => ({ useToast: () => ({ notify: vi.fn() }) }));
vi.mock("../ui/ConfirmProvider", () => ({ useConfirm: () => vi.fn() }));
vi.mock("../../lib/ws", () => ({ openChannelSocket: () => null }));

const httpMock = vi.fn();
vi.mock("../../lib/http", () => ({
  http: (...a: unknown[]) => httpMock(...a),
  getUser: () => ({ id: "me", name: "من" }),
}));

import GroupChat from "../GroupChat";

const msg = (over: Record<string, unknown> = {}) => ({
  id: "m1", author: { id: "u2", name: "علی" }, text: "سلام گروه", pinned: false,
  deleted: false, edited_at: null, forwarded_from: "", attachment: null, mentions: [],
  reply_to: null, reactions: [], created_at: "2026-01-01T10:00:00Z", ...over,
});

const renderChat = () =>
  render(<GroupChat groupId="g1" canModerate canPost members={[]} />);

describe("GroupChat", () => {
  beforeEach(() => httpMock.mockReset());

  const serving = (rows: unknown[]) =>
    httpMock.mockImplementation((path?: string) =>
      Promise.resolve(typeof path === "string" && path.includes("/messages") ? rows : []));

  it("renders messages returned by the API", async () => {
    serving([msg()]);
    renderChat();
    expect(await screen.findByText("سلام گروه")).toBeTruthy();
    expect(screen.getByText("علی")).toBeTruthy();
  });

  it("never shows the text of a deleted message", async () => {
    serving([msg({ deleted: true, text: "" })]);
    renderChat();
    expect(await screen.findByText("این پیام حذف شد")).toBeTruthy();
  });

  it("shows an empty state when the group has no messages", async () => {
    httpMock.mockResolvedValue([]);
    renderChat();
    expect(await screen.findByText("هنوز پیامی نیست")).toBeTruthy();
  });

  it("tells non-members they cannot post", async () => {
    httpMock.mockResolvedValue([]);
    render(<GroupChat groupId="g1" canModerate={false} canPost={false} members={[]} />);
    await waitFor(() => expect(screen.getByText("برای ارسال پیام باید عضو گروه باشید.")).toBeTruthy());
  });

  it("renders an attachment as a link with its size", async () => {
    serving([msg({ text: "", attachment: { kind: "doc", name: "گزارش.pdf", size: "1.2MB", url: "/media/x.pdf" } })]);
    renderChat();
    expect(await screen.findByText("گزارش.pdf")).toBeTruthy();
    expect(screen.getByText("1.2MB")).toBeTruthy();
  });
});
