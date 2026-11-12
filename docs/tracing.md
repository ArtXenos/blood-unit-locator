# Tracing Tables — Emergency Blood Unit Locator

These tables show, step by step, what Merge Sort and Binary Search do on a small sample of 6 records.
Every row was printed by the real functions in `src/algorithms.py` through their `trace` list, so nothing here was worked out by hand.
The hospital data is fictional.

## The 6-record sample

- File: `data/hospitals.csv`, read with `load_records` (22 records, no rows skipped).
- Fixed date: **today = 2026-11-12**. `filter_usable` keeps a record only if it has more than 0 units and expires after today (20 records are usable).
- The sample is the **first 6 usable records**, in the order they appear in the file.

| Position | Hospital | Blood type | Units | Distance (km) | Expiry date |
|---|---|---|---|---|---|
| 0 | Matina Crossing Medical Center | O+ | 12 | 3.2 | 2027-03-15 |
| 1 | Toril Community Hospital | A- | 4 | 14.5 | 2027-01-20 |
| 2 | Buhangin District Hospital | B+ | 7 | 6.8 | 2027-05-02 |
| 3 | Calinan Valley Medical Center | O- | 3 | 27.4 | 2027-02-11 |
| 4 | Mintal Doctors Hospital | A+ | 9 | 11.3 | 2027-06-30 |
| 5 | Bajada General Hospital | O+ | 6 | 1.9 | 2027-04-08 |

Blood types in this order: `[O+, A-, B+, O-, A+, O+]`

### How blood types are compared

Blood types are compared as plain text, one character at a time. The character "+" comes before "-", so `A+` is smaller than `A-`.
This gives the order `A+ < A- < AB+ < AB- < B+ < B- < O+ < O-`. The sort and the search both use this same comparison.

## Merge Sort trace (by blood type)

Call: `merge_sort(sample, get_blood_type, trace)`

How to read the table:

- **Sub-list Left** and **Sub-list Right** are the two lists being merged. Each one is already in order.
- **i** is the position being looked at in Left. **j** is the position being looked at in Right.
- **Comparison** is the test in the code: `left[i] <= right[j]`. If it is true, the left item is taken. If it is false, the right item is taken.
- When one list is finished, the rest of the other list is copied without comparing. That is the last step of that merge.
- **Result** is the merged list so far.

| Step | Sub-list Left | Sub-list Right | i | j | Comparison | Result |
|---|---|---|---|---|---|---|
| 1 (**Merge 1**) | [A-] | [B+] | 0 | 0 | A- <= B+ is true, take left | [A-] |
| 2 | [A-] | [B+] | 1 | 0 | left is finished, copy the rest of right | [A-, B+] |
| 3 (**Merge 2**) | [O+] | [A-, B+] | 0 | 0 | O+ <= A- is false (O+ > A-), take right | [A-] |
| 4 | [O+] | [A-, B+] | 0 | 1 | O+ <= B+ is false (O+ > B+), take right | [A-, B+] |
| 5 | [O+] | [A-, B+] | 0 | 2 | right is finished, copy the rest of left | [A-, B+, O+] |
| 6 (**Merge 3**) | [A+] | [O+] | 0 | 0 | A+ <= O+ is true, take left | [A+] |
| 7 | [A+] | [O+] | 1 | 0 | left is finished, copy the rest of right | [A+, O+] |
| 8 (**Merge 4**) | [O-] | [A+, O+] | 0 | 0 | O- <= A+ is false (O- > A+), take right | [A+] |
| 9 | [O-] | [A+, O+] | 0 | 1 | O- <= O+ is false (O- > O+), take right | [A+, O+] |
| 10 | [O-] | [A+, O+] | 0 | 2 | right is finished, copy the rest of left | [A+, O+, O-] |
| 11 (**Merge 5**) | [A-, B+, O+] | [A+, O+, O-] | 0 | 0 | A- <= A+ is false (A- > A+), take right | [A+] |
| 12 | [A-, B+, O+] | [A+, O+, O-] | 0 | 1 | A- <= O+ is true, take left | [A+, A-] |
| 13 | [A-, B+, O+] | [A+, O+, O-] | 1 | 1 | B+ <= O+ is true, take left | [A+, A-, B+] |
| 14 | [A-, B+, O+] | [A+, O+, O-] | 2 | 1 | O+ <= O+ is true, take left | [A+, A-, B+, O+] |
| 15 | [A-, B+, O+] | [A+, O+, O-] | 3 | 1 | left is finished, copy the rest of right | [A+, A-, B+, O+, O+, O-] |

