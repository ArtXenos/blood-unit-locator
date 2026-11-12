"""Tests for the six hand-written functions in src/algorithms.py.

Every test uses a fixed "today" date and small lists made in memory, so the
result never depends on the real clock or on a file. Expected values were
worked out by hand and are written as plain lists.

Each test docstring states the Input, the Expected output and Why it matters.
"""

import unittest
from datetime import date

from src.models import BloodUnit, get_blood_type, get_distance
from src.algorithms import (
    filter_usable,
    merge_sort,
    merge,
    find_first,
    find_last,
    find_compatible_units,
)

# The fixed "today" used by every test. Never the system clock.
TODAY = date(2026, 11, 1)


def make_unit(hospital, blood_type, units=5, distance_km=1.0,
              expiry_date=date(2027, 6, 30)):
    """Build one BloodUnit. The defaults describe a good, usable unit."""
    return BloodUnit(hospital, blood_type, units, distance_km, expiry_date)


def hospital_names(units):
    """Return the hospital names of a list of units, in the same order."""
    names = []
    for unit in units:
        names.append(unit.hospital)
    return names


def blood_types(units):
    """Return the blood types of a list of units, in the same order."""
    types = []
    for unit in units:
        types.append(unit.blood_type)
    return types


def distances(units):
    """Return the distances of a list of units, in the same order."""
    values = []
    for unit in units:
        values.append(unit.distance_km)
    return values


def make_search_registry():
    """Return an 8-record registry ordered by blood type.

    The records are given out of order and then ordered with merge_sort.
    Positions after ordering:
        0 A+   1 A-   2 A-   3 B+   4 O+   5 O+   6 O+   7 O-
    """
    records = [
        make_unit("Bajada General Hospital", "O+"),
        make_unit("Toril Community Hospital", "A-"),
        make_unit("Buhangin District Hospital", "O-"),
        make_unit("Mintal Doctors Hospital", "O+"),
        make_unit("Agdao Mercy Hospital", "B+"),
        make_unit("Sasa Wharfside Hospital", "A+"),
        make_unit("Lanang Bayview Medical Center", "O+"),
        make_unit("Panacan Family Hospital", "A-"),
    ]
    return merge_sort(records, get_blood_type)


class TestFilterUsable(unittest.TestCase):
    """Tests for filter_usable(records, today)."""

    def test_keeps_good_units(self):
        """Input: two units with stock and an expiry date in 2027.
        Expected: both units come back, in the same order.
        Why: good stock must never be thrown away by the filter.
        """
        records = [
            make_unit("Bajada General Hospital", "O+"),
            make_unit("Toril Community Hospital", "A-"),
        ]
        usable = filter_usable(records, TODAY)
        self.assertEqual(hospital_names(usable),
                         ["Bajada General Hospital", "Toril Community Hospital"])

    def test_removes_zero_unit_records(self):
        """Input: one unit with 0 units and one unit with 3 units.
        Expected: only the unit with 3 units is kept.
        Why: a hospital with no bags left cannot help the patient.
        """
        records = [
            make_unit("Bajada General Hospital", "O+", units=0),
            make_unit("Toril Community Hospital", "O+", units=3),
        ]
        usable = filter_usable(records, TODAY)
        self.assertEqual(hospital_names(usable), ["Toril Community Hospital"])

    def test_removes_expired_records(self):
        """Input: one unit that expired on 2025-01-15 and one good unit.
        Expected: only the good unit is kept.
        Why: expired blood is unsafe and must never be offered.
        """
        records = [
            make_unit("Bajada General Hospital", "O+",
                      expiry_date=date(2025, 1, 15)),
            make_unit("Toril Community Hospital", "O+"),
        ]
        usable = filter_usable(records, TODAY)
        self.assertEqual(hospital_names(usable), ["Toril Community Hospital"])

    def test_unit_expiring_today_is_removed(self):
        """Input: one unit expiring exactly on TODAY and one expiring the day after.
        Expected: only the unit expiring the day after is kept.
        Why: expiry is strict (expiry_date > today), so this checks the boundary.
        """
        records = [
            make_unit("Bajada General Hospital", "O+", expiry_date=TODAY),
            make_unit("Toril Community Hospital", "O+",
                      expiry_date=date(2026, 11, 2)),
        ]
        usable = filter_usable(records, TODAY)
        self.assertEqual(hospital_names(usable), ["Toril Community Hospital"])

    def test_empty_list_gives_empty_list(self):
        """Input: an empty list.
        Expected: an empty list.
        Why: the filter must not crash when no records were loaded.
        """
        self.assertEqual(filter_usable([], TODAY), [])

    def test_all_unusable_gives_empty_list(self):
        """Input: one 0-unit record, one expired record, one expiring today.
        Expected: an empty list.
        Why: this is the "all unusable" edge case that later leads to the
        message "No compatible units available.".
        """
        records = [
            make_unit("Bajada General Hospital", "O-", units=0),
            make_unit("Toril Community Hospital", "O-",
                      expiry_date=date(2025, 1, 15)),
            make_unit("Mintal Doctors Hospital", "O-", expiry_date=TODAY),
        ]
        self.assertEqual(filter_usable(records, TODAY), [])


