#!/usr/bin/env python3
"""Batch-create vault notes from the claims selection."""

import json
import os
import textwrap
from datetime import date

SELECTIONS_PATH = "/Users/coppervessel/Desktop/WS-000-03/scripts/vault-note-selections.json"
VAULT_ROOT = os.path.expanduser("~/.claude/vault")
TODAY = "2026-02-18"


def vault_type_to_dir(vault_type):
    return {
        "encounter": "encounters",
        "atom": "atoms",
        "anti-library": "anti-library",
    }[vault_type]


def make_frontmatter(vault_type):
    return textwrap.dedent(f"""\
    ---
    type: {vault_type}
    status: unverified
    lifecycle: proposed
    created: {TODAY}
    last_touched: {TODAY}
    links_out: 0
    origin: youtube
    ---
    """)


def make_links_section(links_to):
    lines = ["## Links", ""]
    for link in links_to:
        lines.append(f"- [[{link}]]")
    return "\n".join(lines)


def make_note_content(selection):
    vault_type = selection["vault_type"]
    title = selection["claim_title"]
    content = selection["content_full"]
    links = selection["links_to"]
    rationale = selection["rationale"]

    fm = make_frontmatter(vault_type)

    # Build the note body based on type
    if vault_type == "encounter":
        body = textwrap.dedent(f"""\
        # {title}

        #status/unverified — Extracted from WS-000-02 YouTube corpus, not yet validated in practice.

        ## What Happened

        {content}

        ## Why This Matters

        {rationale}

        {make_links_section(links)}
        """)
    elif vault_type == "atom":
        body = textwrap.dedent(f"""\
        # {title}

        #status/unverified — Extracted from WS-000-02 YouTube corpus, cross-video validated but not yet tested.

        ## The Concept

        {content}

        ## Vault Relevance

        {rationale}

        {make_links_section(links)}
        """)
    elif vault_type == "anti-library":
        body = textwrap.dedent(f"""\
        # {title}

        #status/unverified — Assumption extracted from WS-000-02, not yet tested.

        ## The Assumption

        {content}

        ## What Would Falsify This

        {rationale}

        {make_links_section(links)}
        """)
    else:
        raise ValueError(f"Unknown vault type: {vault_type}")

    return fm + body


def main():
    with open(SELECTIONS_PATH) as f:
        selections = json.load(f)

    created = []
    for sel in selections:
        vault_type = sel["vault_type"]
        filename = sel["vault_filename"]
        dir_name = vault_type_to_dir(vault_type)
        dir_path = os.path.join(VAULT_ROOT, dir_name)
        file_path = os.path.join(dir_path, filename)

        # Don't overwrite existing notes
        if os.path.exists(file_path):
            print(f"  SKIP (exists): {dir_name}/{filename}")
            continue

        content = make_note_content(sel)

        # Count links
        link_count = len(sel["links_to"])
        content = content.replace("links_out: 0", f"links_out: {link_count}")

        with open(file_path, "w") as f:
            f.write(content)

        created.append(f"{dir_name}/{filename}")
        print(f"  CREATED: {dir_name}/{filename}")

    print(f"\n{'='*50}")
    print(f"Created {len(created)} vault notes")
    print(f"Skipped {len(selections) - len(created)} (already exist)")

    return created


if __name__ == "__main__":
    created = main()
