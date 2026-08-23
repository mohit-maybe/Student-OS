export const errorCategories = [
  "no_material_error",
  "catalyst_misread",
  "timing_error",
  "regime_shift",
  "risk_sizing",
  "execution_assumption",
  "data_gap",
  "unclassifiable",
] as const;

export type ErrorCategory = (typeof errorCategories)[number];
export type TradeSide = "long" | "short";

export function calculateTradePnl(input: { side: TradeSide; entryPrice: number; exitPrice: number; quantity: number; fees?: number }) {
  if (![input.entryPrice, input.exitPrice, input.quantity].every(value => Number.isFinite(value) && value > 0)) {
    throw new Error("Entry price, exit price, and quantity must be positive finite values.");
  }
  const fees = input.fees ?? 0;
  if (!Number.isFinite(fees) || fees < 0) throw new Error("Fees must be a non-negative finite value.");
  const grossPnl = (input.exitPrice - input.entryPrice) * input.quantity * (input.side === "long" ? 1 : -1);
  const netPnl = grossPnl - fees;
  const returnPct = netPnl / (input.entryPrice * input.quantity);
  return { grossPnl, netPnl, returnPct, outcome: Math.abs(returnPct) < 0.0025 ? "flat" as const : returnPct > 0 ? "win" as const : "loss" as const };
}

export function validateLearningRecord(input: { decisionAt: Date; evaluatedAt: Date; errorCategory: ErrorCategory; lesson: string }) {
  if (input.evaluatedAt <= input.decisionAt) throw new Error("Trade learning must be recorded after the immutable decision timestamp.");
  if (input.lesson.trim().length < 12) throw new Error("A reusable lesson must be specific enough to review, not a generic conclusion.");
  return { learningStatus: "pending_human_review" as const, errorCategory: input.errorCategory };
}

export const demoTradeLearning = [
  {
    id: "preview-nova", symbol: "NOVA", side: "long", netPnl: 123.48, outcome: "win", decisionAt: "2026-08-22T09:35:00.000Z", evaluatedAt: "2026-08-22T16:00:00.000Z",
    sources: ["BBC News — Business · supply-chain item", "Signal context snapshot · v1"], errorCategory: "no_material_error", lesson: "Do not promote one favorable result into a permanent rule; wait for a regime-segmented sample.", status: "preview_only",
  },
  {
    id: "preview-arcc", symbol: "ARCC", side: "long", netPnl: -61.16, outcome: "loss", decisionAt: "2026-08-22T10:10:00.000Z", evaluatedAt: "2026-08-22T16:00:00.000Z",
    sources: ["BBC News — Business · macro context", "Signal context snapshot · v1"], errorCategory: "regime_shift", lesson: "When rate context conflicts with the catalyst, reduce confidence and require separate regime confirmation.", status: "preview_only",
  },
];
