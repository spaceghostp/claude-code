#!/usr/bin/env python3
"""Stop hook: remind Claude to check for vault captures before ending.

Fires every time Claude finishes responding. Gates on session substance
to avoid noise — only blocks if the session is long enough (5+ assistant
turns) and no vault captures were already proposed.

No external dependencies — uses only Python stdlib.
"""

import json
import sys
from pathlib import Path


def should_block(hook_input):
    """Return a reason string if the session should be blocked, else None."""

    # Prevent infinite loops — if we already reminded, let Claude stop
    if hook_input.get("stop_hook_active", False):
        return None

    # Read transcript
    transcript_path = hook_input.get("transcript_path", "")
    if not transcript_path:
        return None

    path = Path(transcript_path).expanduser()
    if not path.is_file():
        return None

    try:
        messages = []
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    messages.append(json.loads(line))
    except (OSError, json.JSONDecodeError, UnicodeDecodeError):
        return None

    # Count assistant turns
    assistant_turns = sum(1 for m in messages if m.get("role") == "assistant")
    if assistant_turns < 5:
        return None

    # Check recent assistant messages for evidence of capture proposals
    assistant_msgs = [m for m in messages if m.get("role") == "assistant"]
    recent = assistant_msgs[-10:]  # Last ~10 assistant messages

    for msg in recent:
        content = msg.get("content", "")
        # Content can be a string or a list of content blocks
        if isinstance(content, list):
            text_parts = []
            for block in content:
                if isinstance(block, dict) and block.get("type") == "text":
                    text_parts.append(block.get("text", ""))
                elif isinstance(block, str):
                    text_parts.append(block)
            content = " ".join(text_parts)
        if not isinstance(content, str):
            continue

        # Capture-signals.md format: "**Vault:**" or vault-capture invocation
        if "Vault:" in content or "vault-capture" in content:
            return None

    return (
        "Before ending this session, review whether any insights "
        "match vault capture signals (vault/_meta/capture-signals.md). "
        "If nothing is vault-worthy, proceed to finish."
    )


def main():
    try:
        hook_input = json.load(sys.stdin)
    except (json.JSONDecodeError, EOFError):
        hook_input = {}

    reason = should_block(hook_input)
    if reason:
        print(json.dumps({"decision": "block", "reason": reason}))
    # No output + exit 0 = allow stop


if __name__ == "__main__":
    try:
        main()
    except Exception:
        # Never block session end on script failure
        sys.exit(0)
