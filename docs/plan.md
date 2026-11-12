# Approved Build Plan — Emergency Blood Unit Locator

Approved by the student on 2026-11-12. This file is the source of truth for the
build order. Read it together with `CLAUDE.md` and `blood-unit-locator-prompt.md`.

## Final folder structure

```text
blood-unit-locator/
├── .claude/            agents (6), skills (4), settings.json, settings.local.json
├── data/hospitals.csv
├── src/
│   ├── __init__.py     empty — lets `python -m unittest` find the package
│   ├── models.py       BloodUnit, COMPATIBLE, messages, get_blood_type, get_distance
│   ├── algorithms.py   exactly six functions (see below)
│   ├── locator.py      prepare_registry, search_patient (the BloodUnitLocator block)
│   ├── data_loader.py  load_records, parse_row
│   └── gui.py          LocatorApp (Tkinter window only — calls locator.py)
├── tests/
│   ├── __init__.py
│   └── test_algorithms.py
├── docs/               plan.md, pseudocode.md, tracing.md, test_results.md, complexity.md
├── main.py
├── CLAUDE.md
├── .gitignore
└── README.md
```

## Modules

**`src/models.py`**
- `BloodUnit` dataclass: `hospital, blood_type, units, distance_km, expiry_date`.
- `COMPATIBLE`: patient → donor table as a dict, in the exact order of the prompt.
- Message constants: `"No hospital records loaded."`, `"Invalid blood type."`,
  `"No compatible units available."`
- Sort-key helpers: `get_blood_type(unit)`, `get_distance(unit)`.

**`src/algorithms.py`** — exactly six pure functions, no GUI, no file access:

| Function | Pseudocode block | Notes |
|---|---|---|
| `filter_usable(records, today)` | FilterUsable | keep if `units > 0` and `expiry_date > today` |
| `merge_sort(items, key, trace=None)` | MergeSort | recursive, `mid = len(items) // 2` |
| `merge(left, right, key, trace=None)` | Merge | `<=` makes it stable |
| `find_first(registry, target, trace=None)` | FindFirst | iterative; on match `high = mid - 1` |
| `find_last(registry, target, trace=None)` | FindLast | iterative; on match `low = mid + 1` |
| `find_compatible_units(registry, patient_type)` | FindCompatibleUnits | loop over COMPATIBLE, copy `registry[first..last]`, merge-sort by distance |

Trace: when `trace` is a list, each step appends a small dict
(merge: left, right, i, j, comparison, result so far; search: low, mid, high,
value at mid, action). When `None`, nothing is recorded. Results are identical either way.

**`src/locator.py`** — the `BloodUnitLocator` pseudocode block, no Tkinter import:
- `prepare_registry(records, today)`: empty check → `filter_usable` → `merge_sort` by blood type. Runs once per CSV load or date change.
- `search_patient(registry, patient_type)`: invalid-type check → `find_compatible_units` → "No compatible units available." check.

**`src/data_loader.py`**
- `load_records(csv_path)` → `(records, skipped_rows)` using the `csv` module.
- `parse_row(row)`: builds a `BloodUnit` or reports why the row is bad (missing field, non-numeric units/distance, bad date, negative value, unknown blood type). Bad rows are skipped and counted, never a crash.

**`src/gui.py`** — `LocatorApp` (Tkinter), calls only `locator.py` and `algorithms.py`:
- Top bar: "Load CSV…" (loads `data/hospitals.csv` at start), editable "Today (YYYY-MM-DD)" field defaulting to the system date, read-only blood-type dropdown (8 types), "Find units" button.
- Results tab: table of hospital, blood type, units, distance, expiry — nearest first — plus a status line (messages, skipped-row count, and "Hospital data is fictional.").
- Trace tab: uses the first 6 usable records; shows the Merge Sort merges, then the Binary Search `low / mid / high` steps **for the blood type selected in the dropdown**, so both a found type and a not-found type (-1) can be demonstrated.
- No add-record form. A bad date in the "today" field shows a message box.

**`main.py`** — creates the window and starts the Tkinter loop (~10 lines).

## Dataset — `data/hospitals.csv`

- Columns: `hospital,blood_type,units,distance_km,expiry_date`.
- 14 fictional Davao-area hospitals, ~22 rows, in no particular order:
  Matina Crossing Medical Center, Toril Community Hospital, Buhangin District Hospital,
  Calinan Valley Medical Center, Mintal Doctors Hospital, Bajada General Hospital,
  Lanang Bayview Medical Center, Agdao Mercy Hospital, Sasa Wharfside Hospital,
  Panacan Family Hospital, Talomo Riverside Clinic, Bangkal Hillside Hospital,
  Tugbok Highlands Medical Center, Samal Island Bridge Hospital.
- All 8 blood types; several O+ and O- rows; two rows with equal distance;
  one row with 0 units; one clearly expired row (2025-01-15); all other expiry dates in 2027–2028.
- The first 6 usable rows: mixed types, one duplicate type, not already sorted.

## Tests — `tests/test_algorithms.py`

Fixed `TODAY = date(2026, 11, 1)`, in-memory lists only.

| # | Test | Expected |
|---|---|---|
| 1 | Many matches: O+ patient, several O+ and O- | only O+ and O- units, distances ascending |
| 2 | One match | list with that one record |
| 3 | All unusable (edge): O- patient, every O- row 0 units or expired | "No compatible units available." |
| 4 | Empty dataset (edge) | "No hospital records loaded." |
| 5 | Invalid type (edge): "C+" | "Invalid blood type." |
| 6 | Stability: equal distances | original order kept |

Extra: 1- and 2-element `merge_sort`; `find_first`/`find_last` on a run of duplicates
and on a missing type (-1); unit expiring exactly today is filtered out; tracing does
not change results; bad CSV rows skipped without a crash.

## Build order

| Step | Work | Agent / skill | Commit |
|---|---|---|---|
| A | git init, `.claude/`, `CLAUDE.md` | — | **done** |
| A2 | Add this plan's decisions to `CLAUDE.md`; create `docs/pseudocode.md` (copy of Section 2 pseudocode) so `algorithm-reviewer` has something to check against | — | yes |
| B | `src/__init__.py`, `tests/__init__.py`, `models.py` | — | yes |
| C | `algorithms.py`, one function at a time, tests after each | test-engineer, run-tests, **algorithm-reviewer**, no-builtin-check | yes |
| D | `locator.py` | test-engineer, run-tests | yes |
| E | `data_loader.py`, `hospitals.csv` | test-engineer, run-tests | yes |
| F | full test file, `docs/test_results.md` | test-engineer, run-tests (debugger-agent on failure) | yes |
| G | `gui.py`, `main.py` | security-agent, no-builtin-check | yes |
| H | `docs/tracing.md`, `docs/complexity.md`, `README.md` (with fictional-data note) | trace-generator + trace-table, complexity-analyst + complexity-report | yes |
| I | final run-tests + no-builtin-check; tell the student to run `python main.py` and `python -m unittest discover -s tests -v`; write "How to explain this in your video" | run-tests, no-builtin-check | yes |

After each module: a 3–5 line plain-words summary.
