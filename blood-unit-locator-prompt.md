# Claude Code Prompt — Emergency Blood Unit Locator (Python)

> Paste everything below into Claude Code, run it from an **empty project folder**.
> Claude Code must work through the six phases **in order** and stop where told to.

---

## 1. DISCUSS

Before writing any code, discuss the project with me.

- Restate the problem, the algorithms, and the deliverables in your own words so I can confirm we agree.
- Ask me **at most 5 short questions** about anything unclear (e.g., Python version, GUI preferences, dataset size).
- Point out any risk you see in the pseudocode or requirements below.

**Stop after this phase and wait for my answers.**

---

## 2. CONTEXT

### Who I am
I am a 2nd-year Computer Science student. This is an **individual final project for my Algorithms course**. I must record a video where I trace the algorithm and explain the code **in my own words**, so the code must be simple, readable, and something I can defend line by line.

### The real-world problem
In a medical emergency, responders need compatible blood units quickly. Hospitals report their blood stock in no particular order. The system must:

1. Remove units that are unusable (0 units or expired).
2. Sort the registry by blood type **once** (Merge Sort).
3. For a patient's blood type, find **all compatible** donor units using Binary Search (first and last occurrence).
4. Sort the matches by distance so the **nearest hospital appears first** (Merge Sort again — stable).

### Course rules (strict — these are graded)
- **Do NOT use** `sort()`, `sorted()`, `bisect`, `heapq`, `pandas`, `numpy`, or any library that does the sorting or searching for me. Merge Sort and Binary Search must be written by hand.
- Must have a **graphical user interface** (use **Tkinter** — built into Python, no install needed).
- Must accept input from the user **and** from a prepared dataset (CSV file).
- Must include **at least 3 test cases, including one edge case**.
- Use functions and clear variable names. Code readability matters more than cleverness.
- Algorithm correctness matters more than GUI looks.
- Deadline: **November 18, 2026, 5:00 PM**.

### Data record
```text
BloodUnit: hospital (str), blood_type (str), units (int), distance_km (float), expiry_date (date)
```

### Blood compatibility table (patient → donor types they can receive)
```text
O-  → O-
O+  → O+, O-
A-  → A-, O-
A+  → A+, A-, O+, O-
B-  → B-, O-
B+  → B+, B-, O+, O-
AB- → AB-, A-, B-, O-
AB+ → AB+, AB-, A+, A-, B+, B-, O+, O-
```

### Approved pseudocode (the Python code must follow this structure exactly)
```text
ALGORITHM FilterUsable(records, today)
    usable ← empty list
    FOR each record IN records
        IF record.units > 0 AND record.expiryDate > today THEN
            append record to usable
    RETURN usable

ALGORITHM MergeSort(list, key)
    IF length(list) ≤ 1 THEN RETURN list
    mid   ← length(list) DIV 2
    left  ← MergeSort(list[0 .. mid-1], key)
    right ← MergeSort(list[mid .. end], key)
    RETURN Merge(left, right, key)

ALGORITHM Merge(left, right, key)
    result ← empty list ; i ← 0 ; j ← 0
    WHILE i < length(left) AND j < length(right)
        IF left[i].key ≤ right[j].key THEN      // "≤" keeps the sort stable
            append left[i] to result ; i ← i + 1
        ELSE
            append right[j] to result ; j ← j + 1
    append remaining left[i ..] and right[j ..] to result
    RETURN result

ALGORITHM FindFirst(list, target)
    low ← 0 ; high ← length(list) - 1 ; answer ← -1
    WHILE low ≤ high
        mid ← (low + high) DIV 2
        IF list[mid].bloodType = target THEN answer ← mid ; high ← mid - 1
        ELSE IF list[mid].bloodType < target THEN low ← mid + 1
        ELSE high ← mid - 1
    RETURN answer

ALGORITHM FindLast(list, target)
    // Same as FindFirst, but on a match: answer ← mid ; low ← mid + 1

ALGORITHM FindCompatibleUnits(registry, patientType)
    matches ← empty list
    FOR each donorType IN COMPATIBLE[patientType]
        first ← FindFirst(registry, donorType)
        IF first ≠ -1 THEN
            last ← FindLast(registry, donorType)
            append registry[first .. last] to matches
    RETURN MergeSort(matches, distanceKm)

ALGORITHM BloodUnitLocator()
    records ← LoadRecords()
    IF records is empty THEN DISPLAY "No hospital records loaded." ; STOP
    usable   ← FilterUsable(records, today)
    registry ← MergeSort(usable, bloodType)        // sort ONCE
    patientType ← INPUT
    IF patientType NOT IN COMPATIBLE THEN DISPLAY "Invalid blood type." ; STOP
    results ← FindCompatibleUnits(registry, patientType)
    IF results is empty THEN DISPLAY "No compatible units available."
    ELSE DISPLAY results
```

