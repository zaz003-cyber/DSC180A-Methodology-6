# Decisions

One line per methodological decision: what you chose, why, and what it changed.
Agents append here via the `/new-feature` skill; you append here by hand.

- Exclude `casual`, `registered`: they sum to `cnt` exactly. Leaky model R^2 1.000 -> honest ridge 0.583.
- Exclude `cnt_2d_bfr`: a shipped 2-day lag we cannot test the alignment of. Build our own lags instead.
- Exclude `instant`, `yr`, `days_since_2011`: time indexes let a tree predict a flat constant past 2011 and a linear model extrapolate a trend we have no grounds for.
- Split 2011 / H1 2012 / H2 2012 by date. Test set touched once, after all feature work.
- Report mean and persistence baselines with every score. Persistence (test R^2 0.510, MAE 840) is within 0.07 R^2 of ridge and beats it on MAE; that caveat goes in the report.

- 2026-11-25: The student selected the median of demand over the seven strictly earlier calendar days. It uses no current-day count and needs no longer warm-up. Compare on validation before deciding whether to retain it.
- 2026-11-25: Classify every raw column, including raw labels represented by derived features, and reject unknown numeric or categorical columns before feature generation. This closes the denylist gap.
- 2026-11-25: Keep iterative checks on H1 2012. The original starter quality test read H2 2012 during environment verification, before any new-feature decisions; change it and add validation-only training so later decisions do not use H2 results.
- 2026-11-25: Add a parameterised seed-fault skill for the three break/check/restore exercises. Normalize Windows paths and use the active Python interpreter in the hook.
- 2026-11-25: Test one prespecified transformation, log(cnt / cnt_lag_1), inverted with yesterday's count. With the original features, tree validation R^2 rises from 0.2185 to 0.5734, below ridge's 0.6475. Do not tune this on H2 2012.

- 2026-11-25: Retain the selected median feature after an independent validation-only prototype: ridge R^2 0.6475 -> 0.6645 (+0.0170), MAE 832.9 -> 815.5; hgb R^2 0.2185 -> 0.2687 (+0.0502), MAE 1296.6 -> 1256.6. Both gains exceed the starter skill's 0.01 R^2 recommendation; the future test set did not enter this choice. Confirm with the Claude Code implementation.
- 2026-11-25: Claude Code with local Qwen3 4B wrote the shifted median expression. Its edit failed the hook because of indentation. Codex corrected that line and verified 21 passing tests, 714 rows, and the validation scores recorded above. With 15 predictors the log-relative tree reached validation R^2 0.6095 and MAE 843.2. Freeze these specifications for final evaluation.
- 2026-11-25: Reject an altered raw CSV in the data stage using the SHA-256 of the official file. A replacement preserved all test assertions yet moved ridge validation MAE from 815.5 to 892.2.
- 2026-11-25: The student chose persistence for routine daily dispatch because mean absolute error is the operating cost of interest. On H2 its MAE is 840.1 versus 939.7 for ridge.
- 2026-11-25: The log-relative target is defensible for one-day-ahead forecasts when yesterday’s count is observed. It improved the tree on validation but did not win mean absolute error on test. Keep untransformed metrics as the default.
- 2026-11-25: Endorse the peer's feature-retention decision. Ridge improved on identical training dates as well. Distinguish holdout access from evidence that it influenced model selection.
