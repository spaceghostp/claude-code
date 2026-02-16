#!/usr/bin/env python3
"""SessionStart hook: surface working notes from the cognitive vault.

Reads vault/_meta/index.json and scores notes from index data without
any per-file I/O. If the index is missing, prints a message to rebuild.

Small-vault short-circuit: if <8 notes, surfaces all without scoring.

No external dependencies — uses only Python stdlib.
"""

import json
import re
import sys
from datetime import datetime
from pathlib import Path


# ---------------------------------------------------------------------------
# Vault discovery
# ---------------------------------------------------------------------------

def find_vault_root():
    """Find the vault directory relative to the script or working directory."""
    script_dir = Path(__file__).resolve().parent
    vault_from_script = script_dir.parent / "vault"
    if (vault_from_script / "_meta" / "conventions.md").exists():
        return vault_from_script

    cwd = Path.cwd()
    vault_from_cwd = cwd / "vault"
    if (vault_from_cwd / "_meta" / "conventions.md").exists():
        return vault_from_cwd

    return None


# ---------------------------------------------------------------------------
# CWD keyword extraction
# ---------------------------------------------------------------------------

def cwd_keywords():
    """Extract lowercase keyword tokens from the current working directory name."""
    cwd_name = Path.cwd().name
    parts = re.split(r"[-_.\s]+", cwd_name)
    expanded = []
    for part in parts:
        expanded.extend(re.sub(r"([a-z])([A-Z])", r"\1 \2", part).split())
    return [w.lower() for w in expanded if len(w) > 1]


# ---------------------------------------------------------------------------
# Index-based scoring
# ---------------------------------------------------------------------------

def score_note_from_index(note_key, note_data, now, project_keywords):
    """Score a note using index data only. Returns (score, matched_keyword)."""
    lifecycle = note_data.get("lifecycle", "active")
    if lifecycle == "dormant":
        return -1, False

    status = note_data.get("status", "")
    score = 0

    # Status scoring
    if status == "working":
        score += 10
    if status == "unverified":
        score += 5

    # Link density from index
    links_out = note_data.get("links_out", [])
    score += min(len(links_out), 5)

    # Staleness
    last_touched = note_data.get("last_touched", "")
    days_since_touch = None
    try:
        touched_date = datetime.strptime(last_touched, "%Y-%m-%d")
        days_since_touch = (now - touched_date).days
        if days_since_touch > 60:
            score += 5
        elif days_since_touch > 30:
            score += 3
    except (ValueError, TypeError):
        pass

    # Recent capture bonus
    if days_since_touch is not None and days_since_touch <= 7:
        score += 3

    # Project-context keyword matching
    matched_keyword = False
    if project_keywords:
        keywords = [k.lower() for k in note_data.get("keywords", [])]
        matches = sum(1 for pk in project_keywords if pk in keywords)
        if matches > 0:
            matched_keyword = True
            score += min(matches * 2, 6)

    return score, matched_keyword


def pick_reasoning_tag(note_data, now, matched_keyword):
    """Select the single highest-priority reasoning tag for a note."""
    lifecycle = note_data.get("lifecycle", "")
    status = note_data.get("status", "")
    last_touched = note_data.get("last_touched", "")

    if lifecycle == "proposed":
        return "(proposed — unreviewed)"

    days_since_touch = None
    try:
        touched_date = datetime.strptime(last_touched, "%Y-%m-%d")
        days_since_touch = (now - touched_date).days
    except (ValueError, TypeError):
        pass

    if days_since_touch is not None and days_since_touch > 30:
        return "(stale — revisit?)"

    if matched_keyword:
        return "(matches project)"

    if status == "working":
        return "(working)"

    if days_since_touch is not None and days_since_touch <= 7:
        return "(recent)"

    return ""


# ---------------------------------------------------------------------------
# Main path
# ---------------------------------------------------------------------------

