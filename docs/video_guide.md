# Video Guide — Emergency Blood Unit Locator

Notes for the recorded explanation. Part 1 is the recording plan: the six
required segments, what to show in each one, and the checklists. Part 2 has two
or three sentences for each function. Part 3 is the 2-minute live demo. The
full spoken script is in `docs/video_script.md`. Say everything in your own
words; these are prompts, not lines to read out.

Deadline: November 18, 2026, 5:00 PM.

## Part 1 — Recording plan

### The six segments (15 minutes in total)

| # | Segment | Time | Length | Show on screen | Must cover |
|---|---|---|---|---|---|
| 1 | Introduction | 0:00 – 1:00 | 1 min | Face large, `README.md` preview behind it | Project title and the real-world problem |
| 2 | Algorithm Explanation | 1:00 – 4:00 | 3 min | `docs/pseudocode.md` beside `src/algorithms.py`, then `src/locator.py` | Why Merge Sort and Binary Search, and the pseudocode block by block |
| 3 | Algorithm Tracing | 4:00 – 9:00 | 5 min | `docs/tracing.md` preview | Merge Sort on 6 records, `find_first` and `find_last` for O+, the -1 case, the distance sort |
| 4 | Live Application Demonstration | 9:00 – 11:00 | 2 min | Terminal, then the application window | Run it, give sample inputs, show the results (Part 3 below) |
| 5 | Complexity Analysis | 11:00 – 14:00 | 3 min | `docs/complexity.md` preview, sections 7 and 8 | Time and space for each step, and sort-once against a linear scan |
| 6 | Conclusion | 14:00 – 15:00 | 1 min | Face large, application behind it | Summary, limitations, possible improvements |

Stay close to these lengths. If a segment runs long, cut words, not content:
in Segment 3, Merges 1 to 4 can be said in two sentences, but keep Merge 5
(step 14), both searches for O+, and the final order.

### What the guidelines ask for, and where it is covered

| Guideline | How this video meets it |
|---|---|
| Face visible during the speaking portions | Keep the webcam picture on for the whole recording, in a corner. |
| Screen recording shows the source code | Segment 2 shows `src/algorithms.py` and `src/locator.py` next to the pseudocode. |
| Screen recording shows the application running | Segment 4 runs `python main.py` live. |
| At least one algorithm tracing example | Segment 3 traces a 6-record sample; the Trace tab repeats it live in Segment 4. |
| Explain the code in your own words | Practise from keywords. Do not read the script or the code aloud line by line. |
| Clear audio | Quiet room, microphone test before the real take. |
| MP4 file or an accessible link | Export as MP4. If a link is submitted, check that it opens without signing in. |
| Able to explain and justify the implementation | Part 2 and "Questions you may be asked" below. Be ready to explain any line that is pointed at. |

### Before recording

1. Open a terminal in the project folder and run
   `python -m unittest discover -s tests -v`. It should end with `OK`.
2. Run `python main.py` once. Check that the **Today** field shows the real
   date and that the status bar says 22 records were loaded. Close it again so
   the demo starts from the terminal.
3. Open these files as editor tabs, in this order: `README.md`,
   `docs/pseudocode.md`, `src/algorithms.py`, `src/locator.py`,
   `docs/tracing.md`, `docs/complexity.md`. Use the Markdown preview for the
   `.md` files so the tables are readable.
4. Make the text big enough to read in the video: zoom the editor in a few
   steps, and close the side panels that are not needed.
5. Turn off notifications and close anything private (chats, email, other
   browser tabs).
6. Fill in the name, section and course blanks in Segment 1 of the script.

### Recording setup

- Record the screen and the webcam together, with the webcam as a small picture
  in a corner. Any screen recorder that can do both and save MP4 works.
- Put the webcam picture where it does not hide the code, the trace tables or
  the application's results table. The top-right corner is usually safest,
  because the application's status bar is at the bottom.
- Record a 10-second test first and play it back: is the face visible, is the
  voice clear and loud enough, can the code be read?
- Recording one segment at a time and joining the clips is easier than one
  15-minute take. A mistake then only costs one segment.
- Move the mouse to the row or line being explained. In Segment 3 the viewer
  should always know which row of the table is being read.

### Delivery tips

- Rehearse each segment with a timer at least twice before the real take.
- Write a small cue card of keywords for each segment (for example, for
  Segment 3: "sample, split, merges 1–4, merge 5, step 14 tie, find_first 3,
  find_last 4, AB- gives -1, distance sort, Bajada first").
- Speak a little slower than normal. The script leaves about one minute spare.
- When explaining code, say what the line is for, not what it literally says:
  "this keeps looking left for an earlier match", not "high equals mid minus
  one".
- After Segment 4, change **Today** back to the real date so the Conclusion
  does not show an empty table.

### Before submitting

- Watch the whole video once. Check the total length (about 15 minutes), the
  order of the six segments, and that the face is visible throughout.
- Check that the file is MP4 and plays on another device, or that the link
  opens in a private browser window.
- Submit before November 18, 2026, 5:00 PM, and leave time for the upload.

## Part 2 — What to say for each function

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

## Part 3 — Demo script (about 2 minutes)

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
