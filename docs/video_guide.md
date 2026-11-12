# Video Guide — Emergency Blood Unit Locator

Notes for the recorded explanation. Part 1 has two or three sentences for each
function. Part 2 is a script for the 2-minute live demo. Say these in your own
words; they are prompts, not lines to read out.

## Part 1 — What to say for each function

### `src/algorithms.py`

**`filter_usable(records, today)`**

- I go through every record once and keep it only if it has more than zero
  units **and** its expiry date is after today.
- A unit that expires today is treated as not usable, because the check is
  "after", not "on or after".
- It is one loop over n records, so the time is O(n), and the new list can hold
  up to n records, so the extra space is O(n).

**`merge_sort(items, key, trace=None)`**

- A list with zero or one item is already in order, so that is where the
  recursion stops.
- Otherwise I cut the list in the middle, sort the left half and the right half
  the same way, and then merge the two halves.
- `key` is a small function that says what to compare: `get_blood_type` for the
  registry and `get_distance` for the results. There are about log n levels of
  cutting and each level handles n items, so the time is O(n log n).

**`merge(left, right, key, trace=None)`**

- `i` points at the next item of the left list and `j` at the next item of the
  right list. I compare those two items and copy the smaller one into `result`.
- I use `<=`, not `<`. On a tie the left item goes first, and the left item
  came first in the original list, so equal items keep their order. That is
  what makes the sort stable.
- When one list is finished, the rest of the other list is already in order,
  so I copy it to the end without comparing.

**`find_first(registry, target, trace=None)`**

- The registry is in blood type order, so I look at the middle item. If it is
  smaller than the target I move `low` to `mid + 1`; if it is bigger I move
  `high` to `mid - 1`.
- If it matches, I save the position in `answer` but I keep looking to the
  left, because an earlier unit of the same type may exist.
- The range is cut in half each time, so the time is O(log n). It is a loop,
  not recursion, and it only uses `low`, `high`, `mid` and `answer`, so the
  extra space is O(1). If the type is not there it returns -1.

**`find_last(registry, target, trace=None)`**

- It is the same search with one line changed: after a match I move `low` to
  `mid + 1`, so I keep looking to the right for a later unit of the same type.
- Together, `find_first` and `find_last` give me the two ends of the block of
  one blood type.

**`find_compatible_units(registry, patient_type)`**

- For each donor type the patient can receive, I call `find_first`. If it is
  not -1, I call `find_last` and copy the whole block between the two
  positions into `matches`.
- The matches are grouped by blood type, so I run Merge Sort a second time,
  now by distance, to put the nearest hospital first.
- The searches cost O(log n) and sorting k matches costs O(k log k), so the
  total is O(log n + k log k).

### `src/locator.py`

**`prepare_registry(records, today)`**

- First I check whether any records were loaded. If not, the message is
  "No hospital records loaded." and I stop.
- Then I filter out the unusable records and sort the rest by blood type.
- This runs once when the file is loaded, not once per patient. Sorting once is
  what makes binary search possible for every search after that.

**`search_patient(registry, patient_type)`**

- First I check that the blood type is in the compatibility table. If not, the
  message is "Invalid blood type."
- Then I call `find_compatible_units`. If the list comes back empty, the
  message is "No compatible units available."; otherwise I return the list.

### Questions you may be asked

- **Why does `A+` come before `A-`?** Blood types are compared as plain text,
  one character at a time, and `+` comes before `-` in the character table.
  The sort and the search both use this same comparison, so they agree.
- **What is the `trace` parameter?** It is an optional list. When I pass one,
  the function writes down each step so I can show it on screen. It never
  changes the answer.
- **Why not just scan the whole list for each patient?** A scan costs n steps
  for every patient. Sorting once costs n log n, and after that each search is
  only about log n steps, so it pays off as soon as there are many searches.

## Part 2 — Demo script (about 2 minutes)

Before recording: open a terminal in the project folder and check that the
**Today** field shows the real date. The numbers below are for the dataset
`data/hospitals.csv` with any date in November 2026.

| Time | Do this | Say / point out |
|---|---|---|
| 0:00 | Run `python main.py`. | The window loads the CSV: 22 records from 14 fictional hospitals, in no particular order. |
| 0:10 | Pick **O+**, press **Find units**. | 8 records. An O+ patient can receive O+ and O-, and only those two types appear. The nearest is first: Bajada General Hospital at 1.9 km; the last is Calinan Valley at 27.4 km. |
| 0:30 | Stay on the Results tab. | Two records are missing on purpose: Panacan Family Hospital has O+ but 0 units, and Bangkal Hillside Hospital has O- that expired in 2025. The filter removed them. Bangkal is only 2.5 km away, so without the filter it would wrongly be second. |
| 0:45 | Open the **Trace** tab. Scroll to part 2. | This is Merge Sort on the first 6 records: 5 merges. In the last merge, point at the line `O+ <= O+, take from left` — that is the tie, and taking the left one is what keeps the sort stable. |
| 1:05 | Scroll to parts 4 and 5. | Binary Search for O+ on the 6 sorted records. `find_first`: low, mid and high change each step and it returns 3. `find_last` returns 4. So every O+ unit is in positions 3 to 4. Each search took 3 steps for 6 records. |
| 1:25 | Pick **AB-**, press **Find units**, look at the Trace tab. | A type that is not in the sample: `low` passes `high`, the loop ends, and `find_first` returns -1, so `find_last` is not called. (The Results tab still shows 9 records, because the full dataset does have compatible units.) |
| 1:40 | Pick **A+**, press **Find units**, go to Results. | Stability in the real results: Matina Crossing has A- and O+ at the same 3.2 km, and Talomo (A+) and Agdao (O-) are both at 4.1 km. Equal distances stay in the order of the compatibility table. |
| 1:50 | Change **Today** to `2030-01-01`, press **Find units**. | Edge case: every unit is expired by then, so the message is "No compatible units available." Change the date back afterwards. |

If there is time left, type `abc` in the **Today** field and press **Find units**
to show that wrong input gives a message box instead of a crash.

### The three messages and when they appear

| Message | When |
|---|---|
| No hospital records loaded. | The CSV file is empty or could not be read. |
| Invalid blood type. | The blood type is not one of the eight in the table. The dropdown only offers valid types, so this is shown by the unit test with `"C+"`. |
| No compatible units available. | Every compatible unit has 0 units or is expired. |
