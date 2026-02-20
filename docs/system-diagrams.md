# System Diagrams

ASCII architecture diagrams for the WS-000-03 repository and its
supporting systems. All diagrams are 76 characters wide or less.

---

## 1. Repo Directory Architecture

Top-level layout of the plugins marketplace repository.

```
WS-000-03/
|
+-- .claude/                  Project settings + vault symlink
|   +-- settings.json         Hook config (project-level)
|   +-- settings.local.json   Local permissions
|   +-- vault -> ~/.claude/vault   (symlink)
|
+-- .claude-plugin/
|   +-- marketplace.json      Plugin registry manifest
|
+-- .github/
|   +-- ISSUE_TEMPLATE/       5 templates
|   +-- workflows/            12 CI/CD workflows
|
+-- .devcontainer/            Codespace config + firewall
|
+-- docs/                     Reference documentation
|   +-- native-tools-reference.md
|   +-- system-diagrams.md    (this file)
|   +-- obsidian-cognitive-infrastructure.md
|   +-- obsidian-personal-workflow.md
|   +-- autonomous-vault-plan.md
|   +-- BMAD-CALIBRATION-PROMPT.md
|   +-- GSD-CALIBRATION-PROMPT.md
|
+-- plugins/                  14 plugins (see Diagram 2)
|   +-- README.md
|   +-- agent-sdk-dev/
|   +-- cli-tools/
|   +-- claude-opus-4-5-migration/
|   +-- code-review/
|   +-- commit-commands/
|   +-- explanatory-output-style/
|   +-- feature-dev/
|   +-- frontend-design/
|   +-- hookify/
|   +-- learning-output-style/
|   +-- plugin-dev/
|   +-- pr-review-toolkit/
|   +-- ralph-wiggum/
|   +-- security-guidance/
|
+-- examples/
|   +-- hooks/                Example hook scripts
|   +-- settings/             Example settings files
|
+-- scripts/                  11 migration/CI scripts
|
+-- Script/                   Windows devcontainer launcher
|
+-- README.md
+-- CHANGELOG.md
+-- LICENSE.md
+-- SECURITY.md
```

---

## 2. Plugin Ecosystem

All 14 plugins grouped by primary type, showing entry points.

```
+-----------------------------------------------------------+
|                    PLUGIN ECOSYSTEM                        |
+-----------------------------------------------------------+
|                                                           |
|  HOOK-BASED (modify agent behavior via lifecycle events)  |
|  +-----------------------------------------------------+ |
|  | explanatory-output-style  SessionStart hook          | |
|  | learning-output-style     SessionStart hook          | |
|  | security-guidance         PreToolUse hook            | |
|  |                           (matcher: Edit|Write)      | |
|  | cli-tools                 PostToolUse hook, 2 skills | |
|  +-----------------------------------------------------+ |
|                                                           |
|  COMMAND-BASED (user-invoked slash commands)              |
|  +-----------------------------------------------------+ |
|  | commit-commands    /commit, /push, /pr               | |
|  +-----------------------------------------------------+ |
|                                                           |
|  SKILL-BASED (guided workflows with SKILL.md)            |
|  +-----------------------------------------------------+ |
|  | claude-opus-4-5-migration   1 skill                  | |
|  | frontend-design             1 skill                  | |
|  +-----------------------------------------------------+ |
|                                                           |
|  AGENT + COMMAND (agents orchestrated via commands)       |
|  +-----------------------------------------------------+ |
|  | agent-sdk-dev       2 agents, 1 command              | |
|  | code-review         1 agent,  1 command              | |
|  | feature-dev         3 agents, 1 command              | |
|  | pr-review-toolkit   6 agents, 1 command              | |
|  +-----------------------------------------------------+ |
|                                                           |
|  TOOLKIT (full-spectrum: hooks + commands + agents)       |
|  +-----------------------------------------------------+ |
|  | hookify      4 hooks, 4 commands, 1 agent, 1 skill  | |
|  | plugin-dev   7 skills, 3 agents, 1 command           | |
|  +-----------------------------------------------------+ |
|                                                           |
|  HYBRID                                                   |
|  +-----------------------------------------------------+ |
|  | ralph-wiggum   3 commands, 1 Stop hook               | |
|  +-----------------------------------------------------+ |
|                                                           |
+-----------------------------------------------------------+
```

---

## 3. Vault System Architecture

