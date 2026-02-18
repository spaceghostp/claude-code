# cli-tools Plugin

External CLI tool integration for Claude Code. Provides skills for
security scanning and codebase metrics, plus a PostToolUse hook for
advisory shell file linting.

## Components

### Skills

- **`/security-scan`** — Run installed security tools (shellcheck,
  bandit, gitleaks, semgrep) with fast-first ordering
- **`/codebase-metrics`** — Run `scc` for LOC, complexity, and
  COCOMO estimates

### Hooks

- **PostToolUse (Edit|Write)** — Advisory shellcheck on shell files.
  Runs after edits to `.sh`, `.bash`, `.zsh`, `.bats` files. Never
  blocks (exit 0 always). Requires shellcheck to be installed.

## Requirements

Tools are checked at runtime. Missing tools are reported, not
errors. Install via:

```bash
brew install shellcheck ast-grep scc hyperfine gitleaks
pip install bandit semgrep
```

## Related Docs

- `docs/cli-tools-that-outperform-claude-code.md`
- `docs/cli-tools-expanding-claude-code.md`
