# Deferred Paper-Trading Lifecycle Extension

The current application permits evidence-linked **paper-order validation only**. It intentionally does not fabricate fills, completed execution history, or live market marks while no licensed market-data provider is connected.

| Future capability | Required persisted data | Gate before enabling |
| --- | --- | --- |
| Queue, fill, cancel, reject | Order state changes, event timestamp, actor, reason, reference/fill price, and source-signal link | Licensed point-in-time price data and deterministic fill policy. |
| Realized P&L | Opening lots, closing orders, average-cost/FIFO method, fees, and close mark | Transaction-level paper fills must be persisted. |
| Unrealized P&L | Open lots, fresh mark time, mark source, mark price, and stale-price warning | Market data must disclose exchange, adjustment basis, and delayed/realtime status. |
| Performance attribution | Signal ID, catalyst, sector, asset class, holding window, benchmark, and method version | Benchmarks and symbols must be point-in-time eligible. |
| Simulation history | Account state, virtual-cash movements, daily snapshots, and audit events | Account ownership isolation and pagination. |

> These controls protect against presenting illustrative values as verified performance. The existing application labels the portfolio as a simulation fixture until the data and lifecycle gates above are satisfied.