class TestMergeSort(unittest.TestCase):
    """Tests for merge_sort(items, key)."""

    def test_empty_list(self):
        """Input: an empty list, ordered by distance.
        Expected: an empty list.
        Why: 0 items is a base case of the recursion and must not crash.
        """
        self.assertEqual(merge_sort([], get_distance), [])

    def test_single_element_list(self):
        """Input: a list with one unit.
        Expected: a list with that same one unit.
        Why: 1 item is the other base case that stops the recursion.
        """
        records = [make_unit("Bajada General Hospital", "O+", distance_km=4.0)]
        result = merge_sort(records, get_distance)
        self.assertEqual(hospital_names(result), ["Bajada General Hospital"])

    def test_two_elements_already_in_order(self):
        """Input: two units with distances 1.5 then 6.0.
        Expected: the same order, 1.5 then 6.0.
        Why: the smallest list that needs a merge must stay right when it
        is already in order.
        """
        records = [
            make_unit("Bajada General Hospital", "O+", distance_km=1.5),
            make_unit("Toril Community Hospital", "O+", distance_km=6.0),
        ]
        result = merge_sort(records, get_distance)
        self.assertEqual(hospital_names(result),
                         ["Bajada General Hospital", "Toril Community Hospital"])

    def test_two_elements_reversed(self):
        """Input: two units with distances 6.0 then 1.5.
        Expected: the order is swapped, 1.5 then 6.0.
        Why: the smallest list where the merge really has to move an item.
        """
        records = [
            make_unit("Toril Community Hospital", "O+", distance_km=6.0),
            make_unit("Bajada General Hospital", "O+", distance_km=1.5),
        ]
        result = merge_sort(records, get_distance)
        self.assertEqual(hospital_names(result),
                         ["Bajada General Hospital", "Toril Community Hospital"])

    def test_six_records_by_blood_type(self):
        """Input: six units with types O+, A-, B+, O+, AB+, A+ in that order.
        Expected: A+, A-, AB+, B+, O+, O+ (plain string order).
        Why: the registry is ordered by blood type once so that Binary
        Search can be used on it; "A-" must come before "AB+".
        """
        records = [
            make_unit("Bajada General Hospital", "O+"),
            make_unit("Toril Community Hospital", "A-"),
            make_unit("Buhangin District Hospital", "B+"),
            make_unit("Mintal Doctors Hospital", "O+"),
            make_unit("Agdao Mercy Hospital", "AB+"),
            make_unit("Sasa Wharfside Hospital", "A+"),
        ]
        result = merge_sort(records, get_blood_type)
        self.assertEqual(blood_types(result),
                         ["A+", "A-", "AB+", "B+", "O+", "O+"])
        self.assertEqual(hospital_names(result), [
            "Sasa Wharfside Hospital",
            "Toril Community Hospital",
            "Agdao Mercy Hospital",
            "Buhangin District Hospital",
            "Bajada General Hospital",
            "Mintal Doctors Hospital",
        ])

    def test_orders_by_distance(self):
        """Input: five units with distances 7.5, 2.0, 9.1, 0.8, 4.4.
        Expected: 0.8, 2.0, 4.4, 7.5, 9.1.
        Why: the final answer must show the nearest hospital first. An odd
        number of items also checks an uneven split.
        """
        records = [
            make_unit("Bajada General Hospital", "O+", distance_km=7.5),
            make_unit("Toril Community Hospital", "O+", distance_km=2.0),
            make_unit("Buhangin District Hospital", "O+", distance_km=9.1),
            make_unit("Mintal Doctors Hospital", "O+", distance_km=0.8),
            make_unit("Agdao Mercy Hospital", "O+", distance_km=4.4),
        ]
        result = merge_sort(records, get_distance)
        self.assertEqual(distances(result), [0.8, 2.0, 4.4, 7.5, 9.1])
        self.assertEqual(hospital_names(result), [
            "Mintal Doctors Hospital",
            "Toril Community Hospital",
            "Agdao Mercy Hospital",
            "Bajada General Hospital",
            "Buhangin District Hospital",
        ])

    def test_stability_equal_distances_keep_original_order(self):
        """Input: Bajada 3.0, Toril 1.0, Buhangin 3.0, Mintal 3.0, Agdao 2.0.
        Expected: Toril, Agdao, then Bajada, Buhangin, Mintal - the three
        units at 3.0 km stay in their original order.
        Why: Merge Sort must be stable (merge uses "<="), so ties on distance
        keep the order they had before.
        """
        records = [
            make_unit("Bajada General Hospital", "O+", distance_km=3.0),
            make_unit("Toril Community Hospital", "O+", distance_km=1.0),
            make_unit("Buhangin District Hospital", "O+", distance_km=3.0),
            make_unit("Mintal Doctors Hospital", "O+", distance_km=3.0),
            make_unit("Agdao Mercy Hospital", "O+", distance_km=2.0),
        ]
        result = merge_sort(records, get_distance)
        self.assertEqual(hospital_names(result), [
            "Toril Community Hospital",
            "Agdao Mercy Hospital",
            "Bajada General Hospital",
            "Buhangin District Hospital",
            "Mintal Doctors Hospital",
        ])

    def test_input_list_is_not_modified(self):
        """Input: three units with distances 5.0, 1.0, 3.0.
        Expected: after the call the input list still reads 5.0, 1.0, 3.0,
        while the returned list reads 1.0, 3.0, 5.0.
        Why: the functions are pure; the caller's list must not change.
        """
        records = [
            make_unit("Bajada General Hospital", "O+", distance_km=5.0),
            make_unit("Toril Community Hospital", "O+", distance_km=1.0),
            make_unit("Buhangin District Hospital", "O+", distance_km=3.0),
        ]
        result = merge_sort(records, get_distance)
        self.assertEqual(distances(records), [5.0, 1.0, 3.0])
        self.assertEqual(distances(result), [1.0, 3.0, 5.0])


