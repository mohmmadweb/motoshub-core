import { describe, expect, it } from "vitest";

import { faNum, faDate } from "@/lib/format";

describe("format helpers", () => {
  it("faNum returns a non-empty localized string", () => {
    expect(typeof faNum(1234)).toBe("string");
    expect(faNum(1234).length).toBeGreaterThan(0);
  });
  it("faDate formats an ISO date to a non-empty string", () => {
    expect(faDate("2026-08-01T10:00:00Z").length).toBeGreaterThan(0);
  });
});
