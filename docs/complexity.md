# Time and Space Complexity — Emergency Blood Unit Locator

Every result below is counted from the loops and the recursion in
`src/algorithms.py` and `src/locator.py`.

Two sizes are used:

- **n** = number of records in the list a function receives. For
  `filter_usable` this is every record loaded from the CSV. For the registry it
  is the number of usable records, which is never more than that.
- **k** = number of registry records that match the patient (rows, not bags of
  blood). k is never more than n.

"Extra space" means memory used on top of the input list. The lists hold
references to the same `BloodUnit` objects; the objects are never duplicated.

## 1. filter_usable(records, today)

There is one loop, `for record in records:`, and it runs exactly n times. Each
pass does two comparisons (`record.units > 0 and record.expiry_date > today`)
and at most one `usable.append(record)`. That is a fixed amount of work per
pass, so the time is **O(n)**.

The new list `usable` can hold up to n records when nothing is expired, so the
extra space is **O(n)**.

Strength / limitation: it is a single simple pass, but it has to run again
whenever "today" changes, because the result depends on the date.

## 2. merge(left, right, key)

Here n = `len(left) + len(right)`.

The loop is `while i < len(left) and j < len(right):`. Every pass appends
exactly one item to `result` and adds 1 to either `i` or `j`. Nothing ever goes
backwards, so the loop can run at most n times. It stops as soon as one list is
finished.

Then `result.extend(left[i:])` and `result.extend(right[j:])` copy the
leftovers without comparing. Loop passes plus leftovers add up to exactly n
items moved, so the time is **O(n)**.

`result` ends with n items, so the extra space is **O(n)**.

Strength / limitation: `if key(left[i]) <= key(right[j]):` takes the left item
on a tie, which keeps equal items in their original order (stable), but the
merge cannot be done in place and needs a second list.

## 3. merge_sort(items, key)

n = `len(items)`.

Each call with more than one item cuts the list at `mid = len(items) // 2`,
calls itself on `items[:mid]` and `items[mid:]`, and then calls `merge` once.
Two half-size problems plus one O(n) merge gives the recurrence:

    T(n) = 2 T(n/2) + O(n)

The "levels" picture solves it. With n = 8:

| Level | Lists being merged | Items merged at this level |
|---|---|---|
| 1 | 4 pairs of size 1 | 8 |
| 2 | 2 pairs of size 2 | 8 |
| 3 | 1 pair of size 4 | 8 |

The list is halved until the pieces have size 1 (`if len(items) <= 1: return
items`), and 8 can be halved 3 times, so there are log2 8 = 3 levels. Every
level merges all n items once. Total work = n per level x log2 n levels, so the
time is **O(n log n)**. For n = 8 that is about 8 x 3 = 24 item moves.

An honest detail: the slices `items[:mid]` and `items[mid:]` also copy items,
n in total per level. That doubles the work per level (2n instead of n) but a
constant factor does not change O(n log n).

Best, average and worst case are all **O(n log n)**. The code always splits in
the middle and always merges, even when the list is already in order. An
ordered list only needs fewer comparisons inside `merge`; the items are still
all copied.

Recursion depth: one call per level plus the base case, so about log2 n + 1
calls are open at the same time (4 for n = 8).

Extra space: the open calls hold slices of size n/2, n/4, n/8, ... which add up
to less than n, and the biggest `result` list has n items. The total is
**O(n)**, plus O(log n) for the call stack, which is smaller.

Strength / limitation: the running time is predictable and the sort is stable,
but it uses O(n) extra memory and does not get faster on data that is already
ordered.

## 4. find_first and find_last (registry, target)

n = `len(registry)`. The registry must already be in blood type order.

The loop is `while low <= high:`. Each pass looks at `mid = (low + high) // 2`
and then runs one of `high = mid - 1` or `low = mid + 1`. Either way, the part
that is still being searched (`low..high`) loses the middle and one whole half,
so it shrinks to at most half its size.

Worked number, n = 20: the range sizes are at most 20, 10, 5, 2, 1, and then it
is empty. That is **5 passes at most**, which is the general formula: about
log2 n + 1 passes (log2 20 is about 4.3, rounded down to 4, plus 1). Each pass
compares two short strings, which is a fixed amount of work, so the time is
**O(log n)**.

These functions do not stop at the first match. On a match `find_first` does
`answer = mid` and `high = mid - 1` to keep looking on the left; `find_last`
does `low = mid + 1` to keep looking on the right. The range still halves on
every pass, so the cost stays O(log n). It just means the best case is also
about log2 n passes instead of 1.

Extra space: they are iterative and use only `low`, `high`, `mid` and `answer`,
so **O(1)**. When the optional `trace` list is passed in, one entry is saved
per pass, which is O(log n) memory. That is only used for the demonstration.

Strength / limitation: very fast and uses no extra memory, but it gives wrong
answers if the registry is not in the same string order that the sort used.

## 5. find_compatible_units(registry, patient_type)

The work has three parts.

1. **Searching.** `for donor_type in COMPATIBLE[patient_type]:` runs at most 8
   times, because the longest list in the table (AB+) has 8 donor types. Each
   pass calls `find_first`, and calls `find_last` only `if first != -1`. That
   is at most 16 binary searches. 16 is a constant, so this part is
   16 x O(log n) = **O(log n)**.
