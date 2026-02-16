---
type: atom
status: unverified
lifecycle: proposed
created: 2026-02-16
last_touched: 2026-02-16
links_out: 1
origin: session
---

# Claude Code Hook Schema

#status/unverified — Verified for project-level settings.json. Plugin format differs.

## The Concept

Claude Code hooks are registered in `.claude/settings.json` under a top-level `"hooks"` key. Each hook event maps to an array of hook definitions.

## Project-Level Format (`.claude/settings.json`)

```json
{
  "hooks": {
    "SessionStart": [
      {
        "type": "command",
        "command": "python3 scripts/resurface.py",
        "timeout": 10
      }
    ],
    "SessionEnd": [
      {
        "type": "command",
        "command": "python3 scripts/build-index.py",
        "timeout": 30
      }
    ]
  }
}
```

## Key Details

- **Hook types:** `"command"` (shell script, deterministic) or `"prompt"` (LLM reasoning, for PreToolUse/PostToolUse/Stop)
- **stdin:** Hooks receive JSON on stdin. Scripts must consume it even if unused.
- **stdout:** Command hooks return JSON: `{"hookSpecificOutput": {"hookEventName": "...", "additionalContext": "..."}}`
- **Exit codes:** 0 = success, 2 = blocking error
- **Timeout defaults:** 60s for command, 30s for prompt
- **Plugin format differs:** Plugins use a nested structure with `"matcher"` fields and a wrapping `"hooks"` object. Don't mix formats.

## Gotcha

`build-index.py` originally didn't read stdin. When registered as a SessionEnd hook, it would hang waiting for stdin to close. Fix: consume stdin at the top of `main()`.

## Links

- [[encounters/2026-02-14-designing-the-cognitive-vault]] — Session where hooks were first designed