### Expected complexity (code must not break these)
| Step | Time | Extra space |
|---|---|---|
| FilterUsable | O(n) | O(n) |
| MergeSort (registry) | O(n log n) | O(n) |
| FindFirst / FindLast | O(log n) | O(1) — **iterative, not recursive** |
| FindCompatibleUnits | O(log n + k log k) | O(k) |

---

## 3. PLAN

Produce a written plan **before** implementing. Include:

1. The final folder structure (see Section 6 for the required `.claude/` layout).
2. Each Python module, its functions, and which pseudocode block each function maps to.
3. The sample dataset you will create (at least 8 fictional hospitals, mixed blood types, at least one 0-unit record and one expired record).
4. The test cases (Section 4 lists the required ones).
5. Which agent and skill you will use at each step.

**Stop after the plan and wait for my approval.**

---

## 4. GOAL

The project is done when **all** of these are true:

- [ ] `python main.py` opens a Tkinter window that loads the CSV, lets me pick a patient blood type, and shows matching units sorted by nearest distance.
- [ ] The GUI can also show a **step-by-step trace** (Merge Sort merges and Binary Search `low / mid / high` values) for the video tracing segment.
- [ ] Merge Sort and Binary Search are hand-written and match the pseudocode one-to-one.
- [ ] `python -m unittest` passes all tests, including:
  1. **Many matches** — `O+` patient gets both `O+` and `O-` units, nearest first.
  2. **One match** — exactly one compatible hospital record exists.
  3. **Edge case** — `O-` patient when every `O-` record has 0 units or is expired → "No compatible units available."
  4. **Edge case** — empty dataset → "No hospital records loaded."
  5. **Edge case** — invalid blood type input (e.g., `"C+"`) → "Invalid blood type."
  6. Merge Sort stability test (equal distances keep their original order).
- [ ] A `docs/` folder contains: pseudocode, one full tracing table (6 records), test results (expected vs. actual), and complexity analysis — ready to paste into my 3–5 page report.
- [ ] Every function has a short docstring written in plain student-level English.

---

## 5. IMPLEMENT

Rules while coding:

- Implement in this order: `models.py` → `algorithms.py` → `data_loader.py` → tests → `gui.py` → `main.py`. Run the tests after each algorithm function.
- Keep the algorithm functions **pure** (no GUI code inside them) so they are easy to test and trace.
- Add an optional `trace` list parameter to `merge_sort`, `find_first`, and `find_last` that records each step (for the GUI trace view and the docs tracing table). The trace must not change the result.
- Use only the Python standard library (`tkinter`, `csv`, `datetime`, `dataclasses`, `unittest`).
- Short comments that explain **why**, not just what — I need to explain them in my video.
- After each module, give me a 3–5 line summary of what it does in plain words.
- Use the agents in `.claude/agents/` as described in Section 6, and say which one you are using.

---

## 6. BUILD

