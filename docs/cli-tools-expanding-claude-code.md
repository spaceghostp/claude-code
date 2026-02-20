# CLI Tools That Expand Claude Code's Capabilities

## The Filter

The [full research document](cli-tools-that-outperform-claude-code.md) catalogs 50+ tools. This document applies a sharper filter: **which tools can Claude Code invoke non-interactively via Bash, consume structured output, and gain capabilities it doesn't have natively?**

Three tests, all must pass:
1. **Non-interactive** — runs without TTY, produces parseable output
2. **Capability gap** — does something Claude Code's 22 native tools (+ 1 conditional) cannot (see [native-tools-reference.md](native-tools-reference.md))
3. **Real value** — the gap matters in practice, not just in theory

---

## Tested: Already Installed

All four tools tested against this repo (WS-000-03: ~1800 LOC Python, shell scripts, YAML, markdown).

### ast-grep

| Metric | Value |
|--------|-------|
| **Disk** | 44 MB (`/opt/homebrew/Cellar/ast-grep/`) |
| **Dependencies** | 0 (static binary) |
| **Scan time** | 0.02s (full repo, Python structural search) |
| **Output** | JSON with AST node positions, metavariable bindings |

**Test results:** Searched `$FUNC($$$ARGS)` across all Python files. Returned 45 function call sites with exact byte offsets, line/column positions, and metavariable captures (which function, which arguments). JSON output includes the matched text, surrounding lines, and language.

**Native alternative:** Grep can find `re.search(` but can't distinguish `re.search(pattern, command)` from `re.search` appearing in a comment or string. LSP provides go-to-definition and find-references for symbols but can't search for structural patterns like "all try/catch blocks catching generic Exception."

**Real value: HIGH.** The gap is genuine and frequent. Every codemod, every "find all instances of this pattern," every refactoring across files benefits from structural awareness. The 0.02s scan time means zero overhead. This is the single highest-value tool on the list.

**Overhead verdict:** Negligible. 44 MB static binary, 0 deps, instant startup, instant scan.

---

### semgrep

| Metric | Value |
|--------|-------|
| **Disk** | 165 MB (Python package + bundled binary) |
| **Dependencies** | 22 Python packages (attrs, boltons, click, colorama, jsonschema, rich, etc.) |
| **Scan time** | 24s (auto rules, full repo) |
| **Output** | JSON with findings, severity, rule metadata |

**Test results:** Found 4 issues with `--config auto`:
- `no-sudo-in-dockerfile` in `.devcontainer/Dockerfile:52`
- `ifs-tampering` in two shell scripts (`.devcontainer/init-firewall.sh:3`, `refresh-firewall-ips.sh:3`)
- `run-shell-injection` in `.github/workflows/claude-dedupe-issues.yml:41`

