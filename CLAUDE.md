# Emergency Blood Unit Locator — project rules

Individual final project for a 2nd-year Algorithms course. The student must
trace the algorithm and explain every line on video, so the code has to stay
simple enough to defend line by line. The full brief is in
`blood-unit-locator-prompt.md`.

Deadline: November 18, 2026, 5:00 PM.

## Graded course rules (never break these)

- Merge Sort and Binary Search are written by hand. Do not use `sort()`,
  `sorted()`, `bisect`, `heapq`, `pandas`, `numpy`, or any library that sorts
  or searches. Do not use `min()`/`max()` to order things either.
- Do not write those forbidden names anywhere in `src/` or `main.py`, not even
  in comments or docstrings. The `no-builtin-check` skill greps for them.
- Standard library only: `tkinter`, `csv`, `datetime`, `dataclasses`,
  `unittest`. Never run `pip install`.
- The GUI is Tkinter. Input comes from the user (blood type picker, "today"
  date field) and from a CSV file.
- Algorithm correctness matters more than GUI looks. Readability matters more
  than cleverness.

## The pseudocode is the source of truth

The approved pseudocode is in Section 2 of the prompt (and `docs/pseudocode.md`).
`src/algorithms.py` has exactly six functions, one per pseudocode block:
`filter_usable`, `merge_sort`, `merge`, `find_first`, `find_last`,
`find_compatible_units`.

- Keep the pseudocode variable names: `low`, `mid`, `high`, `answer`, `left`,
  `right`, `i`, `j`, `result`, `usable`, `matches`.
- `merge` compares with `<=` so the sort is stable.
- `find_first` / `find_last` are iterative (a `while` loop), O(1) extra space.
- The registry is sorted by blood type once, then searched many times.
- Algorithm functions are pure: no GUI code, no printing, no file access.
- The optional `trace` list parameter only records steps. It must never change
  the result.

## Decisions already made

- Blood types compare as plain strings (`A+ < A- < AB+ < AB- < B+ < B- < O+ < O-`).
  The sort and the search must use the same comparison.
- Expiry is strict: a unit is usable only if `expiry_date > today`. A unit
  that expires today is unusable.
- Tests use a fixed "today" date and in-memory records, never the system clock.
- Ties on equal distance keep compatibility-table order (stable sort).
- No add-record form. The trace view uses a 6-record sample; the full run is
  shown separately. The GUI has an editable "today" field that defaults to the
  system date.
- The three user messages are exact: "No hospital records loaded.",
  "Invalid blood type.", "No compatible units available."
- `docs/plan.md` is the approved build plan. Follow its module list and build
  order.
- `src/locator.py` holds the `BloodUnitLocator` pseudocode block as two
  functions: `prepare_registry` (empty check, filter, sort once) and
  `search_patient` (invalid-type check, search, no-units check). It does not
  import Tkinter. `src/algorithms.py` still has exactly six functions.
- The Trace tab searches for the blood type selected in the dropdown, so both
  a found type and a not-found type (-1) can be shown.
- The hospital data is fictional. `README.md` and the GUI status bar both say
  so.

## Code style

- Student-level Python: plain loops and `if` statements, clear names, small
  functions. No clever one-liners, no advanced features.
- Every function has a short docstring in plain English.
- Comments explain why, not just what.

## Working rules

- Only create, edit or run things inside this project folder.
- Only run `python`, `python -m unittest`, `grep` and `git`. Ask before
  anything else.
- Commit after each module.
- Run the tests with `python -m unittest discover -s tests -v` (the
  `run-tests` skill) and the `no-builtin-check` skill before every commit.
- Use the agents in `.claude/agents/` and say which one is in use:
  `algorithm-reviewer` after any change to `src/algorithms.py`,
  `test-engineer` for tests, `debugger-agent` on failures, `security-agent`
  before finishing, `trace-generator` and `complexity-analyst` for `docs/`.
