import { describe, expect, it } from "vitest";
import {
  fromNews, fromProject, fromTask, fromMilestone, fromRisk,
  fromCompetition, fromChallenge, fromAwardTrack, fromPost, fromTender,
} from "../adapters";

describe("adapters map backend enums to the prototype's Persian labels", () => {
  it("project health", () => {
    expect(fromProject({ id: "1", name: "پ", health: "yellow", progress: 40 }).health).toBe("زرد");
    expect(fromProject({ id: "1", name: "پ", health: "red" }).health).toBe("قرمز");
  });

  it("task status + priority, with sane fallbacks", () => {
    const t = fromTask({ id: "t", title: "x", status: "in_progress", priority: "high", progress: 20 });
    expect(t.status).toBe("در حال انجام");
    expect(t.priority).toBe("زیاد");
    expect(t.assignee).toBe("بدون مسئول"); // no assignee → placeholder, never "undefined"
    expect(fromTask({ id: "t", title: "x" }).status).toBe("برنامه‌ریزی"); // default
  });

  it("milestone + risk", () => {
    expect(fromMilestone({ id: "m", title: "x", status: "at_risk", due: "" }).status).toBe("در خطر");
    expect(fromMilestone({ id: "m", title: "x", status: "at_risk", due: "" }).due).toBe("—");
    const r = fromRisk({ id: "r", title: "x", severity: "critical", probability: "high", status: "mitigating" });
    expect([r.severity, r.probability, r.status]).toEqual(["بحرانی", "زیاد", "در حال رفع"]);
  });

  it("competition + challenge", () => {
    const c = fromCompetition({ id: "c", title: "م", status: "judging", entries: [{ id: "e", by: "a", title: "t", votes: 3, my_vote: true }] });
    expect(c.status).toBe("در حال داوری");
    expect(c.entries[0].myVote).toBe(true); // snake_case → camelCase
    expect(fromChallenge({ id: "h", title: "چ", kind: "collective", status: "ended", joined: 2 }).kind).toBe("همگانی");
  });

  it("tender method/stage", () => {
    const t = fromTender({ id: "t", title: "x", method: "no_formality", stage: "commission", participants: 2 });
    expect(t.method).toBe("ترک تشریفات");
    expect(t.stage).toBe("کمیسیون معاملات");
  });

  it("award track counts judged as scored+finalist", () => {
    const tr = fromAwardTrack({ id: "a", title: "محور", categories: ["x"], submission_count: 3,
      entries: [{ status: "scored" }, { status: "finalist" }, { status: "judging" }] });
    expect(tr.submissions).toBe(3);
    expect(tr.judged).toBe(2);
  });

  it("post carries author/group/like state inline", () => {
    const p = fromPost({ id: "p", content: "متن", author: { id: "u", name: "علی", avatar_color: "#111" },
      group_name: "گروه", likes: 2, my_like: true, tags: ["a"], created_at: new Date().toISOString() });
    expect(p._authorName).toBe("علی");
    expect(p._groupName).toBe("گروه");
    expect(p._myLike).toBe(true);
    expect(p.likes).toBe(2);
  });

  it("news maps visibility", () => {
    expect(fromNews({ id: "n", title: "t", summary: "s", visibility: "public", created_at: new Date().toISOString() }).visibility).toBe("عمومی");
  });
});