def surface_from_index(vault_root, now):
    """Surface notes using the index. Returns output dict or None."""
    index_path = vault_root / "_meta" / "index.json"
    try:
        with open(index_path, "r", encoding="utf-8") as f:
            index = json.load(f)
    except (OSError, json.JSONDecodeError, UnicodeDecodeError):
        return None  # Index missing or corrupt

    notes_map = index.get("notes")
    if not isinstance(notes_map, dict):
        return None

    project_kw = cwd_keywords()

    # Small-vault short-circuit: <8 notes → surface all (no scoring needed)
    small_vault = len(notes_map) < 8
    if small_vault:
        selected = []
        for key, data in notes_map.items():
            lifecycle = data.get("lifecycle", "active")
            if lifecycle != "dormant":
                matched_kw = False
                if project_kw:
                    keywords = [k.lower() for k in data.get("keywords", [])]
                    matched_kw = any(pk in keywords for pk in project_kw)
                selected.append((0, key, data, matched_kw))
    else:
        scored = []
        for key, data in notes_map.items():
            score, matched_kw = score_note_from_index(key, data, now, project_kw)
            if score > 0:
                scored.append((score, key, data, matched_kw))
        scored.sort(key=lambda x: x[0], reverse=True)
        selected = scored[:5]

    if not selected:
        return {}

    # --- Build output lines ---
    output_lines = []

    # Hard ceiling check
    proposed_count = sum(
        1 for d in notes_map.values() if d.get("lifecycle") == "proposed"
    )
    if proposed_count >= 10:
        output_lines.append(
            "\u26a0 10+ unreviewed vault notes. "
            "Vault capture paused until `/vault-maintain` runs.\n"
        )

    output_lines.append("## Vault Context \u2014 Working Notes\n")
    output_lines.append(
        "You have active notes in the cognitive vault. "
        "These were surfaced based on status and relevance.\n"
    )

    for _score, key, data, matched_kw in selected:
        title = data.get("title", key.split("/")[-1].replace("-", " ").title())
        note_type = data.get("type", "unknown")
        status = data.get("status", "unknown")
        tag = pick_reasoning_tag(data, now, matched_kw)

        display_path = "vault/" + key + ".md"
        tag_str = f" {tag}" if tag else ""

        output_lines.append(f"### {display_path}{tag_str}")
        output_lines.append(f"**Type:** {note_type} | **Status:** {status}")

        keywords = data.get("keywords", [])
        if keywords:
            output_lines.append(f"**Keywords:** {', '.join(keywords)}")

        links_out = data.get("links_out", [])
        links_in = data.get("links_in", [])
        if links_out or links_in:
            output_lines.append(
                f"**Links:** {len(links_out)} out, {len(links_in)} in"
            )

        output_lines.append("")

    # --- Maintenance threshold warnings ---
    last_maintained = index.get("last_maintained", "")
    notes_since = index.get("notes_since_maintenance", 0)

    days_since_maintained = None
    try:
        maintained_date = datetime.strptime(last_maintained, "%Y-%m-%d")
        days_since_maintained = (now - maintained_date).days
    except (ValueError, TypeError):
        pass

    threshold_exceeded = False
    if notes_since >= 5:
        threshold_exceeded = True
    if days_since_maintained is not None and days_since_maintained >= 7:
        threshold_exceeded = True
    if proposed_count >= 3:
        threshold_exceeded = True

    if threshold_exceeded:
        days_str = str(days_since_maintained) if days_since_maintained is not None else "?"
        output_lines.append(
            f"\u26a0 Vault maintenance recommended \u2014 "
            f"{proposed_count} proposed notes, last maintained {days_str} days ago. "
            f"Consider `/vault-maintain`."
        )

    output_lines.append("---")
    output_lines.append(
        "**Available vault skills:** "
        "`/vault-capture`, `/vault-maintain`"
    )

    context = "\n".join(output_lines)

    return {
        "hookSpecificOutput": {
            "hookEventName": "SessionStart",
            "additionalContext": context,
        }
    }


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    # Read stdin (hook input) — must consume it
    try:
        json.load(sys.stdin)
    except (json.JSONDecodeError, EOFError):
        pass

    vault_root = find_vault_root()
    if vault_root is None:
        print(json.dumps({}))
        sys.exit(0)

    now = datetime.now()

    result = surface_from_index(vault_root, now)

    if result is None:
        # Index missing — tell the session to rebuild
        msg = (
            "Vault index not found. Run `python3 scripts/build-index.py` "
            "to generate it."
        )
        result = {
            "hookSpecificOutput": {
                "hookEventName": "SessionStart",
                "additionalContext": msg,
            }
        }

    print(json.dumps(result))
    sys.exit(0)


if __name__ == "__main__":
    try:
        main()
    except Exception:
        # Never crash — SessionStart hooks must not block session start
        print(json.dumps({}))
        sys.exit(0)
