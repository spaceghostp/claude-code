---
name: Codebase Metrics
description: This skill should be used when the user asks to "show codebase metrics", "count lines of code", "measure complexity", "show LOC", "codebase stats", "how big is the codebase", or "run scc".
version: 0.1.0
---

# Codebase Metrics

Run `scc` to produce codebase metrics including lines of code,
complexity estimates, and COCOMO projections.

## Instructions

1. **Check scc is installed:**
   ```bash
   command -v scc
   ```
   If missing, report that scc is not installed and suggest:
   `brew install scc` (macOS) or `go install github.com/boyter/scc/v3@latest`

2. **Run scc with default table output** (human-readable):
   ```bash
   scc .
   ```

3. **Present results** including:
   - Language breakdown (files, lines, code, comments, blanks)
   - Total lines of code
   - Complexity estimates
   - COCOMO estimates (effort, cost, schedule)

4. **If programmatic analysis is needed**, run with JSON output:
   ```bash
   scc --format json .
   ```

## Notes

- scc is fast (~sub-second for most codebases)
- Default output excludes `.git`, `node_modules`, `vendor` dirs
- Use `--exclude-dir` for additional exclusions if needed
