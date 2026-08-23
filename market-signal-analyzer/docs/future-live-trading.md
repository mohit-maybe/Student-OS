# Future Live-Trading Module

MarketSignal OS is deliberately designed as a research and paper-trading system. **It has no real-money execution route.** Any future broker or exchange integration must be a separately enabled module, with distinct approval, risk, and audit controls.

| Control area | Required before activation | Current application behavior |
| --- | --- | --- |
| Broker / exchange credentials | Stored as project secrets, scoped to the minimum permissions, and validated with a read-only health check | No credentials are requested or used for execution. |
| Explicit activation | Owner-level confirmation and a per-user opt-in acknowledgement | Paper mode is permanently shown in the interface. |
| Order approvals | Human review and a two-step confirmation before every live order submission | No live order object or broker route exists. |
| Risk checks | Buying-power validation, maximum notional, concentration, loss, market-hours, duplicate-order, and kill-switch policies | Paper-order calculations validate positive finite quantities and prices only. |
| Audit trail | Immutable actor, timestamp, source-signal, model-version, decision, approval, request, broker-response, and reconciliation events | The `auditEvents` table is available for future use. |
| Evaluation | Point-in-time evidence cutoffs and post-cutoff outcome windows, with method versioning | Signal evaluation rejects timestamps at or before the information cutoff. |

> The application must never represent a hypothesis, backtest, model score, or paper-trading result as a guarantee of future performance. Any future live-trading deployment requires independent legal, compliance, security, and operational review.