Also reported 14 errors (rules that couldn't parse certain files). The shell injection finding in the GitHub workflow is a genuine catch — it's the kind of pattern an LLM review could miss because the injection vector is split across YAML interpolation boundaries.

**Native alternative:** Claude Code can review code for security issues, but probabilistically. It reads files and reasons about patterns. For a small repo, this works. For a large repo, it can't guarantee it checked every file, every pattern.

**Real value: MODERATE.** The 24-second scan time is the main cost. On this small repo, Claude Code could manually review the 4 Python/shell files faster than semgrep boots up. The value scales with codebase size — at 100k+ LOC, semgrep's exhaustive guarantee becomes worth the wait. The 15.3% baseline detection rate (academic finding) means you're only catching patterns that have rules written for them. The GitHub Actions shell injection was a genuine find.

**Overhead verdict:** Heavy. 165 MB, 22 deps, 24s scan. Justified for security audits on larger codebases. Overkill for quick checks on small repos.

---

### gitleaks

| Metric | Value |
|--------|-------|
| **Disk** | 15 MB (`/opt/homebrew/Cellar/gitleaks/`) |
| **Dependencies** | 0 (static Go binary) |
| **Scan time** | 0.23s (full git history) |
| **Output** | JSON with secret type, file, commit, line |

**Test results:** Clean — no secrets found in any commit. This is the expected result for a repo that never contained credentials, but the scan covered every commit in 230ms.

**Native alternative:** Claude Code cannot scan git history systematically. It can `git log -p` and read diffs, but it would need to page through every commit and search for secret patterns — impractical for repos with hundreds of commits. Even for a single commit, Claude Code would pattern-match probabilistically rather than against a deterministic ruleset.

**Real value: HIGH.** The gap is absolute — Claude Code has no equivalent capability. 0.23s for complete history coverage. The value is highest when onboarding to an unfamiliar repo or before a public release. The tool catches patterns (AWS keys, private keys, tokens) that are easy to miss in manual review.

**Overhead verdict:** Negligible. 15 MB, 0 deps, sub-second scan.

---

### bandit

| Metric | Value |
|--------|-------|
| **Disk** | 1 MB (Python package) |
| **Dependencies** | 3 (PyYAML, rich, stevedore) |
| **Scan time** | 0.22s (1813 LOC) |
| **Output** | JSON with severity, confidence, CWE references |

**Test results:** Found 4 issues in `plugins/security-guidance/hooks/security_reminder_hook.py`:
- [MEDIUM] Insecure temp file usage (line 16)
- [LOW] try/except/pass silencing errors (lines 25, 182)
- [LOW] Standard pseudo-random generator used (line 262) — not suitable for security contexts

**Native alternative:** Claude Code can read Python files and spot these patterns. In fact, for this specific repo, I could have found all four issues by reading the one Python file. Bandit's advantage is exhaustiveness across large codebases — it will check every `.py` file against every rule, every time.

**Real value: LOW-MODERATE.** For Python-only analysis on small repos, Claude Code's native review is often sufficient. The value increases with codebase size and CI integration (run on every commit). The findings here were real but not high-impact — the temp file issue is worth fixing, the try/except/pass patterns are debatable.

**Overhead verdict:** Minimal. 1 MB, 3 deps, sub-second scan. Low cost to keep available.

---

## Not Installed: Overhead Estimates

All sizes estimated from brew info. Tools marked with 0 deps are static binaries.

| Tool | Brew deps | Estimated disk | Value case |
|------|-----------|---------------|------------|
| **shellcheck** | 1 (GHC runtime) | ~30-50 MB | Deterministic shell linting — catches quoting/splitting bugs Claude Code misses |
| **scc** | 0 | ~5 MB | Instant LOC/complexity metrics — Claude Code can't count lines precisely |
| **hyperfine** | 0 | ~3 MB | Statistical benchmarking — `time` gives one noisy sample, hyperfine gives significance |
| **difftastic** | 0 | ~15 MB | AST-aware diffs — formatting noise removed from code review |
| **git-absorb** | 1 (libgit2) | ~10 MB | Fixup commit targeting — no native equivalent |
| **just** | 0 | ~5 MB | Project command runner — Claude Code can read+run `justfile` recipes |
| **watchexec** | 0 | ~5 MB | File-watch triggers — can run in background Bash |
| **dive** | 0 | ~20 MB | Container layer analysis — no native equivalent |
| **comby** | 3 | ~30 MB | Structural search-replace — complements ast-grep for non-code formats |

### Priority assessment for uninstalled tools

**Install immediately (high value, near-zero overhead):**
- `scc` — 5 MB, 0 deps. Instant precise codebase metrics. Claude Code cannot count LOC or compute complexity scores without reading every file.
- `hyperfine` — 3 MB, 0 deps. Proper benchmarking replaces unreliable `time` measurements. JSON output with statistical analysis.
- `shellcheck` — ~40 MB (Haskell runtime), 1 dep. This repo has 11 shell scripts. The `ifs-tampering` findings semgrep caught in `.devcontainer/*.sh` are exactly the kind of issue ShellCheck was built for, and it would catch more.

**Install when needed (moderate value, specific use cases):**
- `difftastic` — 15 MB, 0 deps. Valuable during code review sessions, especially after reformatting. Less useful day-to-day.
- `just` — 5 MB, 0 deps. Only valuable if the project has a `justfile`. Creates cross-session persistence for project commands.
- `watchexec` — 5 MB, 0 deps. Only valuable for TDD workflows or long-running file-watch tasks.
- `git-absorb` — ~10 MB. Only valuable when doing multi-commit cleanup work.

**Install for specific domains:**
- `dive` — 20 MB. Only if working with Docker images.
- `comby` — 30 MB. Only if doing structural transforms on non-code formats (JSON, YAML, HTML) where ast-grep can't help.

---

## Real Value Assessment: Honest Accounting

Cross-referenced against [native-tools-reference.md](native-tools-reference.md) and [usage-methodology.md](usage-methodology.md).

### What actually expands my capabilities (vs. what sounds good)

**Genuine capability expansions:**

| Tool | Why it's genuine | Native tool gap (from reference) |
|------|-----------------|--------------------------------|
| **ast-grep** | Grep does regex on text. LSP does symbol navigation. Neither does structural pattern matching. No native tool can find "all functions with >3 params" or "all catch blocks catching Exception." | Grep: "No AST/structural awareness." Edit: "No AST transforms, no bulk codemod." |
| **gitleaks** | No native tool traverses git history exhaustively. Bash can run `git log -p` but I'd need to page through every commit and regex-search — impractical. | Bash: runs commands but can't systematically scan history. |
| **scc** | No native tool counts lines or computes complexity. I'd need to Read every file and manually count — slow, approximate, and wasteful of context window. | No equivalent capability listed in any native tool. |
| **hyperfine** | Bash can run `time` but that's one noisy sample. Statistical significance requires multiple runs with warmup and outlier detection — I can script this but hyperfine does it better in one command. | Bash: "No `-i` interactive, no file watch, no streaming" — and no statistical benchmarking. |
| **shellcheck** | Deterministic shell analysis catches classes of bugs (word splitting, quoting, subshell scope) that I sometimes miss. The semgrep `ifs-tampering` findings prove this repo has exactly these issues. | Grep/Edit have no shell-specific awareness. |

**Marginal capability expansions (tool does it better, but I can approximate):**

| Tool | Why it's marginal | What I can do instead |
|------|------------------|-----------------------|
| **semgrep** | On small repos (<10k LOC), I can read every file and review for security patterns manually. The 24s overhead is comparable to my review time. Value only clearly exceeds cost at scale. | Read files + reason about patterns. Miss rate is higher but latency is lower for small repos. |
| **bandit** | Same as semgrep but Python-only. On this repo's 1813 LOC, I could have found all 4 issues by reading the one Python file. | Read + review. Works fine for small Python codebases. |
| **difftastic** | I can read both file versions and reason about what changed semantically. AST-aware diff saves me work but doesn't give me a capability I lack. | Read both versions, compare mentally. Slower but possible. |
| **comby** | ast-grep covers most structural search/replace for code. Comby adds value for non-code formats (JSON, YAML) but Edit's `replace_all` handles many of those cases. | Edit with `replace_all`, or ast-grep for code. |
| **git-absorb** | I can figure out which commit a change belongs to by reading `git log` and the diff, then create fixup commits manually. It's tedious but possible. | Manual `git log` analysis + `git commit --fixup`. |

**Not a real expansion (sounds useful, isn't):**

| Tool | Why it's not real |
|------|------------------|
| **jscodeshift** | Requires writing a transform script first. I'd need to write the codemod, then run it. For most tasks, I can just Edit files directly — it's slower but doesn't require learning jscodeshift's API. Only valuable for 100+ file transforms. |
| **OpenRewrite** | JVM-specific, requires Maven/Gradle project. This repo has no JVM code. The tool is excellent but the use case is narrow. |
| **madge** | Only for JS/TS projects. This repo has no JS/TS. For repos that do, `madge --circular --json src/` is genuinely useful but the use case is project-type-specific. |

---

## Category B: Tools I Cannot Use (Interactive/TUI)

These require human interaction. They expand the **user's** capabilities, not mine.

| Tool | Why I can't use it |
|------|-------------------|
| **lazygit** | TUI — interactive rebase, visual hunk staging require human eyes and input |
| **fzf** | Interactive fuzzy picker — I can't select from a live menu mid-pipeline |
| **btop** | Real-time streaming TUI — I run point-in-time commands |
| **zellij** | Terminal multiplexer — organizes the human's workspace |
| **nushell** | Alternative shell — I operate through Bash |
| **starship** | Prompt customizer — visual context for humans |
| **atuin** | Interactive history search — aids human recall |
| **delta** | Diff pager with syntax highlighting — visual enhancement I can't see |
| **git-branchless** | Interactive commit DAG navigation |

---

## Category C: Environment Tools (Indirect)

| Tool | How it helps me indirectly |
|------|--------------------------|
| **mise** | Ensures correct tool versions on PATH — I use whatever's available |
| **direnv** | Auto-loads `.envrc` — I inherit the env vars |
| **devbox** | Reproducible environments — I get consistent tooling |
| **just** | Borderline Category A — I can read a `justfile` and `just <recipe>` to run project commands |
| **watchexec** | Borderline Category A — I can run `watchexec` in a background Bash shell |

---

## Installation

### Already available
```
ast-grep (44 MB)    — structural code search
semgrep  (165 MB)   — security scanning (heavy)
gitleaks (15 MB)    — secret detection
bandit   (1 MB)     — Python security
```

### Recommended installs
```bash
brew install scc hyperfine shellcheck
```
Total: ~48 MB, 1 dependency (shellcheck's GHC runtime). These three fill the most impactful gaps with the least overhead.

### Optional installs
```bash
brew install difftastic git-absorb just watchexec dive comby
```

---

## Summary

| Tier | Tools | Combined disk | Real value |
|------|-------|--------------|------------|
| **Already installed, high value** | ast-grep, gitleaks | 59 MB | Structural search + secret scanning — no native equivalent |
| **Already installed, situational** | semgrep, bandit | 166 MB | Security scanning — value scales with codebase size |
| **Not installed, high value** | scc, hyperfine, shellcheck | ~48 MB | Metrics + benchmarking + shell linting — no native equivalent |
| **Not installed, situational** | difftastic, just, watchexec, git-absorb, dive, comby | ~85 MB | Domain-specific — install when the use case arises |
| **Not a real expansion** | jscodeshift, OpenRewrite, madge | varies | Narrow use cases, require specific project types or significant setup |

**Total additional disk for recommended installs: ~48 MB.**

The honest bottom line: of 14 tools analyzed, **5 provide genuine capability expansions** (ast-grep, gitleaks, scc, hyperfine, shellcheck), **4 provide marginal expansions** that scale with codebase size (semgrep, bandit, difftastic, comby), and **5 sound useful but don't materially change what I can do** for most tasks.