2. **Copying.** `for position in range(first, last + 1):` appends one block of
   matching records. The donor types in one list are all different, so the
   blocks never overlap and all the passes together add up to exactly k:
   **O(k)**.
3. **Ordering by distance.** `return merge_sort(matches, get_distance)` sorts a
   list of k items: **O(k log k)**, from Section 3.

Total time: O(log n) + O(k) + O(k log k) = **O(log n + k log k)**, because
k log k is at least as big as k.

Extra space: `matches` has k items and its merge sort needs O(k) more, so
**O(k)**.

Worst case: k = n. A patient with AB+ can receive all 8 types, so every usable
record matches and the cost becomes O(n log n) for that one query.

Strength / limitation: each block is found without looking at the records that
do not match, but when most of the registry matches, the k log k distance sort
is the real cost and the binary search saves very little.

## 6. The pipeline in src/locator.py

`prepare_registry(records, today)` runs once per loaded file. It calls
`filter_usable` (O(n)) and then `merge_sort(usable, get_blood_type)`
(O(n log n)). One-time cost: O(n) + O(n log n) = **O(n log n)** time, O(n)
extra space.

`search_patient(registry, patient_type)` runs once per query. The check
`patient_type not in COMPATIBLE` is one dictionary lookup, and then it calls
`find_compatible_units`. Cost per query: **O(log n + k log k)** time, O(k)
extra space.

## 7. Summary table

| Step | Time | Extra space |
|---|---|---|
| FilterUsable | O(n) | O(n) |
| Merge (one call) | O(n) | O(n) |
| MergeSort (registry) | O(n log n) | O(n) |
| FindFirst / FindLast | O(log n) | O(1), iterative |
| FindCompatibleUnits | O(log n + k log k) | O(k) |
| prepare_registry (once) | O(n log n) | O(n) |
| search_patient (per query) | O(log n + k log k) | O(k) |

The counts from the code agree with the expected complexity table in
`docs/pseudocode.md`. One note on the trace mode: when a `trace` list is passed
to `merge`, every step saves `list(result)`, a copy of the result so far. That
makes a traced merge of n items cost about n x n / 2 copies instead of n. It is
only switched on for the 6-record demonstration; the normal run passes no
trace and is not affected.

## 8. Trade-off: sort once and search, or scan every time?

For Q queries on the same registry:

| Approach | Total cost |
|---|---|
| Sort once, then binary search | n log n + Q (log n + k log k) |
| Linear scan for every query | Q x n + Q x k log k |

Both approaches still have to put the k matches in distance order, so the
k log k part is the same. The difference is the search: log n per query after
paying n log n once, against n per query with nothing to pay first.

Worked example with n = 10,000 records, k = 50 matches, Q = 1,000 queries,
using log2 (rough step counts, worst case for the search):

| Part | Sort once + binary search | Linear scan |
|---|---|---|
| One-time filter | 10,000 | 0 (done inside each scan) |
| One-time sort, n log2 n | 10,000 x 13.3 = about 133,000 | 0 |
| Search, per query | 16 searches x 14 passes = 224 | 10,000 |
| Copy the matches, per query | 50 | included in the scan |
| Distance sort, per query, k log2 k | 50 x 5.64 = about 282 | about 282 |
| Per query total | 556 | 10,282 |
| **Total for 1,000 queries** | 143,000 + 556,000 = **about 699,000** | **about 10,282,000** |

Sorting once is about 15 times less work here. The one-time cost of 143,000
steps is paid back after about 15 queries (each query saves about 9,700 steps).

Linear search would be fine, or even better, when:

- **n is very small.** With a few dozen records both approaches are instant and
  the scan is simpler code.
- **There is only one query** (or fewer than the break-even number, about 15 in
  the example). One scan costs n; sorting first costs n log n.
- **The data changes constantly.** Every change means running
  `prepare_registry` again, so the n log n is paid over and over.
- **k is close to n.** For an AB+ patient with n = k = 10,000, both approaches
  spend about 133,000 steps per query on the distance sort, and the search
  saving is small next to that.

## 9. Strengths

- The registry is put in order once and reused by every query.
- Merge sort is predictable: O(n log n) in the best, average and worst case.
- The sort is stable because of `<=`, so hospitals at the same distance keep
  the order of the compatibility table.
- Binary search is iterative: O(log n) time and O(1) extra space, with no
  recursion.
- `find_first` and `find_last` give the whole block of a blood type, so the
  records that do not match are never looked at.
- The per-query cost depends mostly on k, the number of matches, and not on
  the size of the registry.

## 10. Limitations

- Merge sort needs O(n) extra memory, and the slices `items[:mid]` and
  `items[mid:]` add more copying.
- The registry must be rebuilt (filter and sort again, O(n log n)) when a new
  CSV is loaded or the "today" date changes.
- Blood types are ordered as plain strings (A+ before A-, then AB+, ...). This
  has no medical meaning, and the sort and the search must use the same
  comparison or the search breaks.
- When most units match (k close to n), k log k dominates and a query costs as
  much as sorting the registry again.
- Up to 16 binary searches run per query. This is a constant, so it does not
  change the Big O, but it is more than a single search.
- `find_first` and `find_last` always run about log2 n passes, even when the
  first middle item is already a match.
- Merge sort does not get faster when the data is already in order.
