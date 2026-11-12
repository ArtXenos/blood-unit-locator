---
name: no-builtin-check
description: Scan the source code for forbidden built-in sorting or searching calls. Use before every commit and before finishing the project.
---
Run: grep -rnE "sorted\(|\.sort\(|bisect|heapq|import pandas|import numpy" src/ main.py
If anything is found, report the file and line and stop. A clean result prints nothing.
