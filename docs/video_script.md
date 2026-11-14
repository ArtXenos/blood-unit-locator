# Video Script — Emergency Blood Unit Locator

Full script for the 15-minute recorded presentation. It follows the six
required segments in order. `docs/video_guide.md` has the recording plan, the
setup checklist and the notes for each function.

How to use this script:

- **SCREEN** says what to show. **SAY** is what to say.
- Do not read it word for word. The guidelines ask for the code to be explained
  in your own words, so practise each segment until you can say it from the
  keywords alone.
- Read `O+` as "O positive" and `A-` as "A negative". Read `<=` as "less than
  or equal".
- The script is about 1,950 words. At a normal speaking pace that is about
  14 minutes, which leaves one minute for clicking and scrolling.
- Every number below was checked against the real program with the dataset
  `data/hospitals.csv` and a "today" date in November 2026.
- Fill in the three blanks in Segment 1 before recording.

| Segment | Starts | Ends | Length |
|---|---|---|---|
| 1. Introduction | 0:00 | 1:00 | 1 min |
| 2. Algorithm Explanation | 1:00 | 4:00 | 3 min |
| 3. Algorithm Tracing | 4:00 | 9:00 | 5 min |
| 4. Live Application Demonstration | 9:00 | 11:00 | 2 min |
| 5. Complexity Analysis | 11:00 | 14:00 | 3 min |
| 6. Conclusion | 14:00 | 15:00 | 1 min |

---

## Segment 1 — Introduction (0:00 – 1:00)

**SCREEN:** Your face, large. Behind it, `README.md` in preview so the project
title is visible.

**SAY:**

Good day. I am ________, from ________, and this is my final project for
________: the **Emergency Blood Unit Locator**.

The real-world problem is this. When a patient is losing blood in an
emergency, the staff need compatible blood right away. But the blood is spread
across many hospitals. Each hospital has different blood types in stock, some
units are already expired, and the nearest hospital is not always the one that
has the right type. Calling hospitals one by one wastes minutes that the
patient does not have.

My program solves that. It reads the blood stock of the hospitals from a CSV
file. The user picks the patient's blood type, and the program lists every unit
that patient can safely receive, with the nearest hospital first. It does this
with two algorithms that I wrote by hand: Merge Sort and Binary Search. All the
hospital data in this video is fictional.

---

## Segment 2 — Algorithm Explanation (1:00 – 4:00)

**SCREEN:** `docs/pseudocode.md` on the left and `src/algorithms.py` on the
right. Scroll both so the block you are talking about is visible.

**SAY:**

I chose Merge Sort and Binary Search because they work as a pair. Binary Search
is very fast, but it only works on a list that is in order. So I sort the list
once with Merge Sort, and after that every patient search is a binary search.

The program has four steps.

**SCREEN:** `FilterUsable` and `filter_usable` (lines 15–26).

Step one is FilterUsable. It goes through every record once and keeps a record
only if it has more than zero units **and** its expiry date is after today. A
unit that expires today is not kept.

**SCREEN:** `MergeSort` / `Merge` and `merge_sort`, `merge` (lines 29–76).

Step two is Merge Sort. If the list has zero or one item, it is already in
order, so it just returns. That is the base case that stops the recursion.
Otherwise it finds the middle, sorts the left half, sorts the right half, and
calls Merge.

Merge is where the real work happens. `i` points at the next item on the left,
and `j` at the next item on the right. I compare those two items, copy the
smaller one into `result`, and move that pointer forward. Notice the sign here
is less than or equal. On a tie, the left item goes first, and the left item
was earlier in the original list, so equal items keep their order. That is
called a stable sort. When one side is finished, I copy what remains of the
other side.

I sort by blood type, and blood types are compared as plain text. So `A+` comes
before `A-`, because the plus character comes before the minus character.

**SCREEN:** `FindFirst` / `FindLast` and `find_first`, `find_last`
(lines 79–130).

Step three is Binary Search. In the sorted list, all the units of one blood
type sit together in one block. A normal binary search finds only one of them.
I need the whole block, so I have two versions.

FindFirst looks at the middle item. If the middle is smaller than the target,
`low` moves to `mid + 1`. If it is bigger, `high` moves to `mid - 1`. If it
matches, I save the position in `answer`, but I do not stop. I move `high` to
`mid - 1` and keep looking left, in case there is an earlier one.

FindLast is the same with one line changed: after a match it moves `low` to
`mid + 1` and keeps looking right. If the blood type is not in the list at all,
`answer` stays at minus one.

**SCREEN:** `FindCompatibleUnits` and `find_compatible_units` (lines 133–150).

Step four is FindCompatibleUnits. For each donor type in the compatibility
table, it calls FindFirst. If the answer is not minus one, it calls FindLast
and copies the block between the two positions into `matches`. At that point
the matches are grouped by blood type, so I run the same Merge Sort a second
time, now by distance. That puts the nearest hospital at the top.

