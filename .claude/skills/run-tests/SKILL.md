---
name: run-tests
description: Run all unit tests and summarise the results as expected vs actual.
---
Run: python -m unittest discover -s tests -v
Summarise: total, passed, failed. For each failure, show the test name and the assertion message.
If any test fails, hand off to the debugger-agent.
