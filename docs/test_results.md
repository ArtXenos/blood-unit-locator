# Test Results

Command: `python -m unittest discover -s tests -v` | Date run: 2026-11-12 | Python 3.14.7 | Total: 72 | Passed: 72 | Failed: 0

All tests are in `tests/test_algorithms.py`. Every test uses the fixed date
`TODAY = 2026-11-01` and records made in memory, so the results do not depend on
the real clock. The only tests that touch files are the CSV loader tests, which
use small temporary files and the project file `data/hospitals.csv`.

The "Actual" column shows what the program returned in the run above. A test is
marked Pass only when the actual value was equal to the expected value.

## Required test cases

These six tests are in the class `TestLocator`. Each one runs the whole
pipeline: remove unusable records, Merge Sort by blood type, Binary Search for
each compatible donor type, Merge Sort by distance.

| Test | Input | Expected | Actual | Pass/Fail |
|---|---|---|---|---|
| 1. Many matches (`test_1_many_matches_o_positive_patient`) | Patient O+. Nine records in no particular order: O+ at 6.0, 0.9 and 4.1 km; O- at 2.5 and 8.2 km; A+ at 1.0 km; B+ at 3.0 km; O+ with 0 units at 0.5 km; expired O- at 0.3 km | Only usable O+ and O- units, nearest first: Mintal Doctors Hospital (O+, 0.9), Toril Community Hospital (O-, 2.5), Lanang Bayview Medical Center (O+, 4.1), Bajada General Hospital (O+, 6.0), Agdao Mercy Hospital (O-, 8.2). Message is empty | Mintal (O+, 0.9), Toril (O-, 2.5), Lanang (O+, 4.1), Bajada (O+, 6.0), Agdao (O-, 8.2). Message is empty | Pass |
| 2. One match (`test_2_one_match`) | Patient O-. Records: A+ at 1.0 km, O- at 7.0 km, B+ at 2.0 km, O- with 0 units at 0.5 km | A list with one record: Toril Community Hospital (O-, 7.0). Message is empty | One record: Toril Community Hospital (O-, 7.0). Message is empty | Pass |
| 3. **Edge case:** all units unusable (`test_3_edge_all_o_negative_units_unusable`) | Patient O-. Three O- records: one with 0 units, one expired on 2025-01-15, one expiring exactly today (2026-11-01). Also a usable A+ and a usable O+ record | Empty list and "No compatible units available." | Empty list and "No compatible units available." | Pass |
| 4. **Edge case:** empty dataset (`test_4_edge_empty_dataset`) | An empty list of records | Empty registry and "No hospital records loaded." | Empty registry and "No hospital records loaded." | Pass |
| 5. **Edge case:** invalid blood type (`test_5_edge_invalid_blood_type`) | Patient types "C+", "" (empty) and "o+" (lower case) on a registry with usable O+ and A+ units | Empty list and "Invalid blood type." for all three | Empty list and "Invalid blood type." for all three | Pass |
| 6. Stability (`test_6_stability_equal_distances_keep_order`) | Patient O+. Records in this order: Toril O- 3.0, Bajada O+ 3.0, Mintal O+ 3.0, Agdao O+ 1.0, Buhangin O- 3.0 | Agdao (1.0) first, then the four units at 3.0 km in their kept order: Bajada, Mintal (O+), Toril, Buhangin (O-) | Agdao (1.0), Bajada (3.0), Mintal (3.0), Toril (3.0), Buhangin (3.0) | Pass |

Tests 3, 4 and 5 are the three edge cases.

## Additional tests

### filter_usable (class `TestFilterUsable`)

