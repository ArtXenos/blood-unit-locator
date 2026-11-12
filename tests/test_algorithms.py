"""Tests for the six hand-written functions in src/algorithms.py.

Every test uses a fixed "today" date and small lists made in memory, so the
result never depends on the real clock or on a file. Expected values were
worked out by hand and are written as plain lists.

Each test docstring states the Input, the Expected output and Why it matters.
"""

import os
import tempfile
import unittest
from datetime import date

from src.models import (
    BloodUnit,
    MSG_INVALID_TYPE,
    MSG_NO_RECORDS,
    MSG_NO_UNITS,
    get_blood_type,
    get_distance,
)
from src.algorithms import (
    filter_usable,
    merge_sort,
    merge,
    find_first,
    find_last,
    find_compatible_units,
)
from src.locator import prepare_registry, search_patient
from src.data_loader import load_records, parse_row

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


# A date before TODAY, used for records that are already expired.
EXPIRED = date(2025, 1, 15)

# The first line every hospital CSV file must have.
CSV_HEADER = "hospital,blood_type,units,distance_km,expiry_date"


class TestLocator(unittest.TestCase):
    """Tests for prepare_registry and search_patient in src/locator.py.

    Tests 1 to 6 are the six required test cases of the project. Each one
    goes through the whole pipeline: filter, order by blood type, search,
    order by distance.
    """

    def test_1_many_matches_o_positive_patient(self):
        """Input: patient "O+"; nine records in no particular order:
        O+ at 6.0, 0.9 and 4.1 km, O- at 2.5 and 8.2 km, one A+, one B+,
        one O+ with 0 units (0.5 km) and one expired O- (0.3 km).
        Expected: Mintal 0.9, Toril 2.5, Lanang 4.1, Bajada 6.0, Agdao 8.2
        and an empty message.
        Why: the normal case - only safe and usable donor units, nearest
        hospital first. The two unusable units are the nearest of all, so
        the test fails if the filter is skipped.
        """
        records = [
            make_unit("Bajada General Hospital", "O+", distance_km=6.0),
            make_unit("Toril Community Hospital", "O-", distance_km=2.5),
            make_unit("Buhangin District Hospital", "A+", distance_km=1.0),
            make_unit("Mintal Doctors Hospital", "O+", distance_km=0.9),
            make_unit("Panacan Family Hospital", "O+", units=0, distance_km=0.5),
            make_unit("Agdao Mercy Hospital", "O-", distance_km=8.2),
            make_unit("Sasa Wharfside Hospital", "B+", distance_km=3.0),
            make_unit("Bangkal Hillside Hospital", "O-", distance_km=0.3,
                      expiry_date=EXPIRED),
            make_unit("Lanang Bayview Medical Center", "O+", distance_km=4.1),
        ]
        registry, message = prepare_registry(records, TODAY)
        self.assertEqual(message, "")
        results, message = search_patient(registry, "O+")
        self.assertEqual(message, "")
        self.assertEqual(hospital_names(results), [
            "Mintal Doctors Hospital",
            "Toril Community Hospital",
            "Lanang Bayview Medical Center",
            "Bajada General Hospital",
            "Agdao Mercy Hospital",
        ])
        self.assertEqual(blood_types(results), ["O+", "O-", "O+", "O+", "O-"])
        self.assertEqual(distances(results), [0.9, 2.5, 4.1, 6.0, 8.2])

    def test_2_one_match(self):
        """Input: patient "O-"; records: A+ at 1.0 km, O- at 7.0 km, B+ at
        2.0 km and one O- with 0 units at 0.5 km.
        Expected: a list with only Toril Community Hospital (O-, 7.0 km)
        and an empty message.
        Why: an O- patient can only receive O-, so exactly one usable
        record must come back as a list of one.
        """
        records = [
            make_unit("Bajada General Hospital", "A+", distance_km=1.0),
            make_unit("Toril Community Hospital", "O-", distance_km=7.0),
            make_unit("Buhangin District Hospital", "B+", distance_km=2.0),
            make_unit("Mintal Doctors Hospital", "O-", units=0, distance_km=0.5),
        ]
        registry, message = prepare_registry(records, TODAY)
        results, message = search_patient(registry, "O-")
        self.assertEqual(message, "")
        self.assertEqual(len(results), 1)
        self.assertEqual(hospital_names(results), ["Toril Community Hospital"])
        self.assertEqual(blood_types(results), ["O-"])

    def test_3_edge_all_o_negative_units_unusable(self):
        """Input: patient "O-"; three O- records that are all unusable
        (0 units, expired on 2025-01-15, expiring exactly today) plus a
        usable A+ and a usable O+ record.
        Expected: results [] and the message "No compatible units available."
        Why: edge case - the blood type exists in the file, but none of it
        can be used. The other types must not be offered to an O- patient.
        """
        records = [
            make_unit("Bajada General Hospital", "O-", units=0),
            make_unit("Buhangin District Hospital", "A+", distance_km=2.0),
            make_unit("Toril Community Hospital", "O-", expiry_date=EXPIRED),
            make_unit("Agdao Mercy Hospital", "O+", distance_km=3.0),
            make_unit("Mintal Doctors Hospital", "O-", expiry_date=TODAY),
        ]
        registry, message = prepare_registry(records, TODAY)
        self.assertEqual(message, "")
        results, message = search_patient(registry, "O-")
        self.assertEqual(results, [])
        self.assertEqual(message, "No compatible units available.")

    def test_4_edge_empty_dataset(self):
        """Input: an empty list of records.
        Expected: registry [] and the message "No hospital records loaded."
        Why: edge case - the program must say clearly that nothing was
        loaded instead of crashing.
        """
        registry, message = prepare_registry([], TODAY)
        self.assertEqual(registry, [])
        self.assertEqual(message, "No hospital records loaded.")

    def test_5_edge_invalid_blood_type(self):
        """Input: patient types "C+", "" and "o+" on a registry that has
        usable O+ and A+ units.
        Expected: results [] and the message "Invalid blood type." for all
        three.
        Why: edge case - a type that is not in the compatibility table must
        be refused before any search. Lower case "o+" is not in the table.
        """
        records = [
            make_unit("Bajada General Hospital", "O+", distance_km=1.0),
            make_unit("Toril Community Hospital", "A+", distance_km=2.0),
        ]
        registry, message = prepare_registry(records, TODAY)
        for patient_type in ["C+", "", "o+"]:
            results, message = search_patient(registry, patient_type)
            self.assertEqual(results, [])
            self.assertEqual(message, "Invalid blood type.")

    def test_6_stability_equal_distances_keep_order(self):
        """Input: patient "O+"; records in this order: Toril O- 3.0,
        Bajada O+ 3.0, Mintal O+ 3.0, Agdao O+ 1.0, Buhangin O- 3.0.
        Expected: Agdao (1.0) first, then the four units at 3.0 km as
        Bajada, Mintal (O+ in input order), Toril, Buhangin (O- in input
        order).
        Why: Merge Sort is stable, so units at the same distance keep the
        compatibility-table order (O+ before O-) and, inside one type, the
        order they had in the file.
        """
        records = [
            make_unit("Toril Community Hospital", "O-", distance_km=3.0),
            make_unit("Bajada General Hospital", "O+", distance_km=3.0),
            make_unit("Mintal Doctors Hospital", "O+", distance_km=3.0),
            make_unit("Agdao Mercy Hospital", "O+", distance_km=1.0),
            make_unit("Buhangin District Hospital", "O-", distance_km=3.0),
        ]
        registry, message = prepare_registry(records, TODAY)
        results, message = search_patient(registry, "O+")
        self.assertEqual(message, "")
        self.assertEqual(hospital_names(results), [
            "Agdao Mercy Hospital",
            "Bajada General Hospital",
            "Mintal Doctors Hospital",
            "Toril Community Hospital",
            "Buhangin District Hospital",
        ])
        self.assertEqual(distances(results), [1.0, 3.0, 3.0, 3.0, 3.0])

    def test_prepare_registry_orders_by_blood_type_and_removes_unusable(self):
        """Input: usable O+, A- and A+ records, one B+ with 0 units and one
        expired O-.
        Expected: a registry of three records with types A+, A-, O+ and an
        empty message.
        Why: the registry must be clean and in blood type order, because
        Binary Search only works on an ordered list.
        """
        records = [
            make_unit("Bajada General Hospital", "O+"),
            make_unit("Toril Community Hospital", "A-"),
            make_unit("Buhangin District Hospital", "B+", units=0),
            make_unit("Mintal Doctors Hospital", "O-", expiry_date=EXPIRED),
            make_unit("Agdao Mercy Hospital", "A+"),
        ]
        registry, message = prepare_registry(records, TODAY)
        self.assertEqual(message, "")
        self.assertEqual(blood_types(registry), ["A+", "A-", "O+"])
        self.assertEqual(hospital_names(registry), [
            "Agdao Mercy Hospital",
            "Toril Community Hospital",
            "Bajada General Hospital",
        ])

    def test_prepare_registry_drops_unit_expiring_today(self):
        """Input: one O+ unit expiring exactly on TODAY and one O+ unit
        expiring the day after.
        Expected: the registry holds only the unit expiring the day after.
        Why: expiry is strict, and the rule must also hold in the full
        pipeline, not only in filter_usable.
        """
        records = [
            make_unit("Bajada General Hospital", "O+", expiry_date=TODAY),
            make_unit("Toril Community Hospital", "O+",
                      expiry_date=date(2026, 11, 2)),
        ]
        registry, message = prepare_registry(records, TODAY)
        self.assertEqual(hospital_names(registry), ["Toril Community Hospital"])

    def test_message_constants_have_the_exact_texts(self):
        """Input: the three message constants from src/models.py.
        Expected: "No hospital records loaded.", "Invalid blood type." and
        "No compatible units available.", letter for letter.
        Why: the pseudocode fixes these texts, and the GUI shows them.
        """
        self.assertEqual(MSG_NO_RECORDS, "No hospital records loaded.")
        self.assertEqual(MSG_INVALID_TYPE, "Invalid blood type.")
        self.assertEqual(MSG_NO_UNITS, "No compatible units available.")


