# Approved Pseudocode — Emergency Blood Unit Locator

This is the approved pseudocode from Section 2 of `blood-unit-locator-prompt.md`.
The Python code in `src/algorithms.py` and `src/locator.py` follows it block by block.

## Data record

```text
BloodUnit: hospital (str), blood_type (str), units (int), distance_km (float), expiry_date (date)
```

## Blood compatibility table (patient → donor types they can receive)

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

## Pseudocode

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

## Pseudocode block → Python function

| Pseudocode block | Python function | File |
|---|---|---|
| FilterUsable | `filter_usable(records, today)` | `src/algorithms.py` |
| MergeSort | `merge_sort(items, key, trace=None)` | `src/algorithms.py` |
| Merge | `merge(left, right, key, trace=None)` | `src/algorithms.py` |
| FindFirst | `find_first(registry, target, trace=None)` | `src/algorithms.py` |
| FindLast | `find_last(registry, target, trace=None)` | `src/algorithms.py` |
| FindCompatibleUnits | `find_compatible_units(registry, patient_type)` | `src/algorithms.py` |
| BloodUnitLocator | `prepare_registry(records, today)` and `search_patient(registry, patient_type)` | `src/locator.py` |

## Expected complexity

| Step | Time | Extra space |
|---|---|---|
| FilterUsable | O(n) | O(n) |
| MergeSort (registry) | O(n log n) | O(n) |
| FindFirst / FindLast | O(log n) | O(1) — iterative, not recursive |
| FindCompatibleUnits | O(log n + k log k) | O(k) |
