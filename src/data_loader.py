"""Reads the hospital blood stock from a CSV file.

Each good row becomes one BloodUnit. A row with a problem (a missing value,
text where a number should be, a wrong date, a negative number or an unknown
blood type) is skipped and written down, so one bad row never crashes the
program.
"""

import csv
from datetime import datetime

from src.models import COMPATIBLE, BloodUnit

# The column names the CSV file must have in its first line.
COLUMNS = ["hospital", "blood_type", "units", "distance_km", "expiry_date"]

# No two places on Earth are further apart than about 20,000 km, so a bigger
# distance must be a typing mistake.
MAX_DISTANCE_KM = 20000


def load_records(csv_path):
    """Read a CSV file and return (records, skipped_rows).

    records is the list of BloodUnit objects that were read correctly.
    skipped_rows is a list of short texts, one for each row that was left out.
    """
    records = []
    skipped_rows = []
    # "utf-8-sig" also reads files saved by Excel, which adds a hidden mark
    # at the very start of the file.
    with open(csv_path, newline="", encoding="utf-8-sig") as csv_file:
        reader = csv.DictReader(csv_file)
        # An empty file has no header line at all.
        if reader.fieldnames is None:
            return records, skipped_rows
        for column in COLUMNS:
            if column not in reader.fieldnames:
                skipped_rows.append("The file has no '" + column + "' column.")
        if len(skipped_rows) > 0:
            return records, skipped_rows
        for row in reader:
            unit, problem = parse_row(row)
            if unit is None:
                skipped_rows.append("Line " + str(reader.line_num) + ": " + problem)
            else:
                records.append(unit)
    return records, skipped_rows


def parse_row(row):
    """Turn one CSV row (a dictionary of texts) into a BloodUnit.

    Returns (unit, problem). When the row is good, problem is an empty
    string. When the row is bad, unit is None and problem says why.
    """
    # 1. Every column must have a value, and there must be no extra values.
    #    The csv module stores extra values under the key None.
    if None in row:
        return None, "too many values in this row"
    for column in COLUMNS:
        value = row.get(column)
        if value is None or value.strip() == "":
            return None, "missing " + column

    # A line break inside the name means a quote was opened and never
    # closed, so several lines of the file were glued into one value.
    hospital = row["hospital"].strip()
    if "\n" in hospital or "\r" in hospital:
        return None, "the hospital name has a line break (a quote is not closed)"

    # 2. The blood type must be one of the eight real types.
    blood_type = row["blood_type"].strip().upper()
    if blood_type not in COMPATIBLE:
        # Only the first few characters are shown so the message stays short.
        return None, "unknown blood type '" + blood_type[:10] + "'"

    # 3. Units must be a whole number that is not negative. Allowing only
    #    the digits 0-9 rejects "-3", "3.5", "+5" and "1_000" in one check.
    units_text = row["units"].strip()
    if not (units_text.isascii() and units_text.isdigit()):
        return None, "units is not a whole number (0 or more)"
    units = int(units_text)

    # 4. Distance must be a real, non-negative number. Writing the check as
    #    "not (0 <= distance <= limit)" also rejects the special values
    #    "nan" and "inf" that float() accepts.
    try:
        distance_km = float(row["distance_km"].strip())
    except ValueError:
        return None, "distance is not a number"
    if not (0 <= distance_km <= MAX_DISTANCE_KM):
        return None, "distance is negative or too large"

    # 5. The expiry date must look like 2027-03-15 and be a real date.
    try:
        expiry_date = datetime.strptime(row["expiry_date"].strip(), "%Y-%m-%d").date()
    except ValueError:
        return None, "expiry date is not a valid YYYY-MM-DD date"

    return BloodUnit(hospital, blood_type, units, distance_km, expiry_date), ""
