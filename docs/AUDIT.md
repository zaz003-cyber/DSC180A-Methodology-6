# Peer leakage audit

Reviewed [CocoXu08/DSC180A-Methodology-7, branch `ma7-work`](https://github.com/CocoXu08/DSC180A-Methodology-7/tree/ma7-work) at [commit `5377983`](https://github.com/CocoXu08/DSC180A-Methodology-7/tree/53779837420d27c82496a8e0fcdbea77a4cf0ade). Claude Code ran the course's `leakage-auditor` agent with local Qwen3 4B. It received numbered source, test, metric and report excerpts from that commit and had read-only access to the snapshot.

## Auditor output (verbatim)

> All five checks pass.

## Independent checks

The 14-day mean matched the preceding 14 calendar days for all 700 retained observations. The raw data had one missing calendar date. The resulting split contained 334 training, 182 validation and 184 test days. Refitting the four published estimators reproduced every validation and test score in the peer's metrics file. [Feature implementation](https://github.com/CocoXu08/DSC180A-Methodology-7/blob/53779837420d27c82496a8e0fcdbea77a4cf0ade/src/features.py#L79) · [Published metrics](https://github.com/CocoXu08/DSC180A-Methodology-7/blob/53779837420d27c82496a8e0fcdbea77a4cf0ade/reports/metrics.json)

Holding all 334 training dates and 182 validation dates fixed gives the following ridge comparison. Only the inclusion of `cnt_roll_14` changes between rows.

| Ridge inputs | Validation R² | Validation MAE (rides/day) |
|---|---:|---:|
| Without the 14-day mean | 0.6434 | 839.2 |
| With the 14-day mean | 0.6919 | 763.2 |

## My verdict

I agree with the auditor on the main result. The 14-day feature uses past demand, and the published scores reproduce. The author's decision to keep the feature also holds up when the training dates are fixed: ridge gains 0.0485 validation R² on the same dates. The reported gain of 0.0444 answers a slightly different question because the longer warm-up also changes which days enter training, as the author explains. One qualification concerns the holdout: a routine test reads test-set R², so that information was available during development. The author reports using validation for feature selection. The code shows when the holdout was accessed and gives me no basis to conclude it influenced that choice. [Peer report](https://github.com/CocoXu08/DSC180A-Methodology-7/blob/53779837420d27c82496a8e0fcdbea77a4cf0ade/REPORT.md#results) · [Holdout check](https://github.com/CocoXu08/DSC180A-Methodology-7/blob/53779837420d27c82496a8e0fcdbea77a4cf0ade/tests/test_contract.py#L49)

## Suggestions for future experiments

- Add a same-date comparison beside the before-and-after table. Build the 14-day feature table once, then fit ridge twice on the same 334 training dates and score both fits on the same 182 validation dates. Dropping only `cnt_roll_14` for the first fit shows how much that predictor contributes: here it reduced validation MAE from 839.2 to 763.2 rides per day.
- Run the routine ridge quality check on the validation split while developing features. Once the feature set and model settings are fixed, run the final test evaluation. That gives future readers a clear record of when the held-out period first informed an assessment.