### Required project structure
```text
blood-unit-locator/
├── .claude/
│   ├── agents/
│   │   ├── algorithm-reviewer.md
│   │   ├── test-engineer.md
│   │   ├── trace-generator.md
│   │   ├── complexity-analyst.md
│   │   ├── debugger-agent.md
│   │   └── security-agent.md
│   ├── skills/
│   │   ├── no-builtin-check/SKILL.md
│   │   ├── trace-table/SKILL.md
│   │   ├── run-tests/SKILL.md
│   │   └── complexity-report/SKILL.md
│   ├── settings.json
│   └── settings.local.json
├── data/
│   └── hospitals.csv
├── src/
│   ├── models.py
│   ├── algorithms.py
│   ├── data_loader.py
│   └── gui.py
├── tests/
│   └── test_algorithms.py
├── docs/
│   ├── pseudocode.md
│   ├── tracing.md
│   ├── test_results.md
│   └── complexity.md
├── main.py
├── CLAUDE.md
├── .gitignore
└── README.md
```

### Step 6.1 — Create the agents (`.claude/agents/`)

Create each file with YAML frontmatter (`name`, `description`, `tools`) followed by its instructions.

**`algorithm-reviewer.md`**
```markdown
---
name: algorithm-reviewer
description: Use after any change to src/algorithms.py. Checks that merge_sort, merge, find_first, find_last and find_compatible_units match the approved pseudocode line by line and that no forbidden built-ins are used.
tools: Read, Grep, Glob
---
You review algorithm code for a student Algorithms project.
Check:
1. Each function maps one-to-one to the pseudocode in docs/pseudocode.md.
2. No use of sort(), sorted(), bisect, heapq, min()/max() for ordering, pandas or numpy.
3. Merge uses "<=" so the sort is stable.
4. find_first / find_last are iterative and use O(1) extra space.
5. Variable names match the pseudocode (low, mid, high, left, right, i, j, result).
Report: PASS/FAIL per check, with file and line numbers. Do not edit files.
```

**`test-engineer.md`**
```markdown
---
name: test-engineer
description: Use to write or extend unit tests in tests/ and to record expected vs actual results in docs/test_results.md.
tools: Read, Write, Edit, Bash
---
You write unittest test cases for a blood unit locator.
Every test must state the input, the expected output, and why it matters.
Required coverage: many matches, one match, all-unusable edge case, empty dataset,
invalid blood type, Merge Sort stability, single-element and two-element lists.
After running tests, update docs/test_results.md with a table:
Test | Input | Expected | Actual | Pass/Fail.
```

**`trace-generator.md`**
```markdown
---
name: trace-generator
description: Use to produce step-by-step tracing tables of Merge Sort and Binary Search for the report and the video tracing segment.
tools: Read, Write, Bash
---
You generate tracing tables using the trace output of the real code (never invent steps).
Merge Sort table columns: Step | Sub-list Left | Sub-list Right | i | j | Comparison | Result.
Binary Search table columns: Step | low | mid | high | registry[mid].blood_type | Comparison | Action.
Use a 6-record sample. Keep the wording simple enough to read aloud in a 5-minute video.
Write output to docs/tracing.md.
```

**`complexity-analyst.md`**
```markdown
---
name: complexity-analyst
description: Use to write and verify the time and space complexity analysis in docs/complexity.md.
tools: Read, Write
---
Derive Big O from the actual loops and recursion in src/algorithms.py — never just state it.
For each function explain: input size, how many times each loop runs, recursion depth,
and extra memory. Include the trade-off: Q queries cost n log n + Q(log n + k log k)
with sort-once-then-search versus Q·n with linear search. List strengths and limitations.
```

