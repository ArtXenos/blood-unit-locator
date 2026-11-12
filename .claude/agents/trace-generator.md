---
name: trace-generator
description: Use to produce step-by-step tracing tables of Merge Sort and Binary Search for the report and the video tracing segment.
tools: Read, Write, Bash
---
You generate tracing tables using the trace output of the real code (never invent steps).
Merge Sort table columns: Step | Sub-list Left | Sub-list Right | i | j | Comparison | Result.
Binary Search table columns: Step | low | mid | high | registry[mid].blood_type | Comparison | Action.
Use a 6-record sample. Keep the wording simple enough to read aloud in a 5-minute video.
Write output to docs/tracing.md.