| Test | Input | Expected | Actual | Pass/Fail |
|---|---|---|---|---|
| `test_keeps_good_units` | Two units with stock, expiring in 2027 | Both kept, same order | Both kept, same order | Pass |
| `test_removes_zero_unit_records` | One unit with 0 units, one with 3 | Only the unit with 3 | Only the unit with 3 | Pass |
| `test_removes_expired_records` | One unit expired 2025-01-15, one good | Only the good unit | Only the good unit | Pass |
| `test_unit_expiring_today_is_removed` | One unit expiring 2026-11-01 (today), one expiring 2026-11-02 | Only the 2026-11-02 unit | Only the 2026-11-02 unit | Pass |
| `test_empty_list_gives_empty_list` | Empty list | Empty list | Empty list | Pass |
| `test_all_unusable_gives_empty_list` | 0 units, expired, expiring today | Empty list | Empty list | Pass |

### merge_sort (class `TestMergeSort`)

| Test | Input | Expected | Actual | Pass/Fail |
|---|---|---|---|---|
| `test_empty_list` | Empty list | Empty list | Empty list | Pass |
| `test_single_element_list` | One unit | The same one unit | The same one unit | Pass |
| `test_two_elements_already_in_order` | Distances 1.5, 6.0 | 1.5, 6.0 | 1.5, 6.0 | Pass |
| `test_two_elements_reversed` | Distances 6.0, 1.5 | 1.5, 6.0 | 1.5, 6.0 | Pass |
| `test_six_records_by_blood_type` | Types O+, A-, B+, O+, AB+, A+ | A+, A-, AB+, B+, O+, O+ | A+, A-, AB+, B+, O+, O+ | Pass |
| `test_orders_by_distance` | Distances 7.5, 2.0, 9.1, 0.8, 4.4 | 0.8, 2.0, 4.4, 7.5, 9.1 | 0.8, 2.0, 4.4, 7.5, 9.1 | Pass |
| `test_stability_equal_distances_keep_original_order` | Bajada 3.0, Toril 1.0, Buhangin 3.0, Mintal 3.0, Agdao 2.0 | Toril, Agdao, Bajada, Buhangin, Mintal | Toril, Agdao, Bajada, Buhangin, Mintal | Pass |
| `test_input_list_is_not_modified` | Distances 5.0, 1.0, 3.0 | Input still 5.0, 1.0, 3.0; result 1.0, 3.0, 5.0 | Input still 5.0, 1.0, 3.0; result 1.0, 3.0, 5.0 | Pass |

### merge (class `TestMerge`)

| Test | Input | Expected | Actual | Pass/Fail |
|---|---|---|---|---|
| `test_merge_two_ordered_lists` | Left 1.0, 4.0; right 2.0, 3.0, 5.0 | 1.0, 2.0, 3.0, 4.0, 5.0 | 1.0, 2.0, 3.0, 4.0, 5.0 | Pass |
| `test_merge_with_empty_left` | Left empty; right 2.0, 3.0 | 2.0, 3.0 | 2.0, 3.0 | Pass |
| `test_merge_with_empty_right` | Left 1.0, 4.0; right empty | 1.0, 4.0 | 1.0, 4.0 | Pass |
| `test_merge_tie_takes_left_item_first` | Left Bajada 2.0; right Toril 2.0 | Bajada, Toril | Bajada, Toril | Pass |

### find_first and find_last (class `TestFindFirstAndFindLast`)

Registry used (positions 0 to 7): A+, A-, A-, B+, O+, O+, O+, O-.

| Test | Input | Expected | Actual | Pass/Fail |
|---|---|---|---|---|
| `test_registry_is_in_the_documented_order` | Eight records out of order, ordered by blood type | A+, A-, A-, B+, O+, O+, O+, O- | A+, A-, A-, B+, O+, O+, O+, O- | Pass |
| `test_run_of_duplicates` | Target O+ | First 4, last 6 | First 4, last 6 | Pass |
| `test_type_that_occurs_once` | Target B+ | First 3, last 3 | First 3, last 3 | Pass |
| `test_type_at_the_very_start` | Target A+ | First 0, last 0 | First 0, last 0 | Pass |
| `test_type_at_the_very_end` | Target O- | First 7, last 7 | First 7, last 7 | Pass |
| `test_missing_type_gives_minus_one` | Target AB+ (not in registry) | First -1, last -1 | First -1, last -1 | Pass |
| `test_empty_registry_gives_minus_one` | Empty registry, target O+ | First -1, last -1 | First -1, last -1 | Pass |