The cognitive vault at `~/.claude/vault/`, showing note types,
scripts, meta files, and skill entry points.

```
~/.claude/vault/
|
+== NOTE TYPES (8) =============================+
|                                                |
|  atoms/           Single irreducible concepts  |
|  tensions/        Ideas pulling against each   |
|  encounters/      Situations where applied     |
|  positions/       Staked falsifiable claims     |
|  questions/       Active unknowns              |
|  revisions/       Documented mind-changes      |
|  anti-library/    Unverified assumptions        |
|  falsifications/  Records of being wrong       |
|                                                |
+================================================+
|
+== _meta/ (governance) ========================+
|                                                |
|  conventions.md      Ontology + rules          |
|  capture-signals.md  When/what to capture      |
|  vault-health.md     Maintained by /maintain   |
|  index.json          Link graph + stats        |
|  position-claims.json                          |
|  quality-baseline.json                         |
|  source-queue.json   Ingestion queue           |
|  source-log.jsonl    Ingestion history         |
|  token-budget.json   Budget tracking           |
|                                                |
+================================================+
|
+== _scripts/ (13 scripts) =====================+
|                                                |
|  build-index.py      Rebuild index.json        |
|  resurface.py        SessionStart hook          |
|  stop-capture-check.py  Stop hook              |
|  validate.py         Schema validation         |
|  vault_parsing.py    Shared parsing utils      |
|  budget-tracker.py   Token budget enforcement  |
|  queue-manager.py    Source queue CLI           |
|  calibration-reveal.py                         |
|  yt-extract.sh       YouTube transcript+OCR    |
|  yt-compress.py      Transcript -> claims      |
|  yt-triage.py        Claims -> vault triage    |
|  repo-extract.py     GitHub repo -> digest     |
|  repo-analyze.py     Digest -> vault analysis  |
|                                                |
+================================================+
|
+== ~/.claude/skills/ (7 vault skills) =========+
|                                                |
|  vault-capture/           Create new note      |
|  vault-maintain/          Index + review        |
|  vault-calibrate-reveal/  Calibration probe    |
|  vault-queue/             Manage ingestion Q   |
|  vault-next/              Session recommender  |
|  vault-ingest-youtube/    YouTube pipeline     |
|  vault-ingest-repo/       GitHub pipeline      |
|                                                |
+================================================+
```

---

## 4. Ingestion Pipeline

Two parallel pipelines for external source ingestion.

```
YOUTUBE INGESTION                GITHUB REPO INGESTION
=================                =====================

+----------------+               +----------------+
| YouTube URL    |               | Repo URL       |
+-------v--------+               +-------v--------+
        |                                |
+-------v--------+               +-------v--------+
| yt-extract.sh  |               | repo-extract.py|
| transcript+OCR |               | clone + digest |
+-------v--------+               +-------v--------+
        |                                |
+-------v--------+               +-------v--------+
| yt-compress.py |               | repo-analyze.py|
| raw -> claims  |               | digest -> vault|
+-------v--------+               |   evidence     |
        |                        +-------v--------+
+-------v--------+                       |
| yt-triage.py   |                       |
| claims -> vault|                       |
| position check |                       |
+-------v--------+                       |
        |                                |
        +-------->  VAULT  <-------------+
                  +------+
                  | atoms, encounters,   |
                  | positions updated    |
                  | source-log.jsonl     |
                  +----------------------+
```

---

## 5. Hook Event System

Lifecycle events and which components fire at each stage.

```
SESSION LIFECYCLE
=================

Setup  (via --init / --init-only / --maintenance)
    |
    v
SessionStart
    |
    +-- [global] resurface.py      Surface vault notes
    +-- [plugin] explanatory-output-style/session-start.sh
    +-- [plugin] learning-output-style/session-start.sh
    |
    v
UserPromptSubmit  (each user message)
    |
    +-- [plugin] hookify/userpromptsubmit.py
    |
    v
PreToolUse  (before each tool call)
    |
    +-- [plugin] hookify/pretooluse.py     (all tools)
    +-- [plugin] security-guidance/        (Edit|Write)
    |
    v
  [ Tool Executes ]
    |
    v
PostToolUse  (after each tool call)
    |
    +-- [plugin] hookify/posttooluse.py
    |
    v
PreCompact  (before context compaction)
    |
    v
SubagentStart  (before sub-agent runs)
    |
    v
SubagentStop  (when sub-agent completes)
    |
    v
Stop  (agent turn ends)
    |
    +-- [global] stop-capture-check.py  Vault capture reminder
    +-- [global] afplay Submarine.aiff  Audio notification
    +-- [plugin] hookify/stop.py
    +-- [plugin] ralph-wiggum/stop-hook.sh
    |
    v
SessionEnd
    |
    +-- [global] build-index.py   Rebuild vault index
    |
    v
Notification  (idle/permission prompts)
    |
    +-- [global] afplay Glass.aiff  Audio alert
    |
    v
PermissionRequest  (permission prompt appears)
    |
    v
ConfigChange  (config files change during session)
    |
    v
TeammateIdle / TaskCompleted  (Agent Teams events)
```

