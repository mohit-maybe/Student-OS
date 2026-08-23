# AI-Finance Learning Design

## Product position

MarketSignal OS should improve **decision-process quality**, calibration, and traceability rather than claim a permanently higher prediction rate. Every stored lesson must refer back to a bounded evidence set, the model/prompt version, a known information cutoff, the later evaluation window, and a defined market-data source.

## Research-informed controls

Research on LLM financial forecasting warns that widely pre-trained models may reproduce future information encountered during training instead of genuinely reasoning from a dated prompt. The application will therefore retain a point-in-time evidence snapshot and require that evaluation happens strictly after its cutoff.[1]

Look-Ahead-Bench similarly distinguishes memorization from generalization by examining performance decay across separate market regimes and by comparing AI results with quantitative baselines. The product will segment scorecards by time regime, asset class, catalyst type, and confidence bucket; a single blended win rate will never be treated as proof of accuracy.[2]

## Learning-record contract

Each completed paper trade will produce a durable learning record containing the following fields.

| Element | Stored value | Purpose |
| --- | --- | --- |
| Trade and signal lineage | Trade ID, signal ID, source IDs/fingerprints, original URLs, prompt/model version | Reconstruct the decision and its evidence. |
| Decision-time state | Information cutoff, entry rule, entry reference, confidence, direction, uncertainty | Prohibit future data from altering the original rationale. |
| Outcome state | Exit or evaluation time, observed price, gross/net paper P&L, direction-aware outcome | Separate what happened after the decision. |
| Error taxonomy | Data gap, catalyst misread, timing, risk sizing, regime shift, execution assumption, unclassifiable | Support error analysis without hindsight rewriting. |
| Reusable lesson | A conditional, falsifiable lesson with a review status and evidence count | Prevent a single trade from becoming an untested permanent rule. |
| Calibration view | Confidence bucket, outcome frequency, sample count, and regime segment | Measure whether stated confidence matches observed outcomes. |

## Accuracy-improvement loop

The application will use a constrained loop: collect immutable trade evidence; evaluate only after the defined window; classify error without changing the original hypothesis; aggregate only when sample-size and regime requirements are met; then surface a **reviewable lesson**, not an automatic strategy mutation. A human must approve any future rule or risk-policy change.

## References

[1]: https://arxiv.org/html/2512.23847v1 "Jiang, Yan, and Gao, A Test of Lookahead Bias in LLM Forecasts"
[2]: https://arxiv.org/abs/2601.13770 "Benhenda, Look-Ahead-Bench: a Standardized Benchmark of Look-ahead Bias in Point-in-Time LLMs for Finance"