**`debugger-agent.md`**
```markdown
---
name: debugger-agent
description: Use when a test fails, the GUI crashes, or output is wrong. Finds the root cause and proposes the smallest fix.
tools: Read, Grep, Glob, Bash, Edit
---
Reproduce the bug first with a failing test or a command.
Find the root cause (off-by-one in low/high, wrong slice in merge, wrong key, date parsing, etc.).
Propose the smallest fix, explain it in 2–3 plain sentences, apply it, and re-run all tests.
Never "fix" by replacing hand-written algorithms with built-ins.
```

**`security-agent.md`**
```markdown
---
name: security-agent
description: Use before finishing to check input validation and safe data handling in data_loader.py and gui.py.
tools: Read, Grep, Glob
---
Check: CSV rows with missing fields, non-numeric units/distance, bad dates, negative values,
unknown blood types, empty file, and GUI input that is not in the compatibility table.
The app must show a clear message instead of crashing. Report issues with file and line; do not edit files.
```

### Step 6.2 — Create the skills (`.claude/skills/`)

Each skill is a folder with a `SKILL.md` containing `name` and `description` frontmatter, then the instructions.

**`no-builtin-check/SKILL.md`**
```markdown
---
name: no-builtin-check
description: Scan the source code for forbidden built-in sorting or searching calls. Use before every commit and before finishing the project.
---
Run: grep -rnE "sorted\(|\.sort\(|bisect|heapq|import pandas|import numpy" src/ main.py
If anything is found, report the file and line and stop. A clean result prints nothing.
```

**`trace-table/SKILL.md`**
```markdown
---
name: trace-table
description: Generate a Markdown tracing table from the real trace output of merge_sort or find_first/find_last for a given sample.
---
1. Load the 6-record sample from data/hospitals.csv (first 6 usable rows).
2. Call the function with trace=[] and collect the steps.
3. Format as a Markdown table (columns defined by the trace-generator agent).
4. Append to docs/tracing.md with a one-line explanation per step.
```

**`run-tests/SKILL.md`**
```markdown
---
name: run-tests
description: Run all unit tests and summarise the results as expected vs actual.
---
Run: python -m unittest discover -s tests -v
Summarise: total, passed, failed. For each failure, show the test name and the assertion message.
If any test fails, hand off to the debugger-agent.
```

**`complexity-report/SKILL.md`**
```markdown
---
name: complexity-report
description: Build or refresh docs/complexity.md with justified time and space complexity for every algorithm function.
---
For each function in src/algorithms.py, write: what n means, loop/recursion count,
resulting Big O for time, extra memory used, and one sentence on strengths/limitations.
End with the overall pipeline cost and the comparison with linear search.
```

### Step 6.3 — Create the settings

**`.claude/settings.json`** (shared project settings)
```json
{
  "permissions": {
    "allow": [
      "Bash(python:*)",
      "Bash(python -m unittest:*)",
      "Bash(grep:*)",
      "Read(./**)",
      "Edit(./src/**)",
      "Edit(./tests/**)",
      "Edit(./docs/**)"
    ],
    "deny": [
      "Bash(pip install:*)",
      "Bash(rm -rf:*)",
      "Read(./.env)"
    ]
  }
}
```

**`.claude/settings.local.json`** (my personal settings — add to `.gitignore`)
```json
{
  "permissions": {
    "allow": []
  }
}
```

### Step 6.4 — Create `CLAUDE.md`

Summarise the course rules from Section 2 (no built-ins, Tkinter GUI, pseudocode is the source of truth, simple student-level code) so every future Claude Code session follows them.

### Step 6.5 — Build, verify, and hand over

1. Build the code following Section 5.
2. Run the `run-tests` skill → all tests must pass.
3. Run the `no-builtin-check` skill → must be clean.
4. Ask the `algorithm-reviewer` and `security-agent` to review; fix anything they report.
5. Use the `trace-generator` and `complexity-analyst` to fill `docs/`.
6. Launch `python main.py` and describe what I should see.
7. Finish with a short **"How to explain this in your video"** section: for each algorithm function, 2–3 sentences I can say in my own words.