def make_row(hospital="Bajada General Hospital", blood_type="O+", units="6",
             distance_km="1.9", expiry_date="2027-04-08"):
    """Build one CSV row as a dictionary of texts. The defaults are a good row."""
    return {
        "hospital": hospital,
        "blood_type": blood_type,
        "units": units,
        "distance_km": distance_km,
        "expiry_date": expiry_date,
    }


def write_csv(folder, lines):
    """Write the given lines into a CSV file inside folder and return its path."""
    csv_path = os.path.join(folder, "test_hospitals.csv")
    with open(csv_path, "w", newline="", encoding="utf-8") as csv_file:
        for line in lines:
            csv_file.write(line + "\n")
    return csv_path


class TestDataLoader(unittest.TestCase):
    """Tests for parse_row and load_records in src/data_loader.py."""

    def check_bad_row(self, row):
        """Check that parse_row refuses the row and says why."""
        unit, problem = parse_row(row)
        self.assertIsNone(unit)
        self.assertIsInstance(problem, str)
        self.assertNotEqual(problem, "")

    def test_parse_row_good_row(self):
        """Input: the row Bajada General Hospital, O+, "6", "1.9", "2027-04-08".
        Expected: a BloodUnit with units 6 (int), distance 1.9 (float),
        expiry date(2027, 4, 8), and an empty problem text.
        Why: the CSV file gives only text; the numbers and the date must be
        converted so they can be compared.
        """
        unit, problem = parse_row(make_row())
        self.assertEqual(problem, "")
        self.assertEqual(unit.hospital, "Bajada General Hospital")
        self.assertEqual(unit.blood_type, "O+")
        self.assertEqual(unit.units, 6)
        self.assertIsInstance(unit.units, int)
        self.assertEqual(unit.distance_km, 1.9)
        self.assertIsInstance(unit.distance_km, float)
        self.assertEqual(unit.expiry_date, date(2027, 4, 8))
        self.assertIsInstance(unit.expiry_date, date)

    def test_parse_row_trims_and_upper_cases_blood_type(self):
        """Input: a row with blood type " o+ ".
        Expected: a BloodUnit with blood type "O+".
        Why: small typing differences in the file must not hide a unit
        from the search, which compares exact strings.
        """
        unit, problem = parse_row(make_row(blood_type=" o+ "))
        self.assertEqual(problem, "")
        self.assertEqual(unit.blood_type, "O+")

    def test_parse_row_zero_units_is_valid(self):
        """Input: a row with units "0".
        Expected: a BloodUnit with units 0 and an empty problem text.
        Why: 0 units is real data, not a mistake. It is removed later by
        filter_usable, not by the loader.
        """
        unit, problem = parse_row(make_row(units="0"))
        self.assertEqual(problem, "")
        self.assertEqual(unit.units, 0)

    def test_parse_row_missing_field(self):
        """Input: a row that has no "units" value at all.
        Expected: unit is None and the problem text is not empty.
        Why: a short line in the file must be skipped, not crash the program.
        """
        row = make_row()
        del row["units"]
        self.check_bad_row(row)
        self.check_bad_row(make_row(units=None))

    def test_parse_row_blank_field(self):
        """Input: a row whose hospital name is only spaces.
        Expected: unit is None and the problem text is not empty.
        Why: a record without a hospital name is useless to the user.
        """
        self.check_bad_row(make_row(hospital="   "))

    def test_parse_row_non_numeric_units(self):
        """Input: a row with units "abc".
        Expected: unit is None and the problem text is not empty.
        Why: text where a number should be must not crash the loader.
        """
        self.check_bad_row(make_row(units="abc"))

    def test_parse_row_negative_units(self):
        """Input: a row with units "-3".
        Expected: unit is None and the problem text is not empty.
        Why: a hospital cannot hold a negative number of bags.
        """
        self.check_bad_row(make_row(units="-3"))

    def test_parse_row_non_numeric_distance(self):
        """Input: a row with distance "far".
        Expected: unit is None and the problem text is not empty.
        Why: the distance is the key of the final ordering, so it must be
        a number.
        """
        self.check_bad_row(make_row(distance_km="far"))

    def test_parse_row_negative_distance(self):
        """Input: a row with distance "-2.5".
        Expected: unit is None and the problem text is not empty.
        Why: a negative distance would wrongly appear as the nearest hospital.
        """
        self.check_bad_row(make_row(distance_km="-2.5"))

    def test_parse_row_nan_distance(self):
        """Input: a row with distance "nan".
        Expected: unit is None and the problem text is not empty.
        Why: Python reads "nan" as a number, but it cannot be compared, so
        it would break the ordering by distance.
        """
        self.check_bad_row(make_row(distance_km="nan"))

    def test_parse_row_inf_distance(self):
        """Input: a row with distance "inf".
        Expected: unit is None and the problem text is not empty.
        Why: Python reads "inf" as a number, but no hospital is infinitely
        far away.
        """
        self.check_bad_row(make_row(distance_km="inf"))

    def test_parse_row_impossible_date(self):
        """Input: a row with expiry date "2027-02-30".
        Expected: unit is None and the problem text is not empty.
        Why: February 30 does not exist, so the expiry check cannot be trusted.
        """
        self.check_bad_row(make_row(expiry_date="2027-02-30"))

    def test_parse_row_wrong_date_format(self):
        """Input: a row with expiry date "15/03/2027".
        Expected: unit is None and the problem text is not empty.
        Why: only the YYYY-MM-DD format is accepted, so day and month can
        never be mixed up.
        """
        self.check_bad_row(make_row(expiry_date="15/03/2027"))

    def test_parse_row_unknown_blood_type(self):
        """Input: a row with blood type "C+".
        Expected: unit is None and the problem text is not empty.
        Why: a type outside the eight real ones could never be matched.
        """
        self.check_bad_row(make_row(blood_type="C+"))

    def test_parse_row_too_many_values(self):
        """Input: a good row that also has extra values stored under the
        key None (this is how the csv module keeps values past the last
        column).
        Expected: unit is None and the problem text is not empty.
        Why: an extra comma shifts the values, so the row cannot be trusted
        even if the first five values look fine.
        """
        row = make_row()
        row[None] = ["extra"]
        self.check_bad_row(row)

    def test_parse_row_hospital_name_with_line_break(self):
        """Input: a row whose hospital name is "Bajada General\\nHospital".
        Expected: unit is None and the problem text is not empty.
        Why: a line break inside a name means a quote was never closed in
        the file, so several lines were glued into one value.
        """
        self.check_bad_row(make_row(hospital="Bajada General\nHospital"))

    def test_parse_row_units_must_be_plain_digits(self):
        """Input: three rows with units "+5", "1_000" and "3.5".
        Expected: each row is refused (unit is None, problem text not empty).
        Why: Python would accept "+5" and "1_000" as numbers, but in a
        hospital file they are typing mistakes; half a bag ("3.5") does not
        exist.
        """
        for units_text in ["+5", "1_000", "3.5"]:
            self.check_bad_row(make_row(units=units_text))

    def test_parse_row_units_with_spaces_is_accepted(self):
        """Input: a row with units " 7 " (spaces around the number).
        Expected: a BloodUnit with units 7 and an empty problem text.
        Why: stray spaces are harmless and must not make the stricter
        digits-only rule throw away a good row.
        """
        unit, problem = parse_row(make_row(units=" 7 "))
        self.assertEqual(problem, "")
        self.assertEqual(unit.units, 7)

    def test_load_records_skips_row_with_extra_value(self):
        """Input: a temporary CSV file with three rows; the middle row has
        one extra value after the expiry date.
        Expected: the first and third rows are kept, and skipped_rows has
        exactly one non-empty entry.
        Why: the too-many-values rule must also work when reading a real
        file, without losing the good rows around the bad one.
        """
        with tempfile.TemporaryDirectory() as folder:
            csv_path = write_csv(folder, [
                CSV_HEADER,
                "Bajada General Hospital,O+,6,1.9,2027-04-08",
                "Buhangin District Hospital,B+,7,6.8,2027-05-02,extra",
                "Toril Community Hospital,A-,4,14.5,2027-01-20",
            ])
            records, skipped_rows = load_records(csv_path)
        self.assertEqual(hospital_names(records),
                         ["Bajada General Hospital", "Toril Community Hospital"])
        self.assertEqual(len(skipped_rows), 1)
        self.assertIsInstance(skipped_rows[0], str)
        self.assertNotEqual(skipped_rows[0], "")

    def test_load_records_good_file(self):
        """Input: a temporary CSV file with the header and two good rows.
        Expected: two records, in file order, and no skipped rows.
        Why: the normal case of reading the hospital file.
        """
        with tempfile.TemporaryDirectory() as folder:
            csv_path = write_csv(folder, [
                CSV_HEADER,
                "Bajada General Hospital,O+,6,1.9,2027-04-08",
                "Toril Community Hospital,A-,4,14.5,2027-01-20",
            ])
            records, skipped_rows = load_records(csv_path)
        self.assertEqual(hospital_names(records),
                         ["Bajada General Hospital", "Toril Community Hospital"])
        self.assertEqual(blood_types(records), ["O+", "A-"])
        self.assertEqual(distances(records), [1.9, 14.5])
        self.assertEqual(skipped_rows, [])

    def test_load_records_skips_bad_rows(self):
        """Input: a temporary CSV file with two good rows and three bad rows
        (units "abc", blood type "C+", date "2027-02-30") mixed in.
        Expected: the two good records are kept, skipped_rows has three
        entries, and nothing crashes.
        Why: one bad line must never stop the rest of the file from loading.
        """
        with tempfile.TemporaryDirectory() as folder:
            csv_path = write_csv(folder, [
                CSV_HEADER,
                "Bajada General Hospital,O+,6,1.9,2027-04-08",
                "Buhangin District Hospital,B+,abc,6.8,2027-05-02",
                "Mintal Doctors Hospital,C+,9,11.3,2027-06-30",
                "Toril Community Hospital,A-,4,14.5,2027-01-20",
                "Agdao Mercy Hospital,O-,5,4.1,2027-02-30",
            ])
            records, skipped_rows = load_records(csv_path)
        self.assertEqual(hospital_names(records),
                         ["Bajada General Hospital", "Toril Community Hospital"])
        self.assertEqual(len(skipped_rows), 3)
        for text in skipped_rows:
            self.assertIsInstance(text, str)
            self.assertNotEqual(text, "")

    def test_load_records_header_only_file(self):
        """Input: a temporary CSV file with only the header line.
        Expected: ([], []).
        Why: a file with no data rows is not an error; it leads to the
        message "No hospital records loaded." later.
        """
        with tempfile.TemporaryDirectory() as folder:
            csv_path = write_csv(folder, [CSV_HEADER])
            records, skipped_rows = load_records(csv_path)
        self.assertEqual(records, [])
        self.assertEqual(skipped_rows, [])

    def test_load_records_empty_file(self):
        """Input: a temporary CSV file with nothing in it.
        Expected: ([], []).
        Why: a completely empty file must not crash the loader.
        """
        with tempfile.TemporaryDirectory() as folder:
            csv_path = write_csv(folder, [])
            records, skipped_rows = load_records(csv_path)
        self.assertEqual(records, [])
        self.assertEqual(skipped_rows, [])

    def test_load_records_missing_column(self):
        """Input: a temporary CSV file whose header has no expiry_date column.
        Expected: no records, and skipped_rows is not empty.
        Why: the wrong kind of file must be reported, not half-loaded.
        """
        with tempfile.TemporaryDirectory() as folder:
            csv_path = write_csv(folder, [
                "hospital,blood_type,units,distance_km",
                "Bajada General Hospital,O+,6,1.9",
            ])
            records, skipped_rows = load_records(csv_path)
        self.assertEqual(records, [])
        self.assertTrue(len(skipped_rows) > 0)

    def test_load_real_dataset(self):
        """Input: the project file data/hospitals.csv.
        Expected: 22 records, 0 skipped rows, at least one record with
        0 units and at least one with an expiry date before TODAY.
        Why: the real file must load cleanly and must contain the unusable
        rows that the demo needs to show the filter working.
        """
        csv_path = os.path.join("data", "hospitals.csv")
        records, skipped_rows = load_records(csv_path)
        self.assertEqual(len(records), 22)
        self.assertEqual(skipped_rows, [])
        zero_unit_count = 0
        expired_count = 0
        for record in records:
            if record.units == 0:
                zero_unit_count = zero_unit_count + 1
            if record.expiry_date < TODAY:
                expired_count = expired_count + 1
        self.assertTrue(zero_unit_count >= 1)
        self.assertTrue(expired_count >= 1)


if __name__ == "__main__":
    unittest.main()