class TestMerge(unittest.TestCase):
    """Tests for merge(left, right, key)."""

    def test_merge_two_ordered_lists(self):
        """Input: left with distances 1.0, 4.0 and right with 2.0, 3.0, 5.0.
        Expected: 1.0, 2.0, 3.0, 4.0, 5.0.
        Why: merge is the step that does the real work of Merge Sort.
        """
        left = [
            make_unit("Bajada General Hospital", "O+", distance_km=1.0),
            make_unit("Toril Community Hospital", "O+", distance_km=4.0),
        ]
        right = [
            make_unit("Buhangin District Hospital", "O+", distance_km=2.0),
            make_unit("Mintal Doctors Hospital", "O+", distance_km=3.0),
            make_unit("Agdao Mercy Hospital", "O+", distance_km=5.0),
        ]
        result = merge(left, right, get_distance)
        self.assertEqual(distances(result), [1.0, 2.0, 3.0, 4.0, 5.0])

    def test_merge_with_empty_left(self):
        """Input: an empty left list and a right list with 2.0, 3.0.
        Expected: 2.0, 3.0.
        Why: when one side has nothing, the rest of the other side is copied.
        """
        right = [
            make_unit("Buhangin District Hospital", "O+", distance_km=2.0),
            make_unit("Mintal Doctors Hospital", "O+", distance_km=3.0),
        ]
        result = merge([], right, get_distance)
        self.assertEqual(distances(result), [2.0, 3.0])

    def test_merge_with_empty_right(self):
        """Input: a left list with 1.0, 4.0 and an empty right list.
        Expected: 1.0, 4.0.
        Why: same as above for the other side.
        """
        left = [
            make_unit("Bajada General Hospital", "O+", distance_km=1.0),
            make_unit("Toril Community Hospital", "O+", distance_km=4.0),
        ]
        result = merge(left, [], get_distance)
        self.assertEqual(distances(result), [1.0, 4.0])

    def test_merge_tie_takes_left_item_first(self):
        """Input: left has Bajada at 2.0; right has Toril at 2.0.
        Expected: Bajada, then Toril.
        Why: on a tie the left item must be taken first ("<="). This is
        the one comparison that makes the whole sort stable.
        """
        left = [make_unit("Bajada General Hospital", "O+", distance_km=2.0)]
        right = [make_unit("Toril Community Hospital", "O+", distance_km=2.0)]
        result = merge(left, right, get_distance)
        self.assertEqual(hospital_names(result),
                         ["Bajada General Hospital", "Toril Community Hospital"])


