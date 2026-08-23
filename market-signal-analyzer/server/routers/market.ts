import { TRPCError } from "@trpc/server";
import { z } from "zod";
import { getAirtableStatus, syncNewsToAirtable } from "../airtable";
import { invokeLLM } from "../_core/llm";
import { protectedProcedure, publicProcedure, router } from "../_core/trpc";
import { listRetainedNews, retainNewsItems } from "../db";
import { computeOutcome, fetchGdeltNews, paperOrderCost, paperPortfolioFixture, type SignalDirection } from "../marketCore";

const analysisSchema = {
  name: "evidence_linked_market_hypothesis",
  strict: true,
  schema: {
    type: "object",
    properties: {
      assetSymbols: { type: "array", items: { type: "string" } },
      assetClass: { type: "string", enum: ["equity", "crypto", "etf", "macro"] },
      catalyst: { type: "string" },
      direction: { type: "string", enum: ["upside", "downside", "mixed", "watch"] },
      sentiment: { type: "string", enum: ["positive", "negative", "neutral", "mixed"] },
      confidence: { type: "integer", minimum: 0, maximum: 100 },
      hypothesis: { type: "string" },
      uncertainty: { type: "string" },
      evidenceExcerpt: { type: "string" },
    },
    required: ["assetSymbols", "assetClass", "catalyst", "direction", "sentiment", "confidence", "hypothesis", "uncertainty", "evidenceExcerpt"],
    additionalProperties: false,
  },
} as const;

export const marketRouter = router({
  connectionStatus: publicProcedure.query(() => ({
    globalNews: { status: "connected", detail: "Public GDELT discovery is available on refresh." },
    marketData: { status: "unconfigured", detail: "Add a licensed market-data provider before using live prices for evaluation." },
    airtable: getAirtableStatus(),
    trading: { status: "paper_only", detail: "Real-money broker routing is intentionally disabled." },
  })),

  refreshGlobalNews: publicProcedure
    .input(z.object({ query: z.string().min(2).max(240).optional() }).optional())
    .query(async ({ input }) => {
      try {
        const items = await fetchGdeltNews(input?.query);
        const provider = items[0]?.publisher === "BBC News — Business" ? "BBC News — Business RSS (fallback)" : "GDELT DOC 2.0";
        return { provider, fetchedAt: new Date(), items, mode: "retrieved" as const };
      } catch (error) {
        return { provider: "GDELT DOC 2.0", fetchedAt: new Date(), items: [], mode: "unavailable" as const, error: error instanceof Error ? error.message : "News refresh unavailable" };
      }
    }),

  retainGlobalNews: protectedProcedure
    .input(z.object({ query: z.string().min(2).max(240).optional() }).optional())
    .mutation(async ({ input }) => {
      const items = await fetchGdeltNews(input?.query);
      const persisted = await retainNewsItems(items);
      const airtable = await syncNewsToAirtable(items);
      const provider = items[0]?.publisher === "BBC News — Business" ? "BBC News — Business RSS (fallback)" : "GDELT DOC 2.0";
      return { provider, fetchedAt: new Date(), ...persisted, airtable };
    }),

  retainedNews: protectedProcedure.query(async () => ({
    items: await listRetainedNews(),
    note: "Persisted source records are listed independently from the current discovery batch.",
  })),

  analyzeEvidence: protectedProcedure
    .input(z.object({ title: z.string().min(1).max(300), publisher: z.string().min(1).max(160), canonicalUrl: z.string().url(), publishedAt: z.date().optional(), summary: z.string().max(5000).default("") }))
    .mutation(async ({ input }) => {
      const informationCutoffAt = new Date();
      const response = await invokeLLM({
        model: "gpt-5-mini",
        messages: [
          { role: "system", content: "You analyze only the supplied news record. Produce an evidence-linked research hypothesis, not investment advice. Do not invent facts, prices, or sources. Treat forecast direction as uncertain, describe the strongest uncertainty, and use the supplied title or summary as the evidence excerpt." },
          { role: "user", content: `SOURCE: ${input.publisher}\nURL: ${input.canonicalUrl}\nPUBLISHED: ${input.publishedAt?.toISOString() ?? "unknown"}\nTITLE: ${input.title}\nSUMMARY: ${input.summary || "No summary supplied."}` },
        ],
        response_format: { type: "json_schema", json_schema: analysisSchema },
      });
      const content = response.choices[0]?.message.content;
      if (typeof content !== "string") throw new TRPCError({ code: "INTERNAL_SERVER_ERROR", message: "Analysis provider returned no structured result." });
      return { analysis: JSON.parse(content), informationCutoffAt, source: { publisher: input.publisher, canonicalUrl: input.canonicalUrl } };
    }),

  createPaperOrder: protectedProcedure
    .input(z.object({ symbol: z.string().min(1).max(16).transform(value => value.toUpperCase()), assetClass: z.enum(["equity", "crypto", "etf"]), side: z.enum(["buy", "sell"]), quantity: z.number().positive(), referencePrice: z.number().positive(), rationale: z.string().min(12).max(1000), informationCutoffAt: z.date() }))
    .mutation(({ input }) => ({
      id: `paper-${crypto.randomUUID()}`,
      status: "queued" as const,
      notional: paperOrderCost(input.quantity, input.referencePrice),
      executedWithRealMoney: false,
      rationale: input.rationale,
      informationCutoffAt: input.informationCutoffAt,
      guardrail: "Paper-trading order only. No broker, wallet, exchange, or real-money order route is connected.",
    })),

  evaluateSignal: protectedProcedure
    .input(z.object({ direction: z.enum(["upside", "downside", "mixed", "watch"]), entryPrice: z.number().positive(), observedPrice: z.number().positive(), informationCutoffAt: z.date(), evaluatedAt: z.date() }))
    .mutation(({ input }) => computeOutcome(input as { direction: SignalDirection; entryPrice: number; observedPrice: number; informationCutoffAt: Date; evaluatedAt: Date })),

  paperPortfolio: publicProcedure.query(() => ({
    ...paperPortfolioFixture,
    label: "Illustrative simulation data — connect a market-data provider and create paper orders to begin evidence-based evaluation.",
  })),
});
