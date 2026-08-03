import { describe, expect, it } from "vitest";
import { faMoney, faToNumber, toFaDigits, toJalali } from "../jalali";

describe("jalali/number helpers", () => {
  it("converts digits to Persian", () => {
    expect(toFaDigits("1405")).toBe("۱۴۰۵");
  });

  it("formats money in Persian with the rial suffix", () => {
    expect(faMoney(1000)).toContain("ریال");
    expect(faMoney(1000)).toMatch(/[۰-۹]/);
  });

  it("parses Persian money back to a number (round-trip)", () => {
    expect(faToNumber(faMoney(2500))).toBe(2500);
    expect(faToNumber("۱۲۳")).toBe(123);
  });

  it("renders a Jalali date for an ISO timestamp", () => {
    const out = toJalali("2026-07-22T10:00:00Z");
    expect(out).toMatch(/[۰-۹]{4}\/[۰-۹]{2}\/[۰-۹]{2}/);
  });

  it("is safe on empty/invalid input (never throws, never 'Invalid Date')", () => {
    expect(toJalali("")).toBe("");
    expect(toJalali(null)).toBe("");
    expect(toJalali("not-a-date")).toBe("");
  });
});