class TestFindFirstAndFindLast(unittest.TestCase):
    """Tests for find_first and find_last on a registry ordered by blood type.

    Registry positions: 0 A+, 1 A-, 2 A-, 3 B+, 4 O+, 5 O+, 6 O+, 7 O-.
    """

    def setUp(self):
        """Build the same 8-record registry before every test."""
        self.registry = make_search_registry()

    def test_registry_is_in_the_documented_order(self):
        """Input: the 8-record registry built by make_search_registry.
        Expected: A+, A-, A-, B+, O+, O+, O+, O-.
        Why: every other test in this class relies on these positions.
        """
        self.assertEqual(blood_types(self.registry),
                         ["A+", "A-", "A-", "B+", "O+", "O+", "O+", "O-"])

    def test_run_of_duplicates(self):
        """Input: target "O+", which sits at positions 4, 5 and 6.
        Expected: find_first gives 4 and find_last gives 6.
        Why: several hospitals hold the same type; both ends of the block
        are needed to copy all of them.
        """
        self.assertEqual(find_first(self.registry, "O+"), 4)
        self.assertEqual(find_last(self.registry, "O+"), 6)

    def test_type_that_occurs_once(self):
        """Input: target "B+", which sits only at position 3.
        Expected: find_first gives 3 and find_last gives 3.
        Why: with a single match the first and the last position are equal.
        """
        self.assertEqual(find_first(self.registry, "B+"), 3)
        self.assertEqual(find_last(self.registry, "B+"), 3)

    def test_type_at_the_very_start(self):
        """Input: target "A+", the first record of the registry.
        Expected: find_first gives 0 and find_last gives 0.
        Why: checks the left edge, where low and high meet at position 0.
        """
        self.assertEqual(find_first(self.registry, "A+"), 0)
        self.assertEqual(find_last(self.registry, "A+"), 0)

    def test_type_at_the_very_end(self):
        """Input: target "O-", the last record of the registry.
        Expected: find_first gives 7 and find_last gives 7.
        Why: checks the right edge, the last valid position.
        """
        self.assertEqual(find_first(self.registry, "O-"), 7)
        self.assertEqual(find_last(self.registry, "O-"), 7)

    def test_missing_type_gives_minus_one(self):
        """Input: target "AB+", which is not in the registry.
        Expected: find_first gives -1 and find_last gives -1.
        Why: -1 is how the caller knows no hospital holds that type.
        """
        self.assertEqual(find_first(self.registry, "AB+"), -1)
        self.assertEqual(find_last(self.registry, "AB+"), -1)

    def test_empty_registry_gives_minus_one(self):
        """Input: an empty registry and target "O+".
        Expected: find_first gives -1 and find_last gives -1.
        Why: the while loop must not run at all, and nothing may crash.
        """
        self.assertEqual(find_first([], "O+"), -1)
        self.assertEqual(find_last([], "O+"), -1)


