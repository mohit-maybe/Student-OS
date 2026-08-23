import { describe, expect, it } from "vitest";
import { toAirtableRecords } from "./airtable";
import { fingerprintNews } from "./marketCore";

describe("Airtable retained-news mapping", () => {
  it("maps provenance fields without including credentials or raw provider payloads", () => {
    const url = "https://news.example/item";
    const records = toAirtableRecords([{
      providerItemId: "example-1", canonicalUrl: url, title: "Provenance test", summary: "A source summary", publisher: "Example News", language: "en", acquiredAt: new Date("2026-08-23T00:00:00.000Z"), publishedAt: new Date("2026-08-22T00:00:00.000Z"), contentFingerprint: fingerprintNews("Provenance test", url), rawPayload: { secret: "must-not-leak" },
    }]);
    expect(records).toHaveLength(1);
    expect(records[0]?.fields).toMatchObject({ "Provider ID": "example-1", Publisher: "Example News", Language: "en" });
    expect(JSON.stringify(records)).not.toContain("must-not-leak");
  });
});
