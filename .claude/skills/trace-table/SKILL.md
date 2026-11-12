---
name: trace-table
description: Generate a Markdown tracing table from the real trace output of merge_sort or find_first/find_last for a given sample.
---
1. Load the 6-record sample from data/hospitals.csv (first 6 usable rows).
2. Call the function with trace=[] and collect the steps.
3. Format as a Markdown table (columns defined by the trace-generator agent).
4. Append to docs/tracing.md with a one-line explanation per step.