The sort took **15 steps** in **5 merges**.

### The sorted registry

| Position | Hospital | Blood type | Units | Distance (km) | Expiry date |
|---|---|---|---|---|---|
| 0 | Mintal Doctors Hospital | A+ | 9 | 11.3 | 2027-06-30 |
| 1 | Toril Community Hospital | A- | 4 | 14.5 | 2027-01-20 |
| 2 | Buhangin District Hospital | B+ | 7 | 6.8 | 2027-05-02 |
| 3 | Matina Crossing Medical Center | O+ | 12 | 3.2 | 2027-03-15 |
| 4 | Bajada General Hospital | O+ | 6 | 1.9 | 2027-04-08 |
| 5 | Calinan Valley Medical Center | O- | 3 | 27.4 | 2027-02-11 |

Blood types in order: `[A+, A-, B+, O+, O+, O-]`

### What happened in each merge

The list of 6 is cut into two halves of 3: `[O+, A-, B+]` and `[O-, A+, O+]`. Each half is cut again until the pieces have 1 item.

- **Merge 1 (steps 1–2):** `[A-]` and `[B+]` are joined. A- is smaller, so the result is `[A-, B+]`.
- **Merge 2 (steps 3–5):** `[O+]` is joined with `[A-, B+]`. O+ is bigger than both, so it goes last. The left half is now `[A-, B+, O+]`.
- **Merge 3 (steps 6–7):** `[A+]` and `[O+]` are joined. A+ is smaller, so the result is `[A+, O+]`.
- **Merge 4 (steps 8–10):** `[O-]` is joined with `[A+, O+]`. O- is bigger than both, so it goes last. The right half is now `[A+, O+, O-]`.
- **Merge 5 (steps 11–15):** the two sorted halves are joined into the full sorted list of 6.

### Stability: look at step 14

In step 14 the two items are equal: `O+ <= O+`. Because the code uses `<=` and not `<`, the test is true and the **left** O+ is taken first.
The left O+ is Matina Crossing Medical Center, which was at position 0 in the sample. The right O+ is Bajada General Hospital, which was at position 5.
So the two O+ units keep their original order: Matina at position 3 and Bajada at position 4. This is what "stable sort" means.

## Binary Search trace — find_first for O+

Call: `find_first(registry, "O+", trace)` on the sorted registry above.

Each row is one pass of the `while` loop. The values of `low`, `mid` and `high` are the ones before the action changes them.

| Step | low | mid | high | registry[mid].blood_type | Comparison | Action |
|---|---|---|---|---|---|---|
| 1 | 0 | 2 | 5 | B+ | B+ < O+ | low = mid + 1 = 3 |
| 2 | 3 | 4 | 5 | O+ | O+ == O+ | answer = 4, high = mid - 1 = 3 |
| 3 | 3 | 3 | 3 | O+ | O+ == O+ | answer = 3, high = mid - 1 = 2 |

Now `low = 3` and `high = 2`, so `low <= high` is false and the loop stops.

**find_first returns 3.**

In step 2 an O+ was found at position 4, but the search did not stop. It saved the answer and kept looking to the left, where it found an earlier O+ at position 3.

## Binary Search trace — find_last for O+

Call: `find_last(registry, "O+", trace)`

| Step | low | mid | high | registry[mid].blood_type | Comparison | Action |
|---|---|---|---|---|---|---|
| 1 | 0 | 2 | 5 | B+ | B+ < O+ | low = mid + 1 = 3 |
| 2 | 3 | 4 | 5 | O+ | O+ == O+ | answer = 4, low = mid + 1 = 5 |
| 3 | 5 | 5 | 5 | O- | O- > O+ | high = mid - 1 = 4 |

Now `low = 5` and `high = 4`, so the loop stops.

**find_last returns 4.**

After the match in step 2 the search kept looking to the right. It only found O-, which is bigger, so the answer stayed 4.

**All O+ units are `registry[3 .. 4]`:** Matina Crossing Medical Center (position 3) and Bajada General Hospital (position 4).
The registry has 6 records, and each search needed only 3 steps.

