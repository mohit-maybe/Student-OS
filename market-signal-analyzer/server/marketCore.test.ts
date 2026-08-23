import { describe, expect, it } from "vitest";
import { computeOutcome, dedupeNews, fingerprintNews, paperOrderCost } from "./marketCore";

describe("market intelligence safeguards", () => {
  it("deduplicates the same normalized story while preserving first-seen provenance", () => {
    const fingerprint = fingerprintNews("A market catalyst", "https://source.example/story");
    const item = {
      providerItemId: "first", canonicalUrl: "https://source.example/story", title: "A market catalyst", summary: "", publisher: "Source", acquiredAt: new Date(), contentFingerprint: fingerprint, rawPayload: {},
    };
    expect(dedupeNews([item, { ...item, providerItemId: "second" }])).toHaveLength(1);
  });

  it("rejects evaluations that happen at or before the information cutoff", () => {
    const cutoff = new Date("2026-08-01T10:00:00.000Z");
    expect(() => computeOutcome({ direction: "upside", entryPrice: 100, observedPrice: 103, informationCutoffAt: cutoff, evaluatedAt: cutoff })).toThrow(/after the signal information cutoff/);
  });

  it("calculates directional outcomes after the cutoff without promising returns", () => {
    const result = computeOutcome({ direction: "downside", entryPrice: 100, observedPrice: 95, informationCutoffAt: new Date("2026-08-01T10:00:00.000Z"), evaluatedAt: new Date("2026-08-02T10:00:00.000Z") });
    expect(result).toMatchObject({ outcome: "favorable", noLookaheadConfirmed: true });
    expect(result.grossReturn).toBeCloseTo(-0.05);
  });

  it("requires a positive simulated quantity and price for paper orders", () => {
    expect(paperOrderCost(2, 125.5)).toBe(251);
    expect(() => paperOrderCost(0, 125.5)).toThrow(/positive finite/);
  });
});
