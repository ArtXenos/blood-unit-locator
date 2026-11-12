"""Data model for the Emergency Blood Unit Locator.

This file holds the BloodUnit record, the blood compatibility table,
the three messages shown to the user, and two small helper functions
that Merge Sort uses as its "key".
"""

from dataclasses import dataclass
from datetime import date


@dataclass
class BloodUnit:
    """One line of blood stock reported by one hospital."""

    hospital: str
    blood_type: str
    units: int
    distance_km: float
    expiry_date: date


# Patient blood type -> donor blood types that patient can safely receive.
# The order of each list is copied from the approved compatibility table.
# It matters: when two hospitals are at the same distance, the stable sort
# keeps them in this order.
COMPATIBLE = {
    "O-": ["O-"],
    "O+": ["O+", "O-"],
    "A-": ["A-", "O-"],
    "A+": ["A+", "A-", "O+", "O-"],
    "B-": ["B-", "O-"],
    "B+": ["B+", "B-", "O+", "O-"],
    "AB-": ["AB-", "A-", "B-", "O-"],
    "AB+": ["AB+", "AB-", "A+", "A-", "B+", "B-", "O+", "O-"],
}

# The exact messages from the pseudocode. They are kept in one place so the
# GUI and the tests always use the same text.
MSG_NO_RECORDS = "No hospital records loaded."
MSG_INVALID_TYPE = "Invalid blood type."
MSG_NO_UNITS = "No compatible units available."


def get_blood_type(unit):
    """Return the blood type of a unit. Used as the key to order the registry."""
    return unit.blood_type


def get_distance(unit):
    """Return the distance of a unit in km. Used as the key to put the nearest first."""
    return unit.distance_km
