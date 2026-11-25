# Verification and seeded faults

## Feature test before implementation

Codex wrote two tests before the feature in commit `c81261e`. For January 20, 2011, the seven counts on January 13–19 were 1406, 1421, 1248, 1204, 1000, 683, and 1650. Sorting gives the fourth value, 1248. The second test changes the count on January 20 and later to ensure the median for January 20 stays the same. The first `make test` exited with status 2.

```text
E   KeyError: 'cnt_median_7'
E           KeyError: 'cnt_median_7'
E   KeyError: 'cnt_median_7'
E           KeyError: 'cnt_median_7'
FAILED tests/test_leakage.py::test_rolling_median_uses_previous_calendar_week
FAILED tests/test_leakage.py::test_rolling_median_excludes_today_and_future
2 failed, 14 passed in 2.69s
make: *** [Makefile:16: test] Error 1
```

## Forbidden column

```diff
-    return [c for c in numeric if c not in FORBIDDEN]
+    return [c for c in numeric if c not in FORBIDDEN] + ["casual"]
```

The PostToolUse hook ran pytest immediately after the edit and exited with code 2. Its stderr included the following lines.

```text
E       AssertionError: forbidden columns in feature set: {'casual'}
E       assert not ({'atemp', 'casual', 'cnt_lag_1', 'cnt_lag_7', 'cnt_median_7', 'cnt_roll_7', ...} & {'casual', 'cnt', 'cnt_2d_bfr', 'days_since_2011', 'holiday', 'instant', ...})

tests\test_leakage.py:34: AssertionError
=========================== short test summary info ===========================
FAILED tests/test_leakage.py::test_no_forbidden_features - AssertionError: fo...
1 failed, 10 passed in 0.59s
```

Qwen restored the original expression in one repair edit. The following hook exited with code 0. 21 passed in 1.58s

## Unshifted rolling mean

```diff
-out[TARGET].shift(1).rolling(LAG_WARMUP).mean()
+out[TARGET].rolling(LAG_WARMUP).mean()
```

The PostToolUse hook ran pytest immediately after the edit and exited with code 2. Its stderr included the following lines.

```text
E           assert np.float64(4389.0) == 4414.857142857143 ± 0.00441486
E             
E             comparison failed
E             Obtained: 4389.0
E             Expected: 4414.857142857143 ± 0.00441486

tests\test_leakage.py:60: AssertionError
=========================== short test summary info ===========================
FAILED tests/test_leakage.py::test_rolling_mean_excludes_today - assert np.fl...
1 failed, 10 passed in 0.62s
```

Qwen restored the original expression in one repair edit. The following hook exited with code 0. 21 passed in 1.49s

## Unknown weather category

```diff
-        raise ValueError(f"unmapped weather labels: {sorted(unknown)}")
+        pass
```

The PostToolUse hook ran pytest immediately after the edit and exited with code 2. Its stderr included the following lines.

```text
E       Failed: DID NOT RAISE ValueError

tests\test_leakage.py:89: Failed
=========================== short test summary info ===========================
FAILED tests/test_leakage.py::test_weather_encoder_rejects_unseen_labels - Fa...
1 failed, 10 passed in 0.67s
```

Qwen restored the original expression in one repair edit. The following hook exited with code 0. Full suite verified separately.

## Raw data replacement

In a disposable checkout, Codex ran the following Bash command directly. It replaced the checkout's raw CSV outside a Claude Code editing session. This demonstrates the external file-change case. The three edits above capture the separate in-session hook behavior.

```bash
cp ../evidence/altered-counts.csv data/raw/bike_daily.csv
```

The replacement increased casual and registered counts by 10% (rounded separately) after January 20, 2011, then recalculated their sum. The date used in the hand calculation and its history stayed intact. Row counts, the component identity, and calendar alignment survived. Before the checksum guard, the suite passed even though validation MAE changed.

```text
Original SHA-256 a6bed1577f6e4de56dcfae6d8315985073cc0ad3446c8c99ed60c86a0b5ad9dc
Replacement SHA-256 5ed0a8dc733db2f10e93ec5059855658a59b5956a27483fc01ce0e377be7d8c2
21 passed in 1.58s
Validation ridge before {'r2': 0.6645, 'mae': 815.5} after {'r2': 0.6671, 'mae': 892.2}
Restored SHA-256 a6bed1577f6e4de56dcfae6d8315985073cc0ad3446c8c99ed60c86a0b5ad9dc
```

The hook matches Edit and Write in Claude Code. An external file replacement has no matching event. The new data-stage check hashes the bytes before the pipeline can build features. With the same replacement, the data stage stopped and printed the following line. Restoring the checked-in bytes allowed ingestion to run again.

```text
raw CSV checksum mismatch: expected a6bed1577f6e4de56dcfae6d8315985073cc0ad3446c8c99ed60c86a0b5ad9dc, found 5ed0a8dc733db2f10e93ec5059855658a59b5956a27483fc01ce0e377be7d8c2
```
