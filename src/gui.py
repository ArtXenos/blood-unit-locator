"""The Tkinter window of the Emergency Blood Unit Locator.

This file only shows things on screen and reads what the user picked.
All the real work (filtering, Merge Sort, Binary Search) is done by the
functions in locator.py and algorithms.py.
"""

import csv
import tkinter as tk
from datetime import date, datetime
from tkinter import filedialog, messagebox, ttk

from src.algorithms import filter_usable, find_first, find_last, merge_sort
from src.data_loader import load_records
from src.locator import prepare_registry, search_patient
from src.models import COMPATIBLE, MSG_INVALID_TYPE, MSG_NO_RECORDS, get_blood_type

# The dataset that is loaded when the program starts. The path is relative,
# so the program should be started from the project folder.
DEFAULT_CSV = "data/hospitals.csv"

# How many records the Trace tab uses. A small sample keeps the trace short
# enough to read and explain.
TRACE_SAMPLE_SIZE = 6

FICTIONAL_NOTE = "Hospital data is fictional."

TABLE_COLUMNS = ["rank", "hospital", "blood_type", "units", "distance", "expiry"]
TABLE_HEADINGS = ["#", "Hospital", "Blood type", "Units", "Distance (km)", "Expiry date"]
TABLE_WIDTHS = [40, 290, 90, 70, 110, 110]


def show_keys(units, key):
    """Return a short text such as "[A+, O-]" showing the key of each unit."""
    texts = []
    for unit in units:
        texts.append(str(key(unit)))
    return "[" + ", ".join(texts) + "]"


def format_merge_trace(trace, key):
    """Turn the steps recorded by merge_sort into lines of text."""
    lines = []
    merge_number = 0
    starting_new_merge = True
    for step in trace:
        left = step["left"]
        right = step["right"]
        i = step["i"]
        j = step["j"]
        if starting_new_merge:
            merge_number = merge_number + 1
            lines.append("")
            lines.append(f"Merge {merge_number}:  left = {show_keys(left, key)}"
                         f"   right = {show_keys(right, key)}")
            starting_new_merge = False
        if step["took"] == "left":
            action = f"{key(left[i])} <= {key(right[j])}, take from left"
        elif step["took"] == "right":
            action = f"{key(left[i])} > {key(right[j])}, take from right"
        else:
            # The "rest" step is always the last step of one merge.
            action = "one side is finished, copy the rest"
            starting_new_merge = True
        lines.append(f"   i={i}  j={j}   {action}"
                     f"   ->  result = {show_keys(step['result'], key)}")
    return lines


def format_search_trace(trace, match_action):
    """Turn the steps recorded by find_first or find_last into lines of text.

    match_action is the text to show when the middle item is a match,
    because that is the only place where the two searches differ.
    """
    lines = []
    step_number = 0
    for step in trace:
        step_number = step_number + 1
        value = step["value"]
        target = step["target"]
        if value == target:
            action = f"{value} = {target}  ->  {match_action}"
        elif value < target:
            action = f"{value} < {target}  ->  low = mid + 1 (go right)"
        else:
            action = f"{value} > {target}  ->  high = mid - 1 (go left)"
        lines.append(f"   Step {step_number}:  low={step['low']}  mid={step['mid']}"
                     f"  high={step['high']}   registry[{step['mid']}] = {value}"
                     f"   {action}")
    if step_number == 0:
        lines.append("   (no steps: the registry is empty)")
    return lines


def build_trace_lines(sample, target):
    """Build the whole text of the Trace tab for a small sample of records.

    The steps come from running the real merge_sort, find_first and
    find_last with a trace list, so the text always matches the code.
    """
    lines = []
    lines.append(f"TRACE on the first {len(sample)} usable records")
    lines.append("")
    lines.append("1) Records in the order they were reported:")
    position = 0
    for unit in sample:
        lines.append(f"   [{position}] {unit.blood_type:<4} {unit.hospital}")
        position = position + 1

    lines.append("")
    lines.append("2) MERGE SORT by blood type (each merge joins two ordered lists):")
    merge_trace = []
    registry = merge_sort(sample, get_blood_type, merge_trace)
    for line in format_merge_trace(merge_trace, get_blood_type):
        lines.append(line)
    if len(sample) < 2:
        lines.append("   (nothing to merge: fewer than 2 usable records)")

    lines.append("")
    lines.append("3) Registry after Merge Sort:")
    position = 0
    for unit in registry:
        lines.append(f"   [{position}] {unit.blood_type:<4} {unit.hospital}")
        position = position + 1

    lines.append("")
    lines.append(f"4) BINARY SEARCH - find_first(registry, \"{target}\"):")
    first_trace = []
    first = find_first(registry, target, first_trace)
    for line in format_search_trace(
            first_trace, "answer = mid, high = mid - 1 (keep looking left)"):
        lines.append(line)
    lines.append(f"   find_first returns {first}")

    lines.append("")
    if first == -1:
        lines.append(f"5) \"{target}\" is not in this sample, so find_last is not needed.")
    else:
        lines.append(f"5) BINARY SEARCH - find_last(registry, \"{target}\"):")
        last_trace = []
        last = find_last(registry, target, last_trace)
        for line in format_search_trace(
                last_trace, "answer = mid, low = mid + 1 (keep looking right)"):
            lines.append(line)
        lines.append(f"   find_last returns {last}")
        lines.append("")
        lines.append(f"   So every \"{target}\" unit is in registry[{first} .. {last}].")
    return lines


