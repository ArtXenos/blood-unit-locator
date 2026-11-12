"""Starts the Emergency Blood Unit Locator.

Run this from the project folder with:  python main.py
"""

import tkinter as tk

from src.gui import LocatorApp


def main():
    """Create the window and keep it open until the user closes it."""
    root = tk.Tk()
    LocatorApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
