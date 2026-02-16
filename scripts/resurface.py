#!/usr/bin/env python3
"""SessionStart hook: surface working notes from the cognitive vault.

Primary path: reads vault/_meta/index.json and scores notes from index data
without any per-file I/O. Falls back to file-scanning if the index is missing
or corrupt.

Surfaces up to 5 notes with reasoning tags and maintenance threshold warnings.

No external dependencies — uses only Python stdlib.
"""

import json
import os
import re
import sys
from datetime import datetime, timedelta
from pathlib import Path


# ---------------------------------------------------------------------------
# Vault discovery
# ---------------------------------------------------------------------------

def find_vault_root():
    """Find the vault directory relative to the script or working directory."""
    # Try sibling to script's parent (scripts/ and vault/ are siblings at repo root)
    script_dir = Path(__file__).resolve().parent
    vault_from_script = script_dir.parent / "vault"
    if (vault_from_script / "_meta" / "conventions.md").exists():
        return vault_from_script

    # Try working directory
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
    # Split on common separators: hyphens, underscores, dots, camelCase boundaries
    parts = re.split(r"[-_.\s]+", cwd_name)
    # Further split camelCase
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

    # Link density from index (no file I/O)
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
        matches = 0
        for pk in project_keywords:
            if pk in keywords:
                matches += 1
        if matches > 0:
            matched_keyword = True
            score += min(matches * 2, 6)

    return score, matched_keyword


def reasoning_tag(note_data, now):
    """Return the single highest-priority reasoning tag string for a note."""
    lifecycle = note_data.get("lifecycle", "")
    status = note_data.get("status", "")
    last_touched = note_data.get("last_touched", "")

    # Priority order: proposed > stale > matches project > working > recent
    if lifecycle == "proposed":
        return "(proposed \u2014 unreviewed)"

    days_since_touch = None
    try:
        touched_date = datetime.strptime(last_touched, "%Y-%m-%d")
        days_since_touch = (now - touched_date).days
    except (ValueError, TypeError):
        pass

    if days_since_touch is not None and days_since_touch > 30:
        return "(stale \u2014 revisit?)"

    # Project-match tag is checked by caller since it needs keyword info
    # — handled via the matched_keyword flag returned alongside score.
    # We return a sentinel so caller can override.
    return None  # Caller fills in project/working/recent


def pick_reasoning_tag(note_data, now, matched_keyword):
    """Full reasoning tag selection including keyword match context."""
    tag = reasoning_tag(note_data, now)
    if tag is not None:
        return tag

    if matched_keyword:
        return "(matches project)"

    status = note_data.get("status", "")
    if status == "working":
        return "(working)"

    last_touched = note_data.get("last_touched", "")
    try:
        touched_date = datetime.strptime(last_touched, "%Y-%m-%d")
        if (now - touched_date).days <= 7:
            return "(recent)"
    except (ValueError, TypeError):
        pass

    return ""


# ---------------------------------------------------------------------------
# Index-based main path
# ---------------------------------------------------------------------------

def surface_from_index(vault_root, now):
    """Try to surface notes using the index. Returns output dict or None."""
    index_path = vault_root / "_meta" / "index.json"
    try:
        with open(index_path, "r", encoding="utf-8") as f:
            index = json.load(f)
    except (OSError, json.JSONDecodeError, UnicodeDecodeError):
        return None  # Fall back to file scanning

    notes_map = index.get("notes")
    if not isinstance(notes_map, dict):
        return None

    project_kw = cwd_keywords()

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

        # Show keywords if present
        keywords = data.get("keywords", [])
        if keywords:
            output_lines.append(f"**Keywords:** {', '.join(keywords)}")

        # Show link summary
        links_out = data.get("links_out", [])
        links_in = data.get("links_in", [])
        if links_out or links_in:
            output_lines.append(
                f"**Links:** {len(links_out)} out, {len(links_in)} in"
            )

        output_lines.append("")  # blank line between notes

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
        "`/vault-capture`, `/vault-maintain`, `/vault-reflect`, `/vault-falsify`"
    )

    context = "\n".join(output_lines)

    return {
        "hookSpecificOutput": {
            "hookEventName": "SessionStart",
            "additionalContext": context,
        }
    }


