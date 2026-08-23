import type { NormalizedNewsItem } from "./marketCore";

const airtableConfig = () => ({
  token: process.env.AIRTABLE_TOKEN,
  baseId: process.env.AIRTABLE_BASE_ID,
  tableId: process.env.AIRTABLE_NEWS_TABLE_ID,
});

export function getAirtableStatus() {
  const { token, baseId, tableId } = airtableConfig();
  return token && baseId && tableId
    ? { status: "configured" as const, detail: "Credentials are configured server-side. Sync runs only when an authenticated user retains a source batch." }
    : { status: "unconfigured" as const, detail: "Reconnect Airtable or provide server-side credentials before retained-story sync can run." };
}

export function toAirtableRecords(items: NormalizedNewsItem[]) {
  return items.slice(0, 10).map(item => ({
    fields: {
      "Provider ID": item.providerItemId,
      "Canonical URL": item.canonicalUrl,
      "Title": item.title,
      "Summary": item.summary,
      "Publisher": item.publisher,
      "Published At": item.publishedAt?.toISOString() ?? null,
      "Acquired At": item.acquiredAt.toISOString(),
      "Fingerprint": item.contentFingerprint,
      "Language": item.language ?? null,
    },
  }));
}

export async function syncNewsToAirtable(items: NormalizedNewsItem[]) {
  const config = airtableConfig();
  if (!config.token || !config.baseId || !config.tableId) {
    return { status: "unconfigured" as const, synced: 0 };
  }

  const response = await fetch(`https://api.airtable.com/v0/${config.baseId}/${config.tableId}`, {
    method: "POST",
    headers: { authorization: `Bearer ${config.token}`, "content-type": "application/json" },
    body: JSON.stringify({ records: toAirtableRecords(items), returnFieldsByFieldId: false }),
  });
  if (!response.ok) throw new Error(`Airtable sync failed (${response.status}).`);
  const result = (await response.json()) as { records?: unknown[] };
  return { status: "synced" as const, synced: result.records?.length ?? 0 };
}