### find_compatible_units (class `TestFindCompatibleUnits`)

| Test | Input | Expected | Actual | Pass/Fail |
|---|---|---|---|---|
| `test_many_matches_for_o_positive_patient` | Patient O+; O+ at 6.0, 0.9, 4.1; O- at 2.5, 8.2; one A+; one B+ | Mintal 0.9, Toril 2.5, Lanang 4.1, Bajada 6.0, Agdao 8.2 | Mintal 0.9, Toril 2.5, Lanang 4.1, Bajada 6.0, Agdao 8.2 | Pass |
| `test_one_match` | Patient O-; one O-, one A+, one B+ | Only Toril (O-) | Only Toril (O-) | Pass |
| `test_no_compatible_units_gives_empty_list` | Patient O-; only A+ and B+ units | Empty list | Empty list | Pass |
| `test_empty_registry_gives_empty_list` | Patient AB+; empty registry | Empty list | Empty list | Pass |
| `test_equal_distance_o_positive_before_o_negative` | Patient O+; O- and O+ both at 3.0 km | O+ unit, then O- unit | O+ unit, then O- unit | Pass |
| `test_equal_distance_follows_table_order_not_registry_order` | Patient AB+; A+ and AB+ both at 3.0 km | AB+ unit, then A+ unit | AB+ unit, then A+ unit | Pass |

### Trace (class `TestTrace`)

| Test | Input | Expected | Actual | Pass/Fail |
|---|---|---|---|---|
| `test_merge_sort_trace_does_not_change_result` | Distances 4.0, 1.0, 3.0, 2.0, with and without a trace list | Same result 1.0, 2.0, 3.0, 4.0; trace not empty | Same result 1.0, 2.0, 3.0, 4.0; trace not empty | Pass |
| `test_merge_trace_steps_have_expected_keys` | Merge Sort on four units with a trace list | Every step has left, right, i, j, took, result | Every step has all six keys | Pass |
| `test_find_first_trace_does_not_change_result` | Target O+, with and without a trace list | 4 both times; trace not empty | 4 both times; trace not empty | Pass |
| `test_find_last_trace_does_not_change_result` | Target O+, with and without a trace list | 6 both times; trace not empty | 6 both times; trace not empty | Pass |
| `test_missing_type_trace_still_gives_minus_one` | Target AB+ with a trace list | -1 from both; traces not empty | -1 from both; traces not empty | Pass |
| `test_binary_search_trace_steps_have_expected_keys` | find_first and find_last for O+ with trace lists | Every step has low, mid, high, value, target | Every step has all five keys | Pass |
| `test_find_first_trace_matches_hand_trace` | find_first for O+ with a trace list | Three steps (low, mid, high, value): (0, 3, 7, B+), (4, 5, 7, O+), (4, 4, 4, O+) | The same three steps | Pass |

### prepare_registry and messages (class `TestLocator`)

| Test | Input | Expected | Actual | Pass/Fail |
|---|---|---|---|---|
| `test_prepare_registry_orders_by_blood_type_and_removes_unusable` | Usable O+, A-, A+; B+ with 0 units; expired O- | Three records: A+, A-, O+ | Three records: A+, A-, O+ | Pass |
| `test_prepare_registry_drops_unit_expiring_today` | O+ expiring 2026-11-01 (today), O+ expiring 2026-11-02 | Only the 2026-11-02 unit | Only the 2026-11-02 unit | Pass |
| `test_message_constants_have_the_exact_texts` | The three message constants | "No hospital records loaded.", "Invalid blood type.", "No compatible units available." | The same three texts | Pass |

### CSV loader: parse_row (class `TestDataLoader`)

