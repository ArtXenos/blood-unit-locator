"""The main steps of the Blood Unit Locator (the BloodUnitLocator pseudocode).

The pseudocode block is split into two functions because the two halves run
at different times:

- prepare_registry runs ONCE each time a CSV file is loaded.
- search_patient runs every time the user asks for a blood type.

Both functions return two things: a list and a message. The message is an
empty string when everything went well. There is no GUI code here, so the
same functions are used by the window and by the unit tests.
"""

from src.algorithms import filter_usable, find_compatible_units, merge_sort
from src.models import (
    COMPATIBLE,
    MSG_INVALID_TYPE,
    MSG_NO_RECORDS,
    MSG_NO_UNITS,
    get_blood_type,
)


def prepare_registry(records, today):
    """Remove unusable records and put the rest in blood type order.

    Returns (registry, message). When no records were loaded the registry
    is empty and the message is "No hospital records loaded."
    """
    if len(records) == 0:
        return [], MSG_NO_RECORDS
    usable = filter_usable(records, today)
    # The registry is put in order ONCE here. Every later search reuses it,
    # which is what makes binary search possible.
    registry = merge_sort(usable, get_blood_type)
    return registry, ""


def search_patient(registry, patient_type):
    """Find the compatible units for one patient, nearest hospital first.

    Returns (results, message). The message is "Invalid blood type." when
    the type is not in the compatibility table, and
    "No compatible units available." when nothing usable was found.
    """
    # Check the input first, because COMPATIBLE[patient_type] would crash
    # on a blood type that does not exist.
    if patient_type not in COMPATIBLE:
        return [], MSG_INVALID_TYPE
    results = find_compatible_units(registry, patient_type)
    if len(results) == 0:
        return [], MSG_NO_UNITS
    return results, ""
