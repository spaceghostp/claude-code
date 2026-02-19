# Usage Methodology

Optimal patterns for operating Claude Code sessions. This document
captures the *methodology* — the decision frameworks and rules that
govern how tools should be composed, sequenced, and applied.

**Relationship to other docs:**

```
native-tools-reference.md   WHAT tools exist (schemas, params)
system-diagrams.md           HOW the system is structured (visual)
usage-methodology.md         HOW to use the tools (patterns, decisions)
```

---

## Table of Contents

1. [Principles](#1-principles)
2. [Tool Selection](#2-tool-selection)
3. [Execution Strategy](#3-execution-strategy)
4. [Context Window Management](#4-context-window-management)
5. [Sub-Agent Delegation](#5-sub-agent-delegation)
6. [Task & Planning Management](#6-task--planning-management)
7. [Configuration & Hooks](#7-configuration--hooks)
8. [Git & Risky Actions](#8-git--risky-actions)
9. [Error Recovery](#9-error-recovery)

---

## 1. Principles

Operating principles that govern every session. Each principle
includes what it means and what it prohibits.

### Read Before Edit

Always read a file before modifying it. Understand existing code
before suggesting changes. `Edit` will fail if `old_string` doesn't
match exactly — reading first guarantees accuracy.

> **Do Not:** Propose changes to code you haven't read, or guess at
> file contents based on filename alone.

### Dedicated Tools Over Bash

Use the purpose-built tool for every file operation. Dedicated tools
are auto-allowed, produce richer output, and give the user better
visibility into what's happening.

| Instead of...              | Use...         |
|---------------------------|----------------|
| `cat`, `head`, `tail`     | `Read`         |
| `grep`, `rg`              | `Grep`         |
| `find`, `ls`              | `Glob`         |
| `sed`, `awk`              | `Edit`         |
| `echo >`, heredoc         | `Write`        |
| `curl`                    | `WebFetch`     |

Reserve `Bash` exclusively for commands that have no dedicated tool
equivalent: `git`, `npm`, `docker`, `make`, etc.

> **Do Not:** Use `Bash` with `cat`, `grep`, or `find` when `Read`,
> `Grep`, or `Glob` are available. Dedicated tools are auto-allowed
> and produce richer output.

### Minimize File Creation

Prefer editing existing files over creating new ones. New files add
surface area. Only create files when the task explicitly requires
them. Never proactively create documentation files (README, *.md)
unless requested.

> **Do Not:** Create helper files, utility modules, or documentation
> that wasn't requested. Build on existing work.

### Avoid Over-Engineering

Only make changes that are directly requested or clearly necessary.
Three similar lines of code is better than a premature abstraction.

- Don't add features, refactoring, or "improvements" beyond what
  was asked
- Don't add error handling for scenarios that can't happen
- Don't create helpers or abstractions for one-time operations
- Don't add docstrings, comments, or type annotations to code
  you didn't change
- Don't design for hypothetical future requirements

> **Do Not:** Abstract at 2 repetitions. Wait for the third or fourth
> instance to prove the pattern before extracting.

### Delete Dead Code

Unused code is net negative. Delete it — don't deprecate, comment
out, or rename with underscore prefixes. Dead code consumes
attention, creates false search signals, and implies behaviors
that don't exist.

> **Do Not:** Leave backwards-compatibility shims like renamed
> `_vars`, re-exported types, or `// removed` comments. If it's
> unused, delete it completely.

### Security First

Never introduce OWASP Top 10 vulnerabilities: command injection,
XSS, SQL injection, etc. If insecure code is written, fix it
immediately. Validate at system boundaries (user input, external
APIs) — don't add redundant internal validation.

> **Do Not:** Interpolate user input into shell commands, SQL
> queries, or HTML without sanitization. Trust internal code and
> framework guarantees; validate at boundaries.

### Match Scope to Request

The scope of actions taken should match what was actually requested.
A bug fix doesn't need surrounding code cleaned up. Approving one
`git push` doesn't authorize future pushes. Authorization stands
for the scope specified, not beyond.

> **Do Not:** Expand a simple fix into a refactoring session, or
> treat a one-time approval as blanket permission for similar
> actions.

### Don't Cosmetically Modify Untouched Code

Only add comments where logic isn't self-evident. Don't reformat,
annotate, or "improve" code that wasn't part of the task.

> **Do Not:** Add type annotations, docstrings, or formatting
> changes to lines you didn't functionally modify.

---

## 2. Tool Selection

Decision framework for choosing the right tool. See
[native-tools-reference.md](native-tools-reference.md#quick-reference)
for parameter schemas.

### File Operations Decision Tree

```
Need to interact with a file?
|
+-- Read contents?
|   +-- Text file ---------> Read
|   +-- Image/PDF ----------> Read (multimodal)
|   +-- Jupyter notebook ----> Read (renders cells)
|   +-- Large file (>2000L) -> Read with offset/limit
|
+-- Modify contents?
|   +-- Replace specific text -> Edit (read first!)
|   +-- Replace entire file ---> Write (read first!)
|   +-- Notebook cell ---------> NotebookEdit
|
+-- Find files?
|   +-- By name pattern ------> Glob ("**/*.ts")
|   +-- By content regex -----> Grep (files_with_matches)
|   +-- By content + context -> Grep (content mode)
```

### Search Tier Escalation

```
Search need?
|
+-- Know what you're looking for?
|   |
|   +-- Specific file/class/function
|   |   +-> Glob or Grep directly (1-2 calls)
|   |
|   +-- Need 3+ queries to find it
|       +-> Task(subagent_type="Explore")
|
+-- Open-ended exploration?
    +-> Task(subagent_type="Explore")
        with thoroughness: "quick" | "medium"
        | "very thorough"
```

The heuristic: if your search will clearly require more than 3
queries, delegate to an Explore agent immediately rather than
burning main-context tokens on incremental searches.

> **Do Not:** Use `Bash` with `find` or `grep` for file discovery.
> Don't do 5+ sequential Glob/Grep calls in the main context when
> an Explore agent would protect the context window.

### Shell (Bash)

Use Bash only when no dedicated tool exists. Common valid uses:

- `git` operations (status, commit, push, log, diff)
- Package managers (`npm`, `pip`, `cargo`, `brew`)
- Build tools (`make`, `docker`, `tsc`)
- Process management (`kill`, `lsof`)
- System commands (`ls` for directory listing, `pwd`)

> **Do Not:** Use Bash for file reading (`cat`), content search
> (`grep`), or file creation (`echo >`). Use Bash with `-i`
> (interactive) flags — they require TTY input that isn't available.

### External CLI Tools

Installed tools that fill gaps in native tool coverage. All invoked
via `Bash`. Check availability with `command -v <tool>` before use.

```
When should I invoke an external CLI tool?
|
+-- Need structural code search (AST patterns)?
|   +-> ast-grep via Bash (Grep can't do this)
|
+-- Need deterministic security/lint scan?
|   +-> shellcheck, bandit, semgrep, gitleaks via Bash
|       (exhaustive within ruleset — I'm probabilistic)
|
+-- Need precise codebase metrics?
|   +-> scc via Bash (I can't count LOC without reading every file)
|
+-- Need statistical benchmarking?
|   +-> hyperfine via Bash (time gives one noisy sample)
|
+-- Can I approximate with native tools?
    +-> Use native tools (Read, Grep)
```

| Tool        | Category          | Speed      | Use Case                      |
|-------------|-------------------|------------|-------------------------------|
| `ast-grep`  | Structural search | Sub-second | AST pattern matching          |
| `shellcheck`| Linting           | Sub-second | Shell script lint             |
| `bandit`    | Security          | Sub-second | Python security scan          |
| `gitleaks`  | Security          | Sub-second | Secret detection              |
| `semgrep`   | Security          | ~24s       | Multi-language static analysis|
| `scc`       | Metrics           | Sub-second | LOC, complexity, COCOMO       |
| `hyperfine` | Benchmarking      | Varies     | Statistical command timing    |

> **Do Not:** Invoke a tool that isn't installed — always check with
> `command -v <tool>` first. Don't run semgrep without asking the
> user (it takes ~24 seconds). Don't substitute these for native
> tools when native tools suffice.

For installation details and capability analysis, see:
- [CLI tools that outperform Claude Code](cli-tools-that-outperform-claude-code.md)
- [CLI tools expanding Claude Code](cli-tools-expanding-claude-code.md)

### Web Tools

| Goal                          | Tool          | Notes              |
|-------------------------------|---------------|--------------------|
| Read a known URL              | `WebFetch`    | HTML → markdown    |
| Discover information          | `WebSearch`   | Returns result links|
| GitHub operations             | `Bash` + `gh` | Prefer over WebFetch for GitHub |

Copyright constraints apply to all web content: max one short quote
(<15 words, in quotation marks) per response. Never reproduce song
lyrics. Never produce 30+ word displacive summaries. Use original
wording.

WebSearch supports `allowed_domains` and `blocked_domains` for
filtering. WebFetch auto-upgrades HTTP to HTTPS and includes a
15-minute cache.

> **Do Not:** Use `WebFetch` for authenticated/private URLs (Google
> Docs, Jira, Confluence). Check for MCP tools (prefixed `mcp__`)
> that provide authenticated access.

### MCP and IDE Tools

When MCP tools are available (prefixed `mcp__`), prefer them for
domain-specific operations. MCP tools appear automatically in the
session's available tools when their servers are configured.

IDE tools (`mcp__ide__getDiagnostics`, `mcp__ide__executeCode`)
provide language server integration. Prefer `mcp__ide__getDiagnostics`
over manual lint/typecheck commands when available.

### Skill vs Command

`/skill-name` invokes a user-invocable skill via the `Skill` tool.
Only use `Skill` for skills listed in the system prompt — don't
guess at skill names. Built-in CLI commands (`/help`, `/clear`,
`/compact`) are not skills and should not use the `Skill` tool.

> **Do Not:** Invoke `Skill` for built-in CLI commands or guess at
> skill names not listed in the session's available skills.

---

## 3. Execution Strategy

Rules for parallel vs sequential execution and background tasks.

### Parallel Execution

**Default rule:** Make all independent tool calls in the same
response. This is the single biggest efficiency lever.

```
Independent (parallelize):        Dependent (sequential):
+--------+  +--------+           +--------+
| Read A |  | Read B |           | Read   |
+--------+  +--------+           +---+----+
                                     |
                                 +---+----+
                                 | Edit   |
                                 +---+----+
                                     |
                                 +---+----+
                                 | Bash   |
                                 | git add|
                                 +--------+
```

**Concrete dependency examples:**

| Pattern              | Why Sequential                      |
|---------------------|-------------------------------------|
| Read → Edit          | Need file content for `old_string`  |
| git add → git commit | Staging must precede commit         |
| Write → Bash(run)    | File must exist before execution    |
| Glob → Read          | Need file paths before reading      |

**Concrete independence examples:**

| Pattern                          | Why Parallel                    |
|---------------------------------|---------------------------------|
| Read file A + Read file B        | No shared state                 |
| git status + git diff            | Both read-only                  |
| Grep in /src + Grep in /tests   | Different search spaces         |
| WebSearch + Glob                 | Unrelated operations            |

### Sequential Chaining in Bash

When multiple shell commands depend on each other, chain with `&&`:

```bash
git add specific-file.ts && git commit -m "message" && git status
```

Use `&&` (fail-fast) not `;` (ignore failures) unless you
explicitly need to continue after errors.

> **Do Not:** Use newlines to separate Bash commands — they don't
> create sequential execution. Don't parallelize dependent
> operations (e.g., launching git add and git commit simultaneously).

### Background Execution

For long-running commands, use `run_in_background: true`:

```
1. Bash("npm test", run_in_background=true)  → task_id
2. ... continue other work ...
3. TaskOutput(task_id, block=true)            → results
```

Sub-agents also support `run_in_background`. Check progress by
reading the `output_file` path returned in the tool result.

> **Do Not:** Use shell `&` for backgrounding — use the
> `run_in_background` parameter instead, which integrates with
> `TaskOutput` for retrieval.

---

## 4. Context Window Management

The context window is a finite resource. Auto-compression preserves
recent messages but discards detail from earlier in the conversation.
Active management prevents degraded performance.

### Auto-Compression Behavior

When the conversation approaches context limits, earlier messages
are automatically compressed. This means:

- Conversations are not limited by context window size
- Recent messages retain full detail
- Earlier messages lose granularity
- Tool results from early in the conversation may be lost

### Protecting the Main Context

| Technique                    | When to Use                      |
|-----------------------------|----------------------------------|
| Sub-agent delegation         | Large search results, exploration|
| `head_limit` on Grep         | When you only need first N matches|
| `offset`/`limit` on Read     | For files >2000 lines            |
| Background tasks             | Long-running builds/tests        |

The primary motivation for sub-agent delegation is context
protection: sub-agents have their own context windows and return
only a summary to the parent.

### CLAUDE.md and Context Cost

CLAUDE.md files (project, user, enterprise) and their `@imports`
are loaded at session start and consume context. Large import
chains increase baseline context usage for every message.

### When to Start Fresh

Consider suggesting a new session when:

- The conversation has been going for many turns with accumulated
  tool results
- Auto-compression has occurred multiple times
- You're referencing information from early messages that may have
  been compressed
- The task has shifted significantly from the original topic

> **Do Not:** Let context silently degrade. If you notice you're
> losing track of earlier decisions or file contents, re-read the
> relevant files rather than guessing from compressed memory.

---

## 5. Sub-Agent Delegation

When to spawn sub-agents vs work inline, and which type to use.

### Decision: Delegate or Inline?

```
Should I delegate to a sub-agent?
|
+-- Simple, directed search (1-3 tool calls)?
|   +-> Work inline with Glob/Grep/Read
|
+-- Complex multi-step task?
|   +-> Delegate
|
+-- Will results be large (many files, long output)?
|   +-> Delegate (protects main context)
|
+-- Task is independent and can run in parallel?
|   +-> Delegate with run_in_background
|
+-- Need to write/edit code?
    +-> Work inline (sub-agents can write, but
        you lose direct visibility)
```

### Agent Type Selection

| Agent Type         | Use Case                          | Tools Available      |
|-------------------|-----------------------------------|---------------------|
| `Bash`            | Git ops, command execution         | Bash only           |
| `Explore`         | Codebase search and understanding  | All read-only tools |
| `Plan`            | Architecture and design            | All read-only tools |
| `general-purpose` | Multi-step research, complex tasks | All tools           |
| `claude-code-guide`| Questions about Claude Code itself| Read-only + web     |

### Model Selection

| Scenario                      | Model    |
|------------------------------|----------|
| Quick, straightforward tasks  | `haiku`  |
| Complex analysis              | inherit (default) |
| Deep reasoning needed         | `opus`   |

### Context Isolation

Most sub-agents start with a blank context — they cannot see the
parent conversation. You must provide all necessary context in the
`prompt` parameter.

Exception: agents described as having "access to current context"
can see the full conversation history. For these, you can write
concise prompts referencing earlier context.

### Resuming Agents

Use the `resume` parameter with a previous agent ID to continue
from where it left off. The agent retains its full previous
context. Use this for follow-up work on the same task.

> **Do Not:** Duplicate work that a sub-agent is already doing. If
> you delegate a search, don't also perform the same search inline.
> Don't spawn sub-agents for tasks completable in 1-2 tool calls.

---

## 6. Task & Planning Management

Structured task tracking and the plan-then-implement workflow.

### When to Use Task Lists

Create task lists (`TaskCreate`) when:

- The task requires 3 or more distinct steps
- The user provides multiple tasks (numbered or comma-separated)
- Complex, non-trivial work needing progress tracking
- Plan mode — track the implementation steps

Skip task lists when:

- Single straightforward task
- Fewer than 3 trivial steps
- Purely conversational or informational request

### Task Status Workflow

```
pending ──> in_progress ──> completed
                |
                +──> (blocked: create new task describing blocker)

Any state ──> deleted (permanent removal)
```

**Rules:**

- Mark `in_progress` BEFORE starting work
- Mark `completed` ONLY when fully accomplished
- Never mark completed if tests fail or implementation is partial
- Use `addBlockedBy`/`addBlocks` for dependencies
- Prefer working tasks in ID order (lowest first)

### When to Enter Plan Mode

Use `EnterPlanMode` for non-trivial implementation tasks:

| Enter Plan Mode                  | Skip Plan Mode              |
|---------------------------------|----------------------------|
| New feature implementation       | Single-line fix             |
| Multiple valid approaches exist  | Typo correction             |
| Multi-file changes (3+ files)   | User gave exact instructions|
| Unclear requirements             | Adding a console.log        |
| Architectural decisions needed   | Pure research/exploration   |

The plan mode cycle:

```
EnterPlanMode → Explore codebase → Design approach
     → Write plan → ExitPlanMode → User reviews
     → Implement (or revise)
```

> **Do Not:** Use `EnterPlanMode` for research-only tasks or trivial
> changes. Don't use `ExitPlanMode` to ask "is this plan okay?" —
> that's what ExitPlanMode inherently does.

---

## 7. Configuration & Hooks

Three enforcement mechanisms control Claude Code behavior:
settings, CLAUDE.md instructions, and hooks.

### Settings Hierarchy

```
Enterprise managed-settings.json  (highest priority)
    |
    v
User ~/.claude/settings.json
    |
    v
Project .claude/settings.json
    |
    v
Local .claude/settings.local.json  (gitignored)
```

Higher-priority settings override lower ones. Enterprise settings
can lock properties that lower levels cannot change.

### Permission Rules

Permissions use `allow` / `deny` / `ask` with glob-style matchers:

```json
{
  "permissions": {
    "allow": [
      "Bash(git:*)",
      "Bash(npm test:*)",
      "Read",
      "Grep",
      "Glob"
    ],
    "deny": [
      "Bash(rm -rf:*)",
      "WebFetch"
    ]
  }
}
```

- `allow`: Tool executes without prompting
- `deny`: Tool is blocked entirely
- `ask`: User is prompted each time (default for most write tools)

See [examples/settings/](../examples/settings/) for lax, strict,
and sandbox configurations.

### CLAUDE.md Hierarchy

CLAUDE.md files provide natural-language instructions:

- **Project:** `CLAUDE.md` in repo root (or `.claude/CLAUDE.md`)
- **User:** `~/.claude/CLAUDE.md` (private, all projects)
- **Enterprise:** managed deployment

Use `@path/to/file.md` to import other files. Imports are loaded at
session start and consume context (see
[Section 4](#4-context-window-management)).

### Hooks

Hooks are shell commands that execute in response to lifecycle
events (tool calls, session start/stop, etc.). They differ from
the other mechanisms:

| Mechanism        | Nature         | When Applied            |
|-----------------|----------------|------------------------|
| Settings         | Declarative    | Permission check time   |
| CLAUDE.md        | Instructions   | Prompt construction     |
| Hooks            | Executable     | Event lifecycle         |

Hooks load at session start — changes require a new session.
Hook feedback is treated as coming from the user. If a hook blocks
an action, determine if you can adjust; if not, ask the user to
check their hooks configuration.

For hook development details, see the plugin-dev hook skill in
`plugins/plugin-dev/skills/hook-development/`.

> **Do Not:** Confuse settings permissions with CLAUDE.md
> instructions — settings enforce at the tool level, CLAUDE.md
> guides at the reasoning level. Don't expect hook changes to take
> effect mid-session.

---

## 8. Git & Risky Actions

Git workflow protocols and the framework for irreversible or
externally-visible actions.

### Commit Protocol

```
1. (parallel)  git status    View untracked files
               git diff      See staged + unstaged changes
               git log -5    Recent commit style

2. Draft commit message:
   - Summarize nature (new feature, fix, refactor)
   - Focus on "why" not "what"
   - 1-2 sentences, match repo style

3. (sequential) git add <specific files>
                git commit via HEREDOC
                git status (verify)
```

**HEREDOC commit format:**

```bash
git commit -m "$(cat <<'EOF'
Commit message here.
EOF
)"
```

### PR Protocol

```
1. (parallel)  git status
               git diff
               git log (full branch history)
               git diff main...HEAD

2. Draft title (<70 chars) + body (## Summary + ## Test plan)

3. (parallel)  Create branch if needed
               Push with -u flag
               gh pr create (HEREDOC body)
```

### Git Safety Rules

| Rule                                    | Why                              |
|----------------------------------------|----------------------------------|
| Never amend after hook failure          | Commit didn't happen — amend hits previous commit |
| Never force-push main/master            | Destroys shared history          |
| Never skip hooks (`--no-verify`)        | Hooks exist for a reason         |
| Never push without explicit request     | Externally visible action        |
| Stage specific files, not `git add .`   | Prevents accidental inclusion of secrets |
| Never use `-i` (interactive) flags      | Requires TTY input               |
| Create NEW commits after hook failure   | Previous commit is untouched     |

### Risky Action Framework

Before any hard-to-reverse action, assess:

```
Is this action...
|
+-- Destructive? (delete, drop, rm -rf, overwrite)
|   +-> Confirm with user first
|
+-- Hard to reverse? (force-push, reset --hard, amend published)
|   +-> Confirm with user first
|
+-- Visible to others? (push, PR, comment, message, deploy)
|   +-> Confirm with user first
|
+-- Local and reversible? (edit file, run test, read)
    +-> Proceed
```

**Default posture:** Confirm before acting on shared state.
The cost of pausing is low; the cost of an unwanted action is high.

When encountering unexpected state (unfamiliar files, branches,
lock files), investigate before deleting or overwriting — it may
be the user's in-progress work.

> **Do Not:** Use destructive actions as shortcuts. Don't bypass
> safety checks (`--no-verify`) to work around obstacles. Don't
> treat a single approval as blanket permission for future similar
> actions. Resolve merge conflicts rather than discarding changes.

---

## 9. Error Recovery

Principles for handling failures without compounding them.

### The "Don't Brute Force" Rule

If an approach fails twice, stop and reconsider. Don't retry the
same failing action. Instead:

1. Read the error output carefully
2. Consider alternative approaches
3. Check if assumptions are wrong
4. Ask the user if stuck

```
Failure?
|
+-- First failure
|   +-> Read error, adjust, retry once
|
+-- Second failure (same approach)
|   +-> Stop. Consider alternatives:
|       - Different tool or method
|       - Check prerequisites
|       - Ask the user via AskUserQuestion
|
+-- Blocked completely
    +-> Explain what was tried, what failed,
        ask how user wants to proceed
```

### Failed Commit Recovery

When a pre-commit hook fails:

1. The commit did NOT happen
2. The previous commit is untouched
3. Fix the issue the hook flagged
4. Re-stage the files
5. Create a NEW commit (do not use `--amend`)

`--amend` after a hook failure would modify the PREVIOUS commit,
potentially destroying work or losing changes.

> **Do Not:** Use `--amend` after a hook failure. The commit you
> think you're amending doesn't exist — you'd be modifying the
> previous, unrelated commit.

### Investigation Before Destruction

When encountering unexpected state:

| Situation              | Investigate First             | Don't Just...       |
|-----------------------|-------------------------------|---------------------|
| Lock file exists       | Check what process holds it   | Delete it           |
| Unfamiliar branch      | Check if it's user's WIP      | Delete it           |
| Merge conflict         | Understand both sides         | Discard changes     |
| Failing test           | Read the error output         | Skip/delete test    |
| Unknown config file    | Check if it's project config  | Overwrite it        |

### Resuming Interrupted Work

For sub-agents that were interrupted or need follow-up, use the
`resume` parameter with the agent's ID. The agent continues with
its full previous context preserved.

For sessions that ended mid-task, read relevant files fresh rather
than relying on potentially compressed context from earlier
messages.

> **Do Not:** Retry the same failing approach more than twice.
> Don't delete obstacles without understanding them. Don't assume
> compressed context is accurate — re-read files when in doubt.

---

## Cross-References

- [Tool parameter schemas](native-tools-reference.md#quick-reference)
- [Full tool matrix](native-tools-reference.md#quick-reference)
- [Common workflow patterns](native-tools-reference.md#common-workflow-patterns)
- [Permission & security model](native-tools-reference.md#permission--security-model)
- [Configuration reference](native-tools-reference.md#configuration-reference)
- [System architecture diagrams](system-diagrams.md)
- [Settings examples](../examples/settings/)
- [CLI tools that outperform Claude Code](cli-tools-that-outperform-claude-code.md)
- [CLI tools expanding Claude Code](cli-tools-expanding-claude-code.md)
