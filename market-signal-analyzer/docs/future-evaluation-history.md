# Deferred Signal Evaluation History

The current system validates that `evaluatedAt` must occur after `informationCutoffAt`, but it does not show market-data-dependent outcomes without a licensed historical and current price source.

| Field | Purpose | Validation |
| --- | --- | --- |
| Signal ID and source fingerprint | Trace each evaluation to its evidence record | Immutable foreign-key relationship. |
| Information cutoff | Last permitted evidence timestamp | Must be no later than the paper-order submission time. |
| Entry reference | Point-in-time reference price, vendor, adjustment basis, and observed timestamp | Must be available at or before the cutoff. |
| Evaluation window | Configured horizon such as 1d, 5d, or 20d | Must open strictly after the cutoff. |
| Observed result | Price, return, direction-aware result, and confidence calibration fields | Must use a post-cutoff observed timestamp. |
| Methodology version | Rules for universe, price adjustment, costs, and outcome thresholds | Immutable on each completed evaluation. |

The future UI must keep pending evaluations visibly distinct from favorable, unfavorable, and flat outcomes. It must also expose the data-source name, timestamp, and methodology version beside every metric rather than aggregating results into an unsupported accuracy claim.