---

## 6. Tool Categories

All 22 native tools (+ 1 conditional) grouped by category with
permission indicators.

```
+-----------------------------------------------------------+
|          NATIVE TOOLS (22 + 1 conditional)                |
+-----------------------------------------------------------+
|                                                           |
|  FILE I/O                          Perm?                  |
|  --------                          -----                  |
|  Read ............................ no    (auto-allowed)    |
|  Edit ............................ YES                     |
|  Write ........................... YES                     |
|  NotebookEdit .................... YES                     |
|                                                           |
|  SEARCH                                                   |
|  ------                                                   |
|  Grep ............................ no    (auto-allowed)    |
|  Glob ............................ no    (auto-allowed)    |
|                                                           |
|  SHELL                                                    |
|  -----                                                    |
|  Bash ............................ conditional             |
|                                                           |
|  WEB                                                      |
|  ---                                                      |
|  WebFetch ........................ no    (auto-allowed)    |
|  WebSearch ....................... no    (auto-allowed)    |
|                                                           |
|  SUB-AGENT EXECUTION                                      |
|  -------------------                                      |
|  Task ............................ YES                     |
|  TaskStop ........................ no    (auto-allowed)    |
|  TaskOutput ...................... no    (auto-allowed)    |
|                                                           |
|  TASK MANAGEMENT                                          |
|  ---------------                                          |
|  TaskCreate ...................... no    (auto-allowed)    |
|  TaskGet ......................... no    (auto-allowed)    |
|  TaskUpdate ...................... no    (auto-allowed)    |
|  TaskList ........................ no    (auto-allowed)    |
|                                                           |
|  PLANNING                                                 |
|  --------                                                 |
|  EnterPlanMode ................... no                      |
|  ExitPlanMode .................... no                      |
|                                                           |
|  USER INTERACTION                                         |
|  ----------------                                         |
|  AskUserQuestion ................. no    (auto-allowed)    |
|                                                           |
|  WORKFLOW DISCOVERY                                       |
|  ------------------                                       |
|  Skill ........................... YES                     |
|                                                           |
|  GIT WORKTREE                                             |
|  -------------                                            |
|  EnterWorktree ................... YES                     |
|                                                           |
|  MCP                                                      |
|  ---                                                      |
|  mcp ............................. YES                     |
|  MCPSearch (conditional) ......... no    (auto-allowed)    |
|                                                           |
+-----------------------------------------------------------+
  YES = requires user permission
  no  = auto-allowed or no permission needed
  conditional = depends on command analysis
```

---

## 7. External CLI Tools (Capability Extensions)

Tools invoked via Bash that fill gaps in native tool coverage.
See [cli-tools-expanding-claude-code.md](cli-tools-expanding-claude-code.md)
for full analysis.

```
+-----------------------------------------------------------+
|           EXTERNAL CLI TOOLS (via Bash)                    |
+-----------------------------------------------------------+
|                                                            |
|  STRUCTURAL SEARCH          Installed?                     |
|  -----------------          ----------                     |
|  ast-grep .................. YES                           |
|                                                            |
|  SECURITY SCANNING                                         |
|  -----------------                                         |
|  semgrep ................... YES  (24s — use on demand)    |
|  gitleaks .................. YES                           |
|  shellcheck ................ YES                           |
|  bandit .................... YES                           |
|                                                            |
|  CODEBASE METRICS                                          |
|  ----------------                                          |
|  scc ....................... YES                           |
|                                                            |
|  BENCHMARKING                                              |
|  ------------                                              |
|  hyperfine ................. YES                           |
|                                                            |
+-----------------------------------------------------------+
  All invoked via Bash tool. Permission required.
  Check availability: command -v <tool>
```