class TestFindCompatibleUnits(unittest.TestCase):
    """Tests for find_compatible_units(registry, patient_type)."""

    def test_many_matches_for_o_positive_patient(self):
        """Input: patient "O+"; registry with O+ at 6.0, 0.9 and 4.1 km,
        O- at 2.5 and 8.2 km, plus one A+ and one B+ unit.
        Expected: only the five O+ and O- units, at 0.9, 2.5, 4.1, 6.0, 8.2.
        Why: this is the normal case - only safe donor types, nearest first.
        """
        records = [
            make_unit("Bajada General Hospital", "O+", distance_km=6.0),
            make_unit("Toril Community Hospital", "O-", distance_km=2.5),
            make_unit("Buhangin District Hospital", "A+", distance_km=1.0),
            make_unit("Mintal Doctors Hospital", "O+", distance_km=0.9),
            make_unit("Agdao Mercy Hospital", "O-", distance_km=8.2),
            make_unit("Sasa Wharfside Hospital", "B+", distance_km=3.0),
            make_unit("Lanang Bayview Medical Center", "O+", distance_km=4.1),
        ]
        registry = merge_sort(records, get_blood_type)
        matches = find_compatible_units(registry, "O+")
        self.assertEqual(hospital_names(matches), [
            "Mintal Doctors Hospital",
            "Toril Community Hospital",
            "Lanang Bayview Medical Center",
            "Bajada General Hospital",
            "Agdao Mercy Hospital",
        ])
        self.assertEqual(blood_types(matches), ["O+", "O-", "O+", "O+", "O-"])
        self.assertEqual(distances(matches), [0.9, 2.5, 4.1, 6.0, 8.2])

    def test_one_match(self):
        """Input: patient "O-"; registry with one O- unit, one A+ and one B+.
        Expected: a list with only the O- unit.
        Why: an O- patient can only receive O-, so a single match must
        still come back as a list of one record.
        """
        records = [
            make_unit("Bajada General Hospital", "A+", distance_km=1.0),
            make_unit("Toril Community Hospital", "O-", distance_km=7.0),
            make_unit("Buhangin District Hospital", "B+", distance_km=2.0),
        ]
        registry = merge_sort(records, get_blood_type)
        matches = find_compatible_units(registry, "O-")
        self.assertEqual(len(matches), 1)
        self.assertEqual(hospital_names(matches), ["Toril Community Hospital"])

    def test_no_compatible_units_gives_empty_list(self):
        """Input: patient "O-"; registry with only A+ and B+ units.
        Expected: an empty list.
        Why: the caller turns an empty list into the message
        "No compatible units available.".
        """
        records = [
            make_unit("Bajada General Hospital", "A+", distance_km=1.0),
            make_unit("Buhangin District Hospital", "B+", distance_km=2.0),
        ]
        registry = merge_sort(records, get_blood_type)
        self.assertEqual(find_compatible_units(registry, "O-"), [])

    def test_empty_registry_gives_empty_list(self):
        """Input: patient "AB+" (accepts every type) and an empty registry.
        Expected: an empty list.
        Why: all eight searches return -1 and nothing may crash.
        """
        self.assertEqual(find_compatible_units([], "AB+"), [])

    def test_equal_distance_o_positive_before_o_negative(self):
        """Input: patient "O+"; an O- unit and an O+ unit, both at 3.0 km,
        with the O- unit written first in the input.
        Expected: the O+ unit first, then the O- unit.
        Why: ties on distance keep compatibility-table order, and the table
        for "O+" lists O+ before O-.
        """
        records = [
            make_unit("Toril Community Hospital", "O-", distance_km=3.0),
            make_unit("Bajada General Hospital", "O+", distance_km=3.0),
        ]
        registry = merge_sort(records, get_blood_type)
        matches = find_compatible_units(registry, "O+")
        self.assertEqual(hospital_names(matches),
                         ["Bajada General Hospital", "Toril Community Hospital"])
        self.assertEqual(blood_types(matches), ["O+", "O-"])

    def test_equal_distance_follows_table_order_not_registry_order(self):
        """Input: patient "AB+"; an A+ unit and an AB+ unit, both at 3.0 km.
        In the registry A+ comes before AB+.
        Expected: the AB+ unit first, then the A+ unit.
        Why: the table for "AB+" lists AB+ before A+, so this proves ties
        follow the compatibility table and not the registry order.
        """
        records = [
            make_unit("Bajada General Hospital", "A+", distance_km=3.0),
            make_unit("Toril Community Hospital", "AB+", distance_km=3.0),
        ]
        registry = merge_sort(records, get_blood_type)
        self.assertEqual(blood_types(registry), ["A+", "AB+"])
        matches = find_compatible_units(registry, "AB+")
        self.assertEqual(blood_types(matches), ["AB+", "A+"])
        self.assertEqual(hospital_names(matches),
                         ["Toril Community Hospital", "Bajada General Hospital"])