# ---------------------------------------------------------------------------
# Fallback: file-scanning approach (original logic)
# ---------------------------------------------------------------------------

def parse_frontmatter(filepath):
    """Parse YAML frontmatter from a markdown file. Returns dict or None."""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            lines = f.readlines()
    except (OSError, UnicodeDecodeError):
        return None

    if not lines or lines[0].strip() != "---":
        return None

    frontmatter = {}
    body_lines = []
    in_frontmatter = True
    found_end = False

    for i, line in enumerate(lines[1:], start=1):
        if in_frontmatter:
            if line.strip() == "---":
                in_frontmatter = False
                found_end = True
                continue
            if ":" in line:
                key, _, value = line.partition(":")
                frontmatter[key.strip()] = value.strip()
        else:
            stripped = line.strip()
            if not stripped or stripped.startswith("```") or stripped == "---":
                continue
            if stripped.startswith("# ") and not stripped.startswith("## "):
                continue
            body_lines.append(stripped)
            if len(body_lines) >= 5:
                break

    if not found_end:
        return None

    frontmatter["_body_preview"] = "\n".join(body_lines[:5])
    frontmatter["_path"] = str(filepath)
    return frontmatter


def score_note_fallback(fm, now):
    """Score a note for resurfacing (file-scanning fallback). Higher = more relevant."""
    score = 0
    status = fm.get("status", "")
    note_type = fm.get("type", "")

    if note_type == "meta":
        return -1

    if status == "working":
        score += 10
    if status == "unverified":
        score += 5

    try:
        with open(fm["_path"], "r", encoding="utf-8") as f:
            content = f.read()
        links_out = len(re.findall(r"\[\[", content))
        score += min(links_out, 5)
    except (OSError, KeyError):
        pass

    last_touched = fm.get("last_touched", "")
    try:
        touched_date = datetime.strptime(last_touched, "%Y-%m-%d")
        days_stale = (now - touched_date).days
        if days_stale > 30:
            score += 3
        if days_stale > 60:
            score += 2
    except (ValueError, TypeError):
        pass

    return score


def surface_from_files(vault_root, now):
    """Fallback: scan vault files and surface top 5 notes."""
    notes = []

    for md_file in vault_root.rglob("*.md"):
        rel = md_file.relative_to(vault_root)
        parts = rel.parts
        if any(p.startswith(".") for p in parts):
            continue
        if parts[0] in ("scripts", "_meta"):
            continue

        fm = parse_frontmatter(md_file)
        if fm is None:
            continue

        score = score_note_fallback(fm, now)
        if score > 0:
            notes.append((score, fm))

    notes.sort(key=lambda x: x[0], reverse=True)
    selected = notes[:5]

    if not selected:
        return {}

    lines = ["## Vault Context \u2014 Working Notes\n"]
    lines.append(
        "You have active notes in the cognitive vault. "
        "These were surfaced based on status and relevance.\n"
    )

    for _, fm in selected:
        rel_path = os.path.relpath(fm["_path"], vault_root.parent)
        status = fm.get("status", "unknown")
        note_type = fm.get("type", "unknown")
        preview = fm.get("_body_preview", "").strip()

        lines.append(f"### {rel_path}")
        lines.append(f"**Type:** {note_type} | **Status:** {status}\n")
        if preview:
            lines.append(f"{preview}\n")

    lines.append("---")
    lines.append(
        "**Available vault skills:** "
        "`/vault-capture`, `/vault-maintain`, `/vault-reflect`, `/vault-falsify`"
    )

    context = "\n".join(lines)

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
    # Read stdin (hook input) — we don't need it but must consume it
    try:
        json.load(sys.stdin)
    except (json.JSONDecodeError, EOFError):
        pass

    vault_root = find_vault_root()
    if vault_root is None:
        print(json.dumps({}))
        sys.exit(0)

    now = datetime.now()

    # Primary path: index-based scoring
    result = surface_from_index(vault_root, now)

    # Fallback: file-scanning if index unavailable
    if result is None:
        result = surface_from_files(vault_root, now)

    print(json.dumps(result))
    sys.exit(0)


if __name__ == "__main__":
    try:
        main()
    except Exception:
        # Never crash — SessionStart hooks must not block session start
        print(json.dumps({}))
        sys.exit(0)