## Binary Search trace — a blood type that is not there

Call: `find_first(registry, "AB-", trace)`. No record in the sample has blood type AB-.

| Step | low | mid | high | registry[mid].blood_type | Comparison | Action |
|---|---|---|---|---|---|---|
| 1 | 0 | 2 | 5 | B+ | B+ > AB- | high = mid - 1 = 1 |
| 2 | 0 | 0 | 1 | A+ | A+ < AB- | low = mid + 1 = 1 |
| 3 | 1 | 1 | 1 | A- | A- < AB- | low = mid + 1 = 2 |

Now `low = 2` and `high = 1`, so the loop stops. No match was found, so `answer` never changed.

**find_first returns -1.**

Because find_first returned -1, `find_compatible_units` skips find_last for AB-. There is no block to copy.

## Second Merge Sort (by distance)

Patient blood type: **O+**. The compatibility table says an O+ patient can receive **O+** and then **O-**.

`find_compatible_units` looks for each donor type in that order and copies each block into `matches`:

| Donor type | find_first | find_last | Block copied |
|---|---|---|---|
| O+ | 3 | 4 | registry[3 .. 4] |
| O- | 5 | 5 | registry[5 .. 5] |

The matches, before sorting by distance:

| Position | Hospital | Blood type | Units | Distance (km) |
|---|---|---|---|---|
| 0 | Matina Crossing Medical Center | O+ | 12 | 3.2 |
| 1 | Bajada General Hospital | O+ | 6 | 1.9 |
| 2 | Calinan Valley Medical Center | O- | 3 | 27.4 |

Distances in this order: `[3.2, 1.9, 27.4]`

Call: `merge_sort(matches, get_distance, trace)`. It is the same Merge Sort, but now it compares distances.

| Step | Sub-list Left | Sub-list Right | i | j | Comparison | Result |
|---|---|---|---|---|---|---|
| 1 (**Merge 1**) | [1.9] | [27.4] | 0 | 0 | 1.9 <= 27.4 is true, take left | [1.9] |
| 2 | [1.9] | [27.4] | 1 | 0 | left is finished, copy the rest of right | [1.9, 27.4] |
| 3 (**Merge 2**) | [3.2] | [1.9, 27.4] | 0 | 0 | 3.2 <= 1.9 is false (3.2 > 1.9), take right | [1.9] |
| 4 | [3.2] | [1.9, 27.4] | 0 | 1 | 3.2 <= 27.4 is true, take left | [1.9, 3.2] |
| 5 | [3.2] | [1.9, 27.4] | 1 | 1 | left is finished, copy the rest of right | [1.9, 3.2, 27.4] |

The sort took **5 steps** in **2 merges**.

- **Merge 1 (steps 1–2):** `[1.9]` and `[27.4]` are joined. 1.9 is smaller, so the result is `[1.9, 27.4]`.
- **Merge 2 (steps 3–5):** `[3.2]` is joined with `[1.9, 27.4]`. 3.2 goes between them.

### Final order, nearest first

| Rank | Hospital | Blood type | Units | Distance (km) |
|---|---|---|---|---|
| 1 | Bajada General Hospital | O+ | 6 | 1.9 |
| 2 | Matina Crossing Medical Center | O+ | 12 | 3.2 |
| 3 | Calinan Valley Medical Center | O- | 3 | 27.4 |

This is exactly the list that `find_compatible_units(registry, "O+")` returns.

## How to read this aloud

1. "I start with 6 usable records. Merge Sort cuts the list in half until each piece has one item, then merges the pieces back in order of blood type."
2. "In every merge step I compare left at i with right at j. If left is smaller or equal I take left, if not I take right. When one side is finished I copy the rest."
3. "In step 14 both items are O plus. Because I use less than or equal, the left one is taken first, so equal items keep their original order. That makes the sort stable."
4. "Now the registry is sorted, so I can use Binary Search. find_first does not stop at the first match. It saves the answer and keeps looking left, and it returns position 3."
5. "find_last does the same but keeps looking right, and it returns position 4. So all O plus units are in positions 3 to 4, found in 3 steps each."
6. "For AB minus the search ends with low greater than high and returns minus 1, so find_last is skipped. Last, the matches for an O plus patient are sorted by distance, and the nearest hospital, Bajada General at 1.9 km, comes first."
