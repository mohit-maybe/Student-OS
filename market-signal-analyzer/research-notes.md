# MarketSignal OS — Research Notes

## News-source architecture

The project will not claim to ingest "all" world news. Instead, it will use a configurable, provenance-preserving source architecture that can combine licensed providers, RSS feeds, and globally scoped research datasets. GDELT documents monitoring broadcast, print, and web reporting in more than 100 languages, with archives reaching January 1, 1979 and updates every 15 minutes. Its coverage is appropriate as one broad global discovery input, while the product will preserve source identity and direct evidence links rather than treating aggregated content as primary evidence.[1]

Massive's documented stock-news endpoint demonstrates fields the ingestion model should retain: a provider article ID, article URL, author, title, description, image URL, publisher name and homepage, original publication time in UTC, ticker associations, keywords, and provider-supplied sentiment with reasoning. Provider sentiment will be labeled as provider context rather than product-generated certainty.[2]

## Initial design implications

Every retained story should have immutable acquisition time, original publication time, canonical URL, source/provider identity, title fingerprint, raw-source pointer, extracted entity links, and an explicit processing version. Deduplication must keep all corroborating records in an evidence cluster instead of deleting alternative publisher records. Signals must be time-stamped against a market-data cut-off before their later evaluation window opens.

The evaluation layer will treat point-in-time universe membership, data availability time, and signal timestamp as first-class fields. A Journal of Portfolio Management study found that using an end-period benchmark membership instead of membership available at the beginning of a test period can overstate performance and understate drawdown risk; the product will avoid this class of error by not retroactively changing the eligible universe or evidence set for a signal.[3]

The optional Airtable destination will be a sync boundary, not a credential store or single source of truth. Airtable's record-creation API accepts a `baseId` and a stable table identifier or name, supports batches of records, requires an appropriately scoped credential and base-editor access, and returns record identifiers. The implementation will prefer table IDs, retain its own sync state, use idempotency keys derived from the story fingerprint, and show an unconfigured status until an authorized connector is available.[4]

RSS ingestion will retain channel title, channel link, language where supplied, item title, original link, item GUID, source, and publication date. RSS 2.0 identifies `guid`, `link`, `pubDate`, and `source` as item-level fields and defines a channel-level `ttl` cache hint; the collector will treat these as source-provided metadata, normalize times to UTC, and use a composite identity rather than trusting any single RSS field.[5] A public GDELT discovery adapter can provide a credential-free starting context because the documented DOC 2.0 API supports article-list mode and JSON-compatible output. That adapter will remain visibly labeled as discovery context rather than a comprehensive or exclusive feed.[6]

The initial deployed adapter falls back to the public BBC News Business RSS feed when GDELT is unavailable or rate-limited. This is intentionally displayed as a named fallback rather than combined indistinguishably with GDELT results. The feed itself publishes channel metadata, a cache TTL, item links, GUIDs, publication timestamps, and a rights notice, all of which support provenance-aware normalization.[7]

## References

[1]: https://www.gdeltproject.org/ "The GDELT Project"
[2]: https://massive.com/docs/rest/stocks/news "Massive Stock News API documentation"
[3]: https://arxiv.org/abs/0810.1922 "Daniel, Sornette, and Wohrmann, Look-Ahead Benchmark Bias in Portfolio Performance Evaluation"
[4]: https://airtable.com/developers/web/api/create-records "Airtable Web API: Create records"
[5]: https://www.rssboard.org/rss-specification "RSS 2.0 Specification"
[6]: https://blog.gdeltproject.org/gdelt-doc-2-0-api-debuts/ "GDELT DOC 2.0 API Debuts"
[7]: https://feeds.bbci.co.uk/news/business/rss.xml "BBC News Business RSS feed"