| Test | Input | Expected | Actual | Pass/Fail |
|---|---|---|---|---|
| `test_parse_row_good_row` | Bajada General Hospital, O+, "6", "1.9", "2027-04-08" | Unit with 6 (whole number), 1.9 (decimal), date 2027-04-08; no problem text | Unit with 6, 1.9, date 2027-04-08; no problem text | Pass |
| `test_parse_row_trims_and_upper_cases_blood_type` | Blood type " o+ " | "O+" | "O+" | Pass |
| `test_parse_row_zero_units_is_valid` | Units "0" | Valid unit with 0 units | Valid unit with 0 units | Pass |
| `test_parse_row_missing_field` | Row with no units value | No unit; problem text given | No unit; problem text given | Pass |
| `test_parse_row_blank_field` | Hospital name of only spaces | No unit; problem text given | No unit; problem text given | Pass |
| `test_parse_row_non_numeric_units` | Units "abc" | No unit; problem text given | No unit; problem text given | Pass |
| `test_parse_row_negative_units` | Units "-3" | No unit; problem text given | No unit; problem text given | Pass |
| `test_parse_row_non_numeric_distance` | Distance "far" | No unit; problem text given | No unit; problem text given | Pass |
| `test_parse_row_negative_distance` | Distance "-2.5" | No unit; problem text given | No unit; problem text given | Pass |
| `test_parse_row_nan_distance` | Distance "nan" | No unit; problem text given | No unit; problem text given | Pass |
| `test_parse_row_inf_distance` | Distance "inf" | No unit; problem text given | No unit; problem text given | Pass |
| `test_parse_row_impossible_date` | Expiry "2027-02-30" | No unit; problem text given | No unit; problem text given | Pass |
| `test_parse_row_wrong_date_format` | Expiry "15/03/2027" | No unit; problem text given | No unit; problem text given | Pass |
| `test_parse_row_unknown_blood_type` | Blood type "C+" | No unit; problem text given | No unit; problem text given | Pass |
| `test_parse_row_too_many_values` | Good row plus one extra value past the last column | No unit; problem text given | No unit; problem text given | Pass |
| `test_parse_row_hospital_name_with_line_break` | Hospital name with a line break inside ("Bajada General", new line, "Hospital") | No unit; problem text given | No unit; problem text given | Pass |
| `test_parse_row_units_must_be_plain_digits` | Units "+5", "1_000" and "3.5" | All three refused: no unit; problem text given | All three refused: no unit; problem text given | Pass |
| `test_parse_row_units_with_spaces_is_accepted` | Units " 7 " (spaces around) | Valid unit with 7 units | Valid unit with 7 units | Pass |

### CSV loader: load_records (class `TestDataLoader`)

| Test | Input | Expected | Actual | Pass/Fail |
|---|---|---|---|---|
| `test_load_records_good_file` | Temporary file: header and two good rows | 2 records in file order; 0 skipped | 2 records in file order; 0 skipped | Pass |
| `test_load_records_skips_bad_rows` | Temporary file: two good rows and three bad rows (units "abc", type "C+", date "2027-02-30") | 2 records kept; 3 skipped; no crash | 2 records kept; 3 skipped; no crash | Pass |
| `test_load_records_skips_row_with_extra_value` | Temporary file: three rows, the middle one with an extra value after the date | 2 records kept (first and third rows); 1 skipped | 2 records kept (first and third rows); 1 skipped | Pass |
| `test_load_records_header_only_file` | Temporary file with only the header | 0 records; 0 skipped | 0 records; 0 skipped | Pass |
| `test_load_records_empty_file` | Temporary file with nothing in it | 0 records; 0 skipped | 0 records; 0 skipped | Pass |
| `test_load_records_missing_column` | Temporary file with no expiry_date column | 0 records; skipped list not empty | 0 records; skipped list not empty | Pass |
| `test_load_real_dataset` | `data/hospitals.csv` | 22 records; 0 skipped; at least one with 0 units; at least one expired before 2026-11-01 | 22 records; 0 skipped; both kinds of unusable record present | Pass |
