---
name: Security Scan
description: This skill should be used when the user asks to "scan for security issues", "run security checks", "check for secrets", "lint shell scripts", "audit the codebase", "run shellcheck", "run bandit", "run gitleaks", "run semgrep", or "run static analysis".
version: 0.1.0
---

# Security Scan

Run installed security scanning tools against the current codebase.

## Instructions

1. **Check which tools are installed:**
   ```bash
   command -v shellcheck bandit gitleaks semgrep
   ```
   Report which tools are available and which are missing. Do not
   fail if some tools are absent — run what's available.

2. **Run fast tools first** (all sub-second):
   - `shellcheck -f gcc` on all `.sh`/`.bash`/`.zsh` files found via Glob
   - `bandit -r . -f json --quiet` on Python files
   - `gitleaks detect --source . --report-format json --report-path /dev/stdout --no-banner`

3. **Report results** from fast tools immediately. Group findings
   by tool and severity.

4. **Ask before running semgrep** — it takes ~24 seconds:
   > "semgrep is available but takes ~24 seconds. Run it?"

   If approved: `semgrep scan --config auto --json --quiet .`

5. **Summarize all findings** by severity (critical, high, medium,
   low, info). Note any tools that were unavailable.

## Notes

- Never install tools automatically — report missing tools and
  let the user decide
- shellcheck exit code 1 means findings (not an error)
- bandit `--quiet` suppresses the progress bar but keeps findings
- gitleaks may find false positives in test fixtures — note this