class LocatorApp:
    """The main window: a top bar, a Results tab and a Trace tab."""

    def __init__(self, root):
        """Build the window and load the default dataset."""
        self.root = root
        self.root.title("Emergency Blood Unit Locator")
        self.root.geometry("980x600")

        self.records = []
        self.skipped_rows = []
        self.csv_name = ""
        # The registry is kept between searches. registry_date remembers
        # which "today" it was built for, so it is rebuilt only when the
        # CSV file or the date changes (the registry is put in order once).
        self.registry = []
        self.registry_message = ""
        self.registry_date = None

        self.today_text = tk.StringVar(value=date.today().isoformat())
        self.patient_type = tk.StringVar(value="O+")
        self.status_text = tk.StringVar(value="")

        self.build_top_bar()
        self.build_tabs()
        self.build_status_bar()
        self.load_csv(DEFAULT_CSV)

    def build_top_bar(self):
        """Create the row with the load button, date field and blood type picker."""
        bar = ttk.Frame(self.root, padding=8)
        bar.pack(side="top", fill="x")

        ttk.Button(bar, text="Load CSV...", command=self.choose_csv).pack(side="left")

        ttk.Label(bar, text="Today (YYYY-MM-DD):").pack(side="left", padx=(16, 4))
        ttk.Entry(bar, textvariable=self.today_text, width=12).pack(side="left")

        ttk.Label(bar, text="Patient blood type:").pack(side="left", padx=(16, 4))
        # "readonly" means the user can only pick one of the eight real types.
        picker = ttk.Combobox(bar, textvariable=self.patient_type, width=6,
                              values=list(COMPATIBLE.keys()), state="readonly")
        picker.pack(side="left")

        ttk.Button(bar, text="Find units", command=self.find_units).pack(side="left", padx=16)

    def build_tabs(self):
        """Create the Results tab (a table) and the Trace tab (a text box)."""
        tabs = ttk.Notebook(self.root)
        tabs.pack(side="top", fill="both", expand=True, padx=8)

        results_tab = ttk.Frame(tabs)
        tabs.add(results_tab, text="Results")
        self.table = ttk.Treeview(results_tab, columns=TABLE_COLUMNS, show="headings")
        for index in range(len(TABLE_COLUMNS)):
            self.table.heading(TABLE_COLUMNS[index], text=TABLE_HEADINGS[index])
            self.table.column(TABLE_COLUMNS[index], width=TABLE_WIDTHS[index], anchor="w")
        table_scroll = ttk.Scrollbar(results_tab, orient="vertical", command=self.table.yview)
        self.table.configure(yscrollcommand=table_scroll.set)
        table_scroll.pack(side="right", fill="y")
        self.table.pack(side="left", fill="both", expand=True)

        trace_tab = ttk.Frame(tabs)
        tabs.add(trace_tab, text="Trace")
        self.trace_box = tk.Text(trace_tab, font=("Courier New", 10), wrap="none",
                                 state="disabled")
        trace_scroll_y = ttk.Scrollbar(trace_tab, orient="vertical",
                                       command=self.trace_box.yview)
        trace_scroll_x = ttk.Scrollbar(trace_tab, orient="horizontal",
                                       command=self.trace_box.xview)
        self.trace_box.configure(yscrollcommand=trace_scroll_y.set,
                                 xscrollcommand=trace_scroll_x.set)
        trace_scroll_y.pack(side="right", fill="y")
        trace_scroll_x.pack(side="bottom", fill="x")
        self.trace_box.pack(side="left", fill="both", expand=True)

    def build_status_bar(self):
        """Create the line of text at the bottom of the window."""
        status = ttk.Label(self.root, textvariable=self.status_text, padding=8,
                           anchor="w")
        status.pack(side="bottom", fill="x")

    def set_status(self, message):
        """Show a message in the status bar, plus the notes that never change."""
        text = message
        if len(self.skipped_rows) > 0:
            text = text + f"  |  {len(self.skipped_rows)} problem(s) found in the file"
        text = text + "  |  " + FICTIONAL_NOTE
        self.status_text.set(text)

    def choose_csv(self):
        """Let the user pick a CSV file, then load it."""
        csv_path = filedialog.askopenfilename(
            title="Choose a hospital CSV file",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")])
        # The path is empty when the user pressed Cancel.
        if csv_path:
            self.load_csv(csv_path)

    def load_csv(self, csv_path):
        """Read a CSV file into self.records and show how it went."""
        try:
            self.records, self.skipped_rows = load_records(csv_path)
        except UnicodeDecodeError:
            # The file is not plain text (for example an image or a
            # spreadsheet). Continue with no records instead of crashing.
            self.records = []
            self.skipped_rows = []
            messagebox.showerror(
                "Could not read the file",
                f"This is not a UTF-8 text file:\n{csv_path}\n\n"
                "Save it as \"CSV UTF-8\" and try again.")
        except (OSError, csv.Error) as error:
            # The file is missing, locked or damaged.
            self.records = []
            self.skipped_rows = []
            messagebox.showerror(
                "Could not read the file",
                f"Could not read:\n{csv_path}\n\n{error}\n\n"
                "Start the program from the project folder, "
                "or use \"Load CSV...\" to pick a file.")
        self.csv_name = csv_path
        # A new file means the old registry is out of date.
        self.registry_date = None
        self.clear_table()
        self.show_trace(["Pick a blood type and press \"Find units\" to see the trace."])

        if len(self.skipped_rows) > 0:
            self.show_skipped_rows()
        if len(self.records) == 0:
            self.set_status(MSG_NO_RECORDS)
        else:
            self.set_status(f"Loaded {len(self.records)} record(s) from {csv_path}")

    def show_skipped_rows(self):
        """Tell the user which rows of the CSV file were left out and why."""
        shown = self.skipped_rows[:10]
        text = "These parts of the file were left out:\n\n" + "\n".join(shown)
        if len(self.skipped_rows) > len(shown):
            text = text + f"\n... and {len(self.skipped_rows) - len(shown)} more"
        messagebox.showwarning("Problems in the CSV file", text)

    def read_today(self):
        """Return the date typed in the "Today" field, or None when it is not a date."""
        try:
            return datetime.strptime(self.today_text.get().strip(), "%Y-%m-%d").date()
        except ValueError:
            messagebox.showerror(
                "Invalid date",
                "Please type today's date as YYYY-MM-DD, for example 2026-11-18.")
            return None

    def find_units(self):
        """Run the search for the picked blood type and show the results."""
        today = self.read_today()
        if today is None:
            # Do not leave old results on screen next to a wrong date.
            self.clear_table()
            self.set_status("Invalid date.")
            return

        # Filter and put the registry in order only when something changed.
        if self.registry_date != today:
            self.registry, self.registry_message = prepare_registry(self.records, today)
            self.registry_date = today
        self.clear_table()
        if self.registry_message != "":
            self.set_status(self.registry_message)
            self.show_trace([self.registry_message])
            return

        patient_type = self.patient_type.get()
        results, message = search_patient(self.registry, patient_type)
        if message == MSG_INVALID_TYPE:
            self.set_status(message)
            self.show_trace([message])
            return

        self.fill_table(results)
        if message != "":
            self.set_status(message)
        else:
            donors = ", ".join(COMPATIBLE[patient_type])
            self.set_status(f"{len(results)} compatible record(s) for patient type "
                            f"{patient_type} (can receive {donors}), nearest first.")

        # The trace uses only a small sample so it stays readable.
        sample = filter_usable(self.records, today)[:TRACE_SAMPLE_SIZE]
        self.show_trace(build_trace_lines(sample, patient_type))

    def clear_table(self):
        """Remove every row from the results table."""
        for row_id in self.table.get_children():
            self.table.delete(row_id)

    def fill_table(self, results):
        """Show the result units in the table, one row each."""
        rank = 0
        for unit in results:
            rank = rank + 1
            self.table.insert("", "end", values=(
                rank, unit.hospital, unit.blood_type, unit.units,
                f"{unit.distance_km:.1f}", unit.expiry_date.isoformat()))

    def show_trace(self, lines):
        """Replace the text of the Trace tab with the given lines."""
        # The box is read-only, so it is unlocked just while it is filled.
        self.trace_box.configure(state="normal")
        self.trace_box.delete("1.0", "end")
        self.trace_box.insert("1.0", "\n".join(lines))
        self.trace_box.configure(state="disabled")
