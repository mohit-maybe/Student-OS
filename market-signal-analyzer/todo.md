# Project TODO

- [x] Research and document reliable global news/RSS, market-data, sentiment-analysis, and paper-trading evaluation patterns with cited sources.
- [x] Inspect available Airtable and other configured integrations without assuming credentials or access. Airtable is enabled but its authorization is currently expired or invalid; no configured market-data connector is available, so the app must display an unconfigured connection state while supporting public GDELT discovery.
- [x] Define a provenance-preserving data model for news sources, normalized stories, evidence links, signal evaluations, paper orders, positions, and audit events.
- [x] Implement secure provider configuration states without embedding credentials and expose connected, disconnected, and demo-only status in the UI.
- [x] Implement world-news normalization, URL/content deduplication, publication/source provenance, retained-source listing, and an Airtable sync boundary when connected.
- [x] Implement structured market and crypto intelligence with entity/ticker extraction, catalyst categories, sentiment, confidence, evidence links, uncertainty disclosures, and time-stamped hypotheses.
- [x] Implement evaluation records with information cutoffs, post-signal outcome windows, no-look-ahead controls, and transparent quality metrics.
- [x] Implement paper trading with virtual cash, order lifecycle, positions, realized/unrealized P&L, win/loss metrics, trade rationales, and performance attribution.
- [x] Document a future broker-integration module with approvals, risk controls, and audit logs while keeping all real-money order submission disabled.
- [x] Build a premium, responsive black editorial dashboard with bold typography, data imagery, cursor/typewriter explanatory microcopy, keyboard-accessible navigation, and chart interactions.
- [x] Build daily trend boards, market-regime views, equity and crypto watchlists, source analysis panels, and interactive price, volume, sentiment, and bar charts.
- [x] Add Vitest coverage for data validation, source provenance, no-look-ahead evaluation controls, paper-trading calculations, and API responses.
- [x] Verify desktop/mobile rendering, accessibility essentials, error/loading/empty states, and no client- or server-side console errors.
- [ ] Extend the paper-trading engine from queued-order validation to persisted fills, cancellations, realized/unrealized P&L attribution, and owner-visible simulation history.
- [ ] Add a retained evaluation-history view showing each signal cutoff, post-cutoff market window, result, and methodology version once a licensed market-data provider is connected.
- [ ] Save a final project checkpoint, clone/synchronize the selected GitHub repository, and push the completed source code.
