import { describe, expect, it } from "vitest";
import { appRouter } from "./routers";
import type { TrpcContext } from "./_core/context";

const publicContext = {
  user: null,
  req: { headers: {}, protocol: "https" },
  res: {},
} as TrpcContext;

describe("market router public responses", () => {
  it("exposes explicit disconnected and paper-only provider states", async () => {
    const caller = appRouter.createCaller(publicContext);
    const status = await caller.market.connectionStatus();
    expect(status.marketData.status).toBe("unconfigured");
    expect(status.trading.status).toBe("paper_only");
    expect(status.airtable.status).toBe("unconfigured");
  });

  it("labels the portfolio fixture as illustrative rather than market data", async () => {
    const caller = appRouter.createCaller(publicContext);
    const portfolio = await caller.market.paperPortfolio();
    expect(portfolio.positions).toHaveLength(3);
    expect(portfolio.label).toMatch(/Illustrative simulation data/);
  });
});
