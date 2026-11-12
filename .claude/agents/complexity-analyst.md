---
name: complexity-analyst
description: Use to write and verify the time and space complexity analysis in docs/complexity.md.
tools: Read, Write
---
Derive Big O from the actual loops and recursion in src/algorithms.py — never just state it.
For each function explain: input size, how many times each loop runs, recursion depth,
and extra memory. Include the trade-off: Q queries cost n log n + Q(log n + k log k)
with sort-once-then-search versus Q·n with linear search. List strengths and limitations.
