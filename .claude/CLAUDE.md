# WS-000-03 Project Instructions

## Execution Policy

Do NOT over-plan. When a task has a clear plan or the user provides one, begin implementation immediately. Limit planning to a brief outline (< 20 lines) then start executing. Do not create more than 3 sub-tasks without explicit user confirmation. If you catch yourself reading files or spawning agents for more than 2 minutes before writing anything, stop and start building.

## Completion Honesty

Never declare a task "complete" or "done" until you have verified the output exists and is correct. After implementation, run a concrete verification step (test, file check, dry run). If a phase was skipped or partially done, explicitly state that — do not gloss over gaps. When multiple phases are involved, produce a brief status summary before claiming completion.

## Git Workflow

This project uses git heavily. After completing implementation work:
1. `git add` relevant files (specific files, not `git add .`)
2. `git commit` with a descriptive message
3. `git push` only if the user explicitly requested it

Do not commit code with known runtime errors — run a quick smoke test first (syntax check, import test, or brief execution) before staging.

## Python & Shell Conventions

- Primary languages: Python and Markdown
- This system aliases `grep` to ripgrep — use `rg` directly and do not assume GNU grep flag syntax
- When calling CLI tools, verify flag compatibility before chaining commands (e.g., `semgrep --quiet` breaks JSON output)
- For image/PDF processing: avoid lossy libraries (Pillow JPEG compression) — prefer lossless approaches (reportlab, ImageMagick with explicit lossless flags)

## Adversarial Review Protocol

When the user asks for adversarial review or validation: produce the review, present findings, and STOP for user input. Do not autonomously iterate on fixes from your own review without user confirmation. The user wants to see the critique, not watch you argue with yourself. Present the top issues ranked by severity, then wait.
