import { beforeEach, describe, expect, it } from "vitest";

import { useAuthStore } from "@/store/auth";
import { useToastStore } from "@/store/toast";

describe("auth store", () => {
  beforeEach(() => useAuthStore.getState().reset());

  it("can() reflects the user's permissions", () => {
    expect(useAuthStore.getState().can("news.create")).toBe(false);
    useAuthStore.getState().setUser({ permissions: ["news.create", "news.list"] } as never);
    expect(useAuthStore.getState().can("news.create")).toBe(true);
    expect(useAuthStore.getState().can("news.delete")).toBe(false);
  });

  it("reset clears the session", () => {
    useAuthStore.getState().setSession({ access: "a", refresh: "r", user: { name: "x" } as never });
    useAuthStore.getState().reset();
    expect(useAuthStore.getState().access).toBeNull();
    expect(useAuthStore.getState().user).toBeNull();
  });
});

describe("toast store", () => {
  beforeEach(() => useToastStore.setState({ toasts: [] }));

  it("push adds a toast; dismiss removes it", () => {
    useToastStore.getState().push("سلام", "success");
    const list = useToastStore.getState().toasts;
    expect(list).toHaveLength(1);
    expect(list[0].message).toBe("سلام");
    useToastStore.getState().dismiss(list[0].id);
    expect(useToastStore.getState().toasts).toHaveLength(0);
  });
});
