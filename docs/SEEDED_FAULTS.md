# Verification and seeded faults

## Feature test before implementation

Codex wrote the named-date and future-perturbation tests before the feature.

The first run used `make test`; the process exited with status 2.

The baseline's 14 tests still passed and the two new tests failed because

`cnt_median_7` did not yet exist. The test-first commit is `c81261e`.

For 2011-01-20, the counts on Jan 13–19 are 1406, 1421, 1248, 1204,

1000, 683, and 1650. Their median is 1248.

Exact excerpts from that run:

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
