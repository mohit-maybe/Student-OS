import { createHash } from "node:crypto";

export type NormalizedNewsItem = {
  providerItemId: string;
  canonicalUrl: string;
  title: string;
  summary: string;
  publisher: string;
  publisherUrl?: string;
  imageUrl?: string;
  language?: string;
  publishedAt?: Date;
  acquiredAt: Date;
  contentFingerprint: string;
  rawPayload: Record<string, unknown>;
};

export type SignalDirection = "upside" | "downside" | "mixed" | "watch";
export type SignalOutcome = "pending" | "favorable" | "unfavorable" | "flat";

const normalizeText = (value: string) =>
  value.toLowerCase().replace(/https?:\/\/\S+/g, "").replace(/[^a-z0-9]+/g, " ").trim();

export function fingerprintNews(title: string, url: string) {
  return createHash("sha256").update(`${normalizeText(title)}|${url.toLowerCase().trim()}`).digest("hex");
}

export function dedupeNews<T extends NormalizedNewsItem>(items: T[]): T[] {
  const seen = new Set<string>();
  return items.filter(item => {
    const key = item.contentFingerprint;
    if (seen.has(key)) return false;
    seen.add(key);
    return true;
  });
}

type GdeltArticle = {
  url?: string;
  title?: string;
  seendate?: string;
  domain?: string;
  language?: string;
  socialimage?: string;
  sourcecountry?: string;
};

const decodeXml = (value: string) => value
  .replace(/^<!\[CDATA\[|\]\]>$/g, "")
  .replace(/&amp;/g, "&")
  .replace(/&quot;/g, '"')
  .replace(/&#39;/g, "'")
  .replace(/&lt;/g, "<")
  .replace(/&gt;/g, ">");

const rssField = (item: string, field: string) => {
  const match = item.match(new RegExp(`<${field}(?:\\s[^>]*)?>([\\s\\S]*?)<\\/${field}>`, "i"));
  return match?.[1] ? decodeXml(match[1].trim()) : undefined;
};

async function fetchBbcBusinessRss(): Promise<NormalizedNewsItem[]> {
  const response = await fetch("https://feeds.bbci.co.uk/news/business/rss.xml", {
    headers: { "user-agent": "MarketSignalOS/1.0 (paper-trading research workspace)" },
    signal: AbortSignal.timeout(12_000),
  });
  if (!response.ok) throw new Error(`BBC RSS request failed (${response.status})`);
  const xml = await response.text();
  const acquiredAt = new Date();
  const language = rssField(xml, "language") ?? "en-gb";
  const items = Array.from(xml.matchAll(/<item>([\s\S]*?)<\/item>/gi)).map(match => match[1]);
  return dedupeNews(items.flatMap(item => {
    const title = rssField(item, "title");
    const canonicalUrl = rssField(item, "link");
    if (!title || !canonicalUrl) return [];
    const publishedValue = rssField(item, "pubDate");
    const imageUrl = item.match(/<media:thumbnail[^>]*url="([^"]+)"/i)?.[1];
    return [{
      providerItemId: rssField(item, "guid") ?? canonicalUrl,
      canonicalUrl,
      title,
      summary: rssField(item, "description") ?? "Public business-news RSS item. Open the source link for full context.",
      publisher: "BBC News — Business",
      publisherUrl: "https://www.bbc.co.uk/news/business",
      imageUrl,
      language,
      publishedAt: publishedValue && !Number.isNaN(Date.parse(publishedValue)) ? new Date(publishedValue) : undefined,
      acquiredAt,
      contentFingerprint: fingerprintNews(title, canonicalUrl),
      rawPayload: { feedUrl: "https://feeds.bbci.co.uk/news/business/rss.xml", itemGuid: rssField(item, "guid") ?? null },
    }];
  }));
}

export async function fetchGdeltNews(query = "markets OR stocks OR crypto"): Promise<NormalizedNewsItem[]> {
  const url = new URL("https://api.gdeltproject.org/api/v2/doc/doc");
  url.searchParams.set("query", query);
  url.searchParams.set("mode", "artlist");
  url.searchParams.set("format", "json");
  url.searchParams.set("maxrecords", "12");
  url.searchParams.set("timespan", "24h");

  try {
    const response = await fetch(url, {
      headers: { "user-agent": "MarketSignalOS/1.0 (paper-trading research workspace)" },
      signal: AbortSignal.timeout(9_000),
    });
    if (!response.ok) throw new Error(`GDELT news request failed (${response.status})`);
    const payload = (await response.json()) as { articles?: GdeltArticle[] };
    const acquiredAt = new Date();
    return dedupeNews(
      (payload.articles ?? [])
        .filter(article => article.url && article.title)
        .map(article => ({
          providerItemId: article.url!, canonicalUrl: article.url!, title: article.title!,
          summary: "Public global-news discovery result. Open the original publisher link for full source context.",
          publisher: article.domain ?? "Unknown publisher", publisherUrl: article.domain ? `https://${article.domain}` : undefined,
          imageUrl: article.socialimage, language: article.language,
          publishedAt: article.seendate ? new Date(article.seendate) : undefined, acquiredAt,
          contentFingerprint: fingerprintNews(article.title!, article.url!), rawPayload: article as Record<string, unknown>,
        }))
    );
  } catch {
    return fetchBbcBusinessRss();
  }
}

export function computeOutcome(input: {
  direction: SignalDirection;
  entryPrice: number;
  observedPrice: number;
  informationCutoffAt: Date;
  evaluatedAt: Date;
}) {
  if (!Number.isFinite(input.entryPrice) || input.entryPrice <= 0 || !Number.isFinite(input.observedPrice)) {
    throw new Error("A positive entry price and a finite observed price are required for evaluation.");
  }
  if (input.evaluatedAt <= input.informationCutoffAt) {
    throw new Error("Evaluation must occur after the signal information cutoff to prevent look-ahead bias.");
  }
  const rawReturn = (input.observedPrice - input.entryPrice) / input.entryPrice;
  const directionalReturn = input.direction === "downside" ? -rawReturn : rawReturn;
  const outcome: SignalOutcome = Math.abs(directionalReturn) < 0.0025
    ? "flat"
    : directionalReturn > 0
      ? "favorable"
      : "unfavorable";
  return { grossReturn: rawReturn, directionalReturn, outcome, noLookaheadConfirmed: true };
}

export function paperOrderCost(quantity: number, referencePrice: number) {
  if (!Number.isFinite(quantity) || quantity <= 0 || !Number.isFinite(referencePrice) || referencePrice <= 0) {
    throw new Error("Quantity and reference price must both be positive finite values.");
  }
  return quantity * referencePrice;
}

export const paperPortfolioFixture = {
  virtualCash: 100000,
  equity: 102438.12,
  returnPct: 2.44,
  winLoss: { wins: 7, losses: 5, ratio: 1.4 },
  positions: [
    { symbol: "NOVA", assetClass: "equity", quantity: 28, averagePrice: 118.2, markPrice: 122.61, pnl: 123.48, status: "Paper" },
    { symbol: "ARCC", assetClass: "equity", quantity: 44, averagePrice: 54.3, markPrice: 52.91, pnl: -61.16, status: "Paper" },
    { symbol: "BTC", assetClass: "crypto", quantity: 0.12, averagePrice: 64120, markPrice: 65244, pnl: 134.88, status: "Paper" },
  ],
};
