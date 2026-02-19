# Release Notes — February 2026

## Claude Code v2.1.37 (February 7, 2026)

**Released by:** @ashwin-ant

### Bug Fixes

- **Fast Mode Availability Fix** — Fixed `/fast` not immediately available after enabling `/extra-usage`.

**Source:** [ClaudeWorld](https://claude-world.com/articles/claude-code-2137-release/)

---

## Claude Code v2.1.36 (February 6, 2026)

**Released by:** @ashwin-ant

### New Features

- **Fast Mode for Opus 4.6** — Fast mode is now available for Claude Opus 4.6, providing faster output with the same model quality. Toggle with `/fast`.

**Documentation:** [Fast Mode Guide](https://code.claude.com/docs/en/fast-mode)

**Source:** [GitHub Releases](https://github.com/anthropics/claude-code/releases)

---

## Claude Code v2.1.34 (February 6, 2026)

**Released by:** @ashwin-ant

### Bug Fixes

- **Agent Teams Render Fix** — Fixed crash when agent teams setting changed between renders.
- **Sandbox Security Fix** — Fixed security issue where commands excluded from sandboxing (via `sandbox.excludedCommands` or `dangerouslyDisableSandbox`) could bypass the Bash ask permission rule when `autoAllowBashIfSandboxed` was enabled.

**Source:** [GitHub Release v2.1.34](https://github.com/anthropics/claude-code/releases/tag/v2.1.34)

---

## Claude Code v2.1.33 (February 6, 2026)

**Released by:** @ashwin-ant

### New Features

- **`TeammateIdle` and `TaskCompleted` Hook Events** — New hook event types for multi-agent workflows. `TeammateIdle` fires when a teammate agent becomes idle; `TaskCompleted` fires when a spawned task finishes.
- **`Task(agent_type)` Restriction Syntax** — Agent `tools` frontmatter can now restrict which sub-agent types are spawnable using `Task(agent_type)` syntax (e.g., `Task(Bash)`, `Task(Explore)`), enforcing least-privilege on sub-agent spawning.
- **Agent `memory` Frontmatter Field** — Agents can declare persistent memory with `user`, `project`, or `local` scope, enabling cross-session state without manual memory management.
- **Plugin Name in Skill Descriptions** — Plugin name is now shown in skill descriptions and the `/skills` menu for better discoverability.

### Bug Fixes

- **Agent Teams tmux Fix** — Fixed teammate sessions in tmux to correctly send and receive messages.
- **Agent Teams Plan Availability Warning** — Fixed warnings about agent teams not being available on the current plan.
- **Extended Thinking Interruption Fix** — Fixed an issue where submitting a new message while the model was in extended thinking would interrupt the thinking phase.
- **API Streaming Abort Fix** — Fixed an API error where whitespace text combined with a thinking block would bypass normalization and produce an invalid request when aborting mid-stream.
- **API Proxy 404 Fix** — 404 errors on streaming endpoints no longer trigger a non-streaming fallback for API proxy compatibility.
- **Proxy Settings via Environment Variables** — Fixed proxy settings configured via `settings.json` environment variables not being applied to WebFetch and other HTTP requests on the Node.js build.
- **`/resume` Session Picker Fix** — Fixed session picker showing raw XML markup instead of clean titles for sessions started with slash commands.

### Improvements

- Invalid managed settings errors are now surfaced to users.
- Improved error messages for API connection failures — now shows specific cause (e.g., ECONNREFUSED, SSL errors) instead of generic "Connection error."

### VSCode Extension

- Added support for remote sessions, allowing OAuth users to browse and resume sessions from claude.ai.
- Added git branch and message count to the session picker, with support for searching by branch name.
- Fixed scroll-to-bottom under-scrolling on initial session load and session switch.

---

## Claude Code v2.1.31 (February 3, 2026)

**Released by:** @ashwin-ant
**Commit:** `bd78b216ed563e57767901dcdd80f9a7750434c9`

### New Features

- **Session Resume Hint on Exit** — When you exit a session, Claude Code now shows a hint explaining how to continue/resume your conversation later.
- **Japanese IME Full-Width Space Support** — Added support for full-width (zenkaku) space input from Japanese IME in checkbox selection interfaces.

### Bug Fixes

- **PDF Size Lock Fix** — Fixed an issue where PDF-too-large errors permanently locked up sessions, requiring users to start a new conversation.
- **Sandbox Mode "Read-only file system" Fix** — Fixed bash commands incorrectly reporting failure with "Read-only file system" errors when sandbox mode was enabled.
- **Plan Mode Crash Fix** — Fixed a crash that made sessions unusable after entering plan mode when the project config in `~/.claude.json` was missing default fields.
- **Temperature Override Fix** — Fixed `temperatureOverride` being silently ignored in the streaming API path, which caused all streaming requests to use the default temperature (1) regardless of the configured override.
- **LSP Shutdown/Exit Compatibility** — Fixed LSP shutdown/exit compatibility with strict language servers that reject null params.

### Improvements

- Improved system prompts to guide the model toward using dedicated tools (Read, Edit, Glob, Grep) instead of bash equivalents (`cat`, `sed`, `grep`, `find`).
- Improved PDF and request size error messages to show actual limits (100 pages, 20MB).
- Reduced layout jitter in the terminal when the spinner appears and disappears during streaming.
- Removed misleading Anthropic API pricing from the model selector for third-party provider (Bedrock, Vertex, Foundry) users.

### Known Issues

- Verbose mode does not display thinking blocks — regression from prior version ([Issue #22977](https://github.com/anthropics/claude-code/issues/22977)).

---

## Claude Opus 4.6 (February 5, 2026)

**Model ID:** `claude-opus-4-6`

### Specifications

| Spec | Value |
|------|-------|
| Context Window | 200K (default), 1M tokens (beta) |
| Max Output Tokens | 128K (doubled from 64K) |
| Pricing | $5 input / $25 output per million tokens |
| US-only inference | 1.1x price multiplier via `inference_geo: "us"` |

### Key New Features

1. **Adaptive Thinking** — `thinking: {type: "adaptive"}` is the recommended thinking mode. Claude dynamically decides when and how much to think based on the problem. A new `max` effort level provides the highest capability. The previous `thinking: {type: "enabled"}` with `budget_tokens` is deprecated.

2. **1M Token Context Window (Beta)** — First Opus model to support one million token context. Scores 76% on MRCR v2 at 1M tokens (vs. 18.5% for Sonnet 4.5).

3. **128K Output Tokens** — Output capacity doubled from 64K to 128K tokens. Streaming is required for large `max_tokens` values.

4. **Compaction API (Beta)** — Server-side context summarization enabling effectively infinite conversations. When context approaches the window limit, the API automatically summarizes earlier parts.

5. **Agent Teams (Claude Code)** — Research preview enabling multiple AI agents to work simultaneously on different aspects of a coding project, coordinating autonomously.

6. **Data Residency Controls** — New `inference_geo` parameter specifies where model inference runs (`"global"` or `"us"` per request).

7. **Fine-grained Tool Streaming (GA)** — Generally available on all models with no beta header required.

### Benchmark Performance

| Benchmark | Opus 4.6 | Previous Best |
|-----------|----------|---------------|
| Terminal-Bench 2.0 (agentic coding) | 65.4% | 59.8% (Opus 4.5) |
| GDPval-AA (professional tasks) | 1606 Elo | +144 over GPT-5.2 |
| OSWorld (agentic computer use) | 72.7% | 66.3% (Opus 4.5) |
| MRCR v2 (1M token retrieval) | 76% | 18.5% (Sonnet 4.5) |
| Legal reasoning | 90.2% | — |

### Breaking Changes

- **Prefilling assistant messages** is not supported. Requests with prefilled assistant messages return a 400 error. Use structured outputs or system prompt instructions instead.
- **`thinking: {type: "enabled"}` and `budget_tokens`** are deprecated. Migrate to `thinking: {type: "adaptive"}`.
- **`interleaved-thinking-2025-05-14` beta header** is deprecated. Adaptive thinking automatically enables interleaved thinking.
- **`output_format` parameter** moved to `output_config.format`.
- **Tool parameter quoting** may produce slightly different JSON string escaping in tool call arguments.

### Sources

- [Introducing Claude Opus 4.6 — Anthropic](https://www.anthropic.com/news/claude-opus-4-6)
- [What's new in Claude 4.6 — Claude API Docs](https://platform.claude.com/docs/en/about-claude/models/whats-new-claude-4-6)
- [Claude Code v2.1.31 — GitHub Releases](https://github.com/anthropics/claude-code/releases/tag/v2.1.31)