**SCREEN:** `src/locator.py`.

The main routine also handles three edge cases: no records loaded, an invalid
blood type, and no compatible units available.

---

## Segment 3 — Algorithm Tracing (4:00 – 9:00)

**SCREEN:** `docs/tracing.md` in Markdown preview. Point at each row with the
mouse as you say it.

**SAY:**

Now I will trace the algorithm on a small sample: the first six usable records
of my dataset. Every row in these tables was printed by the real functions, so
the trace matches the code.

**SCREEN:** "The 6-record sample".

The blood types, in the order of the file, are: `O+`, `A-`, `B+`, `O-`, `A+`,
`O+`. There are two `O+` records: Matina Crossing at position 0 and Bajada
General at position 5. Remember those two.

**SCREEN:** "Merge Sort trace" table.

Merge Sort first. There are six items, so `mid` is 3. The list is cut into
`O+, A-, B+` on the left and `O-, A+, O+` on the right. Each half is cut again
until every piece has one item. Then the merging starts.

Merge 1 joins `A-` and `B+`. `A-` is less than or equal to `B+`, so I take the
left. The left is finished, so I copy the rest. Result: `A-, B+`.

Merge 2 joins `O+` with `A-, B+`. `O+` is bigger than `A-`, take right. `O+` is
bigger than `B+`, take right. The right is finished, so `O+` goes last. The
left half is now `A-, B+, O+`.

Merges 3 and 4 do the same for the right half and give `A+, O+, O-`.

Merge 5 is the important one. It joins the two sorted halves, and `i` and `j`
both start at 0.

- Step 11: `A-` against `A+`. Is `A-` less than or equal to `A+`? No, because
  plus comes before minus. Take right. `j` becomes 1.
- Step 12: `A-` against `O+`. True, take left. `i` becomes 1.
- Step 13: `B+` against `O+`. True, take left. `i` becomes 2.
- Step 14: `O+` against `O+`. They are equal. Because I use less than or equal,
  the test is true and I take the left one. The left `O+` is Matina, which came
  first in the original list. So Matina stays in front of Bajada. This one step
  is why the sort is stable.
- Step 15: the left is finished, so I copy the rest of the right: `O+` and
  `O-`.

The sorted registry is `A+, A-, B+, O+, O+, O-`. That took 15 steps in 5
merges.

**SCREEN:** "Binary Search trace — find_first for O+".

Now Binary Search for `O+` on that sorted registry. This is FindFirst. `low` is
0, `high` is 5, and `answer` is minus one.

- Step 1: `mid` is 0 plus 5, divided by 2, which is 2. Position 2 is `B+`. `B+`
  is smaller than `O+`, so `low` becomes 3.
- Step 2: `low` 3, `high` 5, so `mid` is 4. Position 4 is `O+`. A match.
  `answer` becomes 4, but I keep looking left: `high` becomes 3.
- Step 3: `low` 3, `high` 3, `mid` 3. Position 3 is also `O+`. `answer` becomes
  3 and `high` becomes 2.

Now `low` is 3 and `high` is 2. `low` is greater than `high`, so the loop
stops. FindFirst returns 3.

**SCREEN:** "find_last for O+".

FindLast. Step 1 is the same: `mid` 2, `B+`, `low` becomes 3.

- Step 2: `mid` is 4, `O+`, a match. `answer` is 4, and this time `low` becomes
  5, to look right.
- Step 3: `low` 5, `high` 5, `mid` 5. Position 5 is `O-`, which is bigger than
  `O+`, so `high` becomes 4.

`low` is 5 and `high` is 4, so the loop stops. FindLast returns 4. So every
`O+` unit is in positions 3 to 4, and each search needed only three steps.

**SCREEN:** "a blood type that is not there".

One more case: a type that is not in the sample, `AB-`. `mid` 2 is `B+`, which
is bigger than `AB-`, so `high` becomes 1. `mid` 0 is `A+`, which is smaller,
so `low` becomes 1. `mid` 1 is `A-`, also smaller, so `low` becomes 2. Now
`low` has passed `high`. `answer` never changed, so FindFirst returns minus
one, and FindLast is skipped.

**SCREEN:** "Second Merge Sort (by distance)".

The last step. An `O+` patient can receive `O+` and `O-`. The block for `O+` is
positions 3 to 4, and the block for `O-` is position 5. So `matches` has three
records, with distances 3.2, 1.9 and 27.4. The second Merge Sort, by distance,
merges 1.9 with 27.4, and then 3.2 goes between them.

The final order is Bajada General at 1.9 km, Matina Crossing at 3.2, and
Calinan Valley at 27.4. That is the output of the algorithm.

