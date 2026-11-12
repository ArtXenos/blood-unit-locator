"""Hand-written algorithms for the Emergency Blood Unit Locator.

There are exactly six functions here, one for each block of the approved
pseudocode (see docs/pseudocode.md). They are "pure": they only work on the
lists they are given. No GUI code, no printing and no file reading.

Some functions accept an optional "trace" list. When a list is passed in,
the function writes down each step it takes so the steps can be shown on
screen. The trace never changes the answer.
"""

from src.models import COMPATIBLE, get_distance


def filter_usable(records, today):
    """Return only the records that can still be used.

    A record is usable when it has more than 0 units and its expiry date is
    after today. A unit that expires today is treated as not usable.
    """
    usable = []
    for record in records:
        # Both conditions must be true: there is blood left AND it is not expired.
        if record.units > 0 and record.expiry_date > today:
            usable.append(record)
    return usable


def merge_sort(items, key, trace=None):
    """Put a list in order using Merge Sort and return the ordered list.

    "key" is a small function that says what to compare, for example the
    blood type or the distance. The list is cut in half, each half is put in
    order the same way, and then the two halves are merged.
    """
    # A list with 0 or 1 items is already in order. This stops the recursion.
    if len(items) <= 1:
        return items
    mid = len(items) // 2
    left = merge_sort(items[:mid], key, trace)
    right = merge_sort(items[mid:], key, trace)
    return merge(left, right, key, trace)


def merge(left, right, key, trace=None):
    """Join two lists that are already in order into one ordered list.

    i points at the next item of left and j at the next item of right.
    The smaller of the two is copied to result each time.
    """
    result = []
    i = 0
    j = 0
    while i < len(left) and j < len(right):
        # "<=" (not "<") takes the left item on a tie. The left item came
        # first in the original list, so equal items keep their order (stable).
        if key(left[i]) <= key(right[j]):
            result.append(left[i])
            if trace is not None:
                trace.append({"left": left, "right": right, "i": i, "j": j,
                              "took": "left", "result": list(result)})
            i = i + 1
        else:
            result.append(right[j])
            if trace is not None:
                trace.append({"left": left, "right": right, "i": i, "j": j,
                              "took": "right", "result": list(result)})
            j = j + 1
    # One list is finished. Whatever is left in the other one is already in
    # order, so it is copied to the end without more comparing.
    result.extend(left[i:])
    result.extend(right[j:])
    if trace is not None:
        trace.append({"left": left, "right": right, "i": i, "j": j,
                      "took": "rest", "result": list(result)})
    return result


def find_first(registry, target, trace=None):
    """Return the position of the FIRST unit with the target blood type.

    The registry must already be in blood type order. Returns -1 when the
    blood type is not in the registry at all.
    """
    low = 0
    high = len(registry) - 1
    answer = -1
    while low <= high:
        mid = (low + high) // 2
        if trace is not None:
            trace.append({"low": low, "mid": mid, "high": high,
                          "value": registry[mid].blood_type, "target": target})
        if registry[mid].blood_type == target:
            # Found one, but an earlier one may exist, so remember this
            # position and keep looking in the left half.
            answer = mid
            high = mid - 1
        elif registry[mid].blood_type < target:
            # The middle is too small, so the target can only be to the right.
            low = mid + 1
        else:
            # The middle is too big, so the target can only be to the left.
            high = mid - 1
    return answer


def find_last(registry, target, trace=None):
    """Return the position of the LAST unit with the target blood type.

    Same as find_first, except that after a match it keeps looking in the
    right half. Returns -1 when the blood type is not in the registry.
    """
    low = 0
    high = len(registry) - 1
    answer = -1
    while low <= high:
        mid = (low + high) // 2
        if trace is not None:
            trace.append({"low": low, "mid": mid, "high": high,
                          "value": registry[mid].blood_type, "target": target})
        if registry[mid].blood_type == target:
            # Found one, but a later one may exist, so remember this
            # position and keep looking in the right half.
            answer = mid
            low = mid + 1
        elif registry[mid].blood_type < target:
            low = mid + 1
        else:
            high = mid - 1
    return answer


def find_compatible_units(registry, patient_type):
    """Return every unit the patient can receive, nearest hospital first.

    The registry is in blood type order, so all units of one donor type sit
    next to each other. Two binary searches give the first and last position
    of that block, and the block is copied out.
    """
    matches = []
    for donor_type in COMPATIBLE[patient_type]:
        first = find_first(registry, donor_type)
        # Only look for the last position when the donor type exists at all.
        if first != -1:
            last = find_last(registry, donor_type)
            for position in range(first, last + 1):
                matches.append(registry[position])
    # The matches are grouped by blood type. A second Merge Sort, this time
    # by distance, puts the nearest hospital at the top.
    return merge_sort(matches, get_distance)
