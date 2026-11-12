# Emergency Blood Unit Locator

Final project for the Algorithms course. In a medical emergency, responders need
compatible blood quickly. This program reads the blood stock reported by
hospitals, and for a patient's blood type it lists every compatible unit with
the **nearest hospital first**.

> **Note:** all hospital names and stock numbers in `data/hospitals.csv` are
> fictional. They were made up for this project and do not describe real
> hospitals.

## How it works

1. **Filter** — remove records with 0 units or an expiry date that is not after today.
2. **Merge Sort** — put the registry in blood type order, once.
3. **Binary Search** — for each donor type the patient can receive, find the
   first and last position of that type in the registry.
4. **Merge Sort again** — order the matches by distance. The sort is stable, so
   hospitals at the same distance keep their order.

Merge Sort and Binary Search are written by hand in `src/algorithms.py`. No
built-in or library sorting or searching is used anywhere in the program.

## Requirements

- Python 3 (tested on Python 3.14).
- Nothing to install. Only the standard library is used
  (`tkinter`, `csv`, `datetime`, `dataclasses`, `unittest`).

## How to run

Run both commands from the project folder.

```text
python main.py
```

1. The window opens and loads `data/hospitals.csv`.
2. Pick the patient's blood type and press **Find units**.
3. The **Results** tab shows the compatible units, nearest first.
4. The **Trace** tab shows the Merge Sort merges and the Binary Search
   `low / mid / high` steps on the first 6 usable records, for the blood type
   that is picked.

Other things to try: **Load CSV...** opens another file, and the **Today** field
can be changed to see units expire.

## How to run the tests

```text
python -m unittest discover -s tests -v
```

The expected and actual results are written in `docs/test_results.md`.

## CSV format

The first line must be the header below. The rows can be in any order.

```text
hospital,blood_type,units,distance_km,expiry_date
Bajada General Hospital,O+,6,1.9,2027-04-08
```

A row with a missing value, an unknown blood type, a number that is not a
number, or a wrong date is skipped and reported. It never crashes the program.

## Project structure

```text
main.py               starts the window
src/models.py         BloodUnit record, compatibility table, messages
src/algorithms.py     the six hand-written algorithm functions
src/locator.py        the main steps: prepare_registry, search_patient
src/data_loader.py    reads and checks the CSV file
src/gui.py            the Tkinter window
tests/                unit tests
data/hospitals.csv    fictional dataset (22 rows, 14 hospitals)
docs/                 pseudocode, tracing tables, test results, complexity
```

## Complexity

| Step | Time | Extra space |
|---|---|---|
| Filter usable records | O(n) | O(n) |
| Merge Sort (registry) | O(n log n) | O(n) |
| Binary Search (first / last) | O(log n) | O(1) |
| Find compatible units | O(log n + k log k) | O(k) |

`n` is the number of records and `k` is the number of matching units. The
full explanation is in `docs/complexity.md`.