---

## Segment 4 — Live Application Demonstration (9:00 – 11:00)

**SCREEN:** A terminal in the project folder, then the application window.

**SAY and DO:**

**DO:** Run `python main.py`.

Now the real application. The window loads my CSV file: 22 records from 14
hospitals, in no particular order. The Today field is filled with the system
date, and I can change it.

**DO:** Pick **O+**, press **Find units**.

There are 8 records. Only `O+` and `O-` appear, because those are the types an
`O+` patient can receive. The nearest is first: Bajada General at 1.9 km. The
farthest is Calinan Valley at 27.4.

Two records are missing on purpose. Panacan Family Hospital has `O+` but zero
units, and Bangkal Hillside has `O-` that expired in 2025. Bangkal is only
2.5 km away, so without the filter it would wrongly be second.

**DO:** Open the **Trace** tab and scroll through it.

The Trace tab shows the same six-record trace I just did by hand, produced live
by the code: the five merges, then FindFirst returns 3 and FindLast returns 4.

**DO:** Pick **AB-**, press **Find units**, stay on the Trace tab, then open
Results.

For `AB-`, FindFirst returns minus one, because `AB-` is not in the sample. The
Results tab still shows 9 records, because the full dataset does have
compatible units.

**DO:** Pick **A+**, press **Find units**, look at Results.

`A+` gives 13 records. Look at the ties. Matina has `A-` and `O+`, both at
3.2 km, and Talomo and Agdao are both at 4.1. They stay in the order of the
compatibility table, because the sort is stable.

**DO:** Change **Today** to `2030-01-01`, press **Find units**.

Last, an edge case. By 2030 every unit is expired, so the message is "No
compatible units available."

---

## Segment 5 — Complexity Analysis (11:00 – 14:00)

**SCREEN:** `docs/complexity.md` in preview, at "7. Summary table". Keep
`src/algorithms.py` ready to point at a loop.

**SAY:**

For the complexity, `n` is the number of records, and `k` is the number of
records that match the patient.

FilterUsable is one loop over `n` records, so the time is O(n). Its new list
can hold up to `n` records, so the extra space is O(n).

Merge Sort. The list is cut in half again and again until the pieces have one
item. A list of 8 can be halved 3 times, so there are log n levels. At every
level, the merges handle all `n` items once. That is `n` work per level, times
log n levels: O(n log n). It is the same in the best, average and worst case,
because my code always cuts in the middle and always merges, even when the list
is already in order. The extra space is O(n), because Merge builds a new
`result` list.

Binary Search. Every pass of the loop throws away half of the range. For my 20
usable records the range goes 20, 10, 5, 2, 1, so there are at most 5 passes.
That is O(log n). It is a loop, not recursion, and it only uses four variables:
`low`, `high`, `mid` and `answer`. So the extra space is O(1). Because it keeps
looking after a match, the best case is also about log n passes, not one.

FindCompatibleUnits. The patient with the most donor types is `AB+`, with 8.
So there are at most 16 binary searches. 16 is a constant, so the searching is
O(log n). Copying the blocks is `k`, and sorting `k` matches by distance is
k log k. The total is O(log n + k log k), with O(k) extra space.

So preparing the registry costs O(n log n), once. After that, each patient
costs O(log n + k log k).

**SCREEN:** "8. Trade-off: sort once and search, or scan every time?"

Is that efficient? Compare it with the simple way: scanning the whole list for
every patient, which costs `n` every time. Take 10,000 records, 50 matches and
1,000 patients. Sorting once and using binary search is about 699,000 steps in
total. The linear scan is about 10.3 million. That is about 15 times less work,
and the cost of sorting is paid back after about 15 patients.

To be fair, a linear scan would be fine for a very small list or for a single
search. And for an `AB+` patient almost every record matches, so `k` is close
to `n`, and the distance sort becomes the main cost.

---

## Segment 6 — Conclusion (14:00 – 15:00)

**SCREEN:** Your face, large. Behind it, the application showing the O+
results (change Today back to the real date first).

**SAY:**

To summarize: the Emergency Blood Unit Locator removes the unusable units,
sorts the registry once with Merge Sort, finds each compatible block with two
binary searches, and sorts the matches by distance. The result is the nearest
compatible hospital, first.

It has limitations. Merge Sort needs O(n) extra memory. The registry has to be
filtered and sorted again whenever a new file is loaded or the date changes.
The data is fictional and comes from a CSV file, not from live hospital
systems. And the distance is one fixed number, not the real travel time.

For improvements, I would connect it to a live hospital inventory. I would use
road distance or travel time. I would let the user enter how many units are
needed, and combine hospitals until that number is reached. And I would insert
a new record at its correct position in the sorted registry instead of sorting
everything again.

Thank you for watching.
