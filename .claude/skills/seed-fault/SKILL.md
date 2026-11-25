---
name: seed-fault
description: Check that a deliberate methodology fault triggers a real test failure, then restore the code and record the evidence.
argument-hint: "<forbidden-column | unshifted-roll | unguarded-weather>"
allowed-tools: Read, Edit, Write, Bash(make*), Bash(python*), Bash(git diff*), Bash(git status*)
---

# Fault to exercise: $ARGUMENTS

Only change `src/features.py` and append evidence to `docs/SEEDED_FAULTS.md`.
Do not change the raw CSV, remove tests, change permissions, or commit files.

1. Read the current code and run `make test`. Stop if the starting suite fails.
2. Apply exactly the requested fault using Edit:
   - `forbidden-column`: append `casual` to the returned feature columns.
   - `unshifted-roll`: remove `.shift(1)` from `cnt_roll_7` only.
   - `unguarded-weather`: remove the unknown-label `ValueError` guard only.
3. Preserve the actual PostToolUse hook stderr. Run `make test` and preserve
   its output and exit status. The run must fail for the intended reason;
   otherwise report the gap and stop without claiming the check worked.
4. Restore just the changed lines using Edit, then run `make test` again.
   Do not use checkout/reset to discard unrelated work.
5. Append the exact fault diff, red output, hook stderr, and green summary
   to `docs/SEEDED_FAULTS.md`. State the actual number of repair turns.
   If the hook output was unavailable, say so; never reconstruct a log.
