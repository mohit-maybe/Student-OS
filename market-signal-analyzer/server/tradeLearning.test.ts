import { describe, expect, it } from "vitest";
import { calculateTradePnl, validateLearningRecord } from "./tradeLearning";

describe("paper-trade learning safeguards", () => {
  it("calculates long and short paper P&L without altering the original decision", () => {
    expect(calculateTradePnl({ side: "long", entryPrice: 100, exitPrice: 105, quantity: 3, fees: 1 })).toMatchObject({ grossPnl: 15, netPnl: 14, outcome: "win" });
    expect(calculateTradePnl({ side: "short", entryPrice: 100, exitPrice: 95, quantity: 2 })).toMatchObject({ grossPnl: 10, outcome: "win" });
  });

  it("requires a post-decision evaluation and a reviewable lesson", () => {
    const decisionAt = new Date("2026-08-20T09:30:00.000Z");
    expect(() => validateLearningRecord({ decisionAt, evaluatedAt: decisionAt, errorCategory: "timing_error", lesson: "Specific lesson" })).toThrow(/after the immutable decision/);
    expect(validateLearningRecord({ decisionAt, evaluatedAt: new Date("2026-08-21T09:30:00.000Z"), errorCategory: "timing_error", lesson: "Require a subsequent catalyst confirmation before re-entering." })).toMatchObject({ learningStatus: "pending_human_review" });
    expect(validateLearningRecord({ decisionAt, evaluatedAt: new Date("2026-08-21T09:30:00.000Z"), errorCategory: "data_gap", lesson: "Record an unavailable source field rather than infer a missing catalyst." })).toMatchObject({ errorCategory: "data_gap", learningStatus: "pending_human_review" });
  });
});