class TestTrace(unittest.TestCase):
    """Tests for the optional trace list. It may record, never change."""

    def make_records(self):
        """Return four units with distances 4.0, 1.0, 3.0, 2.0."""
        return [
            make_unit("Bajada General Hospital", "O+", distance_km=4.0),
            make_unit("Toril Community Hospital", "A-", distance_km=1.0),
            make_unit("Buhangin District Hospital", "B+", distance_km=3.0),
            make_unit("Mintal Doctors Hospital", "O+", distance_km=2.0),
        ]

    def test_merge_sort_trace_does_not_change_result(self):
        """Input: four units (4.0, 1.0, 3.0, 2.0), once without a trace and
        once with trace=[].
        Expected: both calls return 1.0, 2.0, 3.0, 4.0 and the trace list
        is not empty.
        Why: the trace is only for showing steps on screen; the answer must
        be the same with or without it.
        """
        plain = merge_sort(self.make_records(), get_distance)
        trace = []
        traced = merge_sort(self.make_records(), get_distance, trace)
        self.assertEqual(distances(plain), [1.0, 2.0, 3.0, 4.0])
        self.assertEqual(traced, plain)
        self.assertTrue(len(trace) > 0)

    def test_merge_trace_steps_have_expected_keys(self):
        """Input: merge_sort on four units with trace=[].
        Expected: every step has the keys left, right, i, j, took, result.
        Why: the Trace tab of the GUI reads exactly these keys.
        """
        trace = []
        merge_sort(self.make_records(), get_distance, trace)
        for step in trace:
            for name in ["left", "right", "i", "j", "took", "result"]:
                self.assertIn(name, step)

    def test_find_first_trace_does_not_change_result(self):
        """Input: the 8-record registry and target "O+", with and without
        trace=[].
        Expected: both calls return 4 and the trace list is not empty.
        Why: recording the steps must not move low, mid or high.
        """
        registry = make_search_registry()
        trace = []
        self.assertEqual(find_first(registry, "O+"), 4)
        self.assertEqual(find_first(registry, "O+", trace), 4)
        self.assertTrue(len(trace) > 0)

    def test_find_last_trace_does_not_change_result(self):
        """Input: the 8-record registry and target "O+", with and without
        trace=[].
        Expected: both calls return 6 and the trace list is not empty.
        Why: same rule as find_first - the trace only records.
        """
        registry = make_search_registry()
        trace = []
        self.assertEqual(find_last(registry, "O+"), 6)
        self.assertEqual(find_last(registry, "O+", trace), 6)
        self.assertTrue(len(trace) > 0)

    def test_missing_type_trace_still_gives_minus_one(self):
        """Input: the 8-record registry and missing target "AB+", trace=[].
        Expected: find_first and find_last both return -1, and both trace
        lists are not empty.
        Why: the Trace tab must be able to show a not-found search too.
        """
        registry = make_search_registry()
        first_trace = []
        last_trace = []
        self.assertEqual(find_first(registry, "AB+", first_trace), -1)
        self.assertEqual(find_last(registry, "AB+", last_trace), -1)
        self.assertTrue(len(first_trace) > 0)
        self.assertTrue(len(last_trace) > 0)

    def test_binary_search_trace_steps_have_expected_keys(self):
        """Input: find_first and find_last for "O+" on the 8-record registry,
        each with its own trace list.
        Expected: every step has the keys low, mid, high, value, target.
        Why: these are the values the student shows in the trace table.
        """
        registry = make_search_registry()
        first_trace = []
        last_trace = []
        find_first(registry, "O+", first_trace)
        find_last(registry, "O+", last_trace)
        for step in first_trace + last_trace:
            for name in ["low", "mid", "high", "value", "target"]:
                self.assertIn(name, step)

    def test_find_first_trace_matches_hand_trace(self):
        """Input: find_first for "O+" on the 8-record registry, trace=[].
        Expected: three steps, worked out by hand:
            low 0, mid 3, high 7, value B+  (too small, go right)
            low 4, mid 5, high 7, value O+  (match, keep looking left)
            low 4, mid 4, high 4, value O+  (match, answer is 4)
        Why: the recorded steps must be the real steps of the algorithm,
        because the student reads them out in the video.
        """
        registry = make_search_registry()
        trace = []
        find_first(registry, "O+", trace)
        expected = [
            {"low": 0, "mid": 3, "high": 7, "value": "B+", "target": "O+"},
            {"low": 4, "mid": 5, "high": 7, "value": "O+", "target": "O+"},
            {"low": 4, "mid": 4, "high": 4, "value": "O+", "target": "O+"},
        ]
        self.assertEqual(trace, expected)


if __name__ == "__main__":
    unittest.main()
