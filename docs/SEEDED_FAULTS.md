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

The three deliberate fault exercises and the Bash/raw-data experiment
will be recorded below after actual Claude Code runs.
