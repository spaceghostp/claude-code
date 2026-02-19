#!/usr/bin/env python3
"""
WS-000-02 REFERENCE IMPLEMENTATION — Not directly compatible with the cognitive vault
at ~/.claude/vault/. This script expects a notes/ subdirectory with Obsidian-style
frontmatter. The cognitive vault uses atoms/, encounters/, positions/, etc.
Adapt load paths and frontmatter parsing if porting to cognitive vault.

Vault SQLite Indexer — build a complementary search index from Obsidian vault notes.

Parses YAML frontmatter from all markdown notes and indexes them into a SQLite
database for fast structured queries. The vault markdown files remain the source
of truth; the SQLite database is a derived, regenerable index.

Usage:
    python3 scripts/vault_indexer.py vault/           # full rebuild
    python3 scripts/vault_indexer.py vault/ --db vault-data/vault.db

Output:
    vault.db (or specified path) with tables: notes, note_tags, notes_fts
"""

import json
import re
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path


# ---------------------------------------------------------------------------
# Schema
# ---------------------------------------------------------------------------

SCHEMA = """
CREATE TABLE IF NOT EXISTS notes (
    id TEXT PRIMARY KEY,
    type TEXT NOT NULL,
    title TEXT NOT NULL,
    summary TEXT,
    source TEXT,
    created TEXT,
    filepath TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS note_tags (
    note_id TEXT NOT NULL REFERENCES notes(id) ON DELETE CASCADE,
    tag TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_type ON notes(type);
CREATE INDEX IF NOT EXISTS idx_source ON notes(source);
CREATE INDEX IF NOT EXISTS idx_created ON notes(created);
CREATE INDEX IF NOT EXISTS idx_tag ON note_tags(tag);
CREATE INDEX IF NOT EXISTS idx_note_id ON note_tags(note_id);

-- Full-text search
CREATE VIRTUAL TABLE IF NOT EXISTS notes_fts USING fts5(
    id, title, summary, type,
    content='notes',
    content_rowid='rowid'
);

-- Triggers to keep FTS in sync
CREATE TRIGGER IF NOT EXISTS notes_ai AFTER INSERT ON notes BEGIN
    INSERT INTO notes_fts(rowid, id, title, summary, type)
    VALUES (new.rowid, new.id, new.title, new.summary, new.type);
END;

CREATE TRIGGER IF NOT EXISTS notes_ad AFTER DELETE ON notes BEGIN
    INSERT INTO notes_fts(notes_fts, rowid, id, title, summary, type)
    VALUES ('delete', old.rowid, old.id, old.title, old.summary, old.type);
END;

CREATE TRIGGER IF NOT EXISTS notes_au AFTER UPDATE ON notes BEGIN
    INSERT INTO notes_fts(notes_fts, rowid, id, title, summary, type)
    VALUES ('delete', old.rowid, old.id, old.title, old.summary, old.type);
    INSERT INTO notes_fts(rowid, id, title, summary, type)
    VALUES (new.rowid, new.id, new.title, new.summary, new.type);
END;
"""


# ---------------------------------------------------------------------------
# Frontmatter parsing
# ---------------------------------------------------------------------------

def parse_frontmatter(content: str) -> dict:
    """Parse YAML frontmatter from markdown content."""
    if not content.startswith('---'):
        return {}

    end_match = re.search(r'\n---\n', content[3:])
    if not end_match:
        return {}

    fm_str = content[4:end_match.start() + 3]
    fm = {}

    for line in fm_str.split('\n'):
        if ':' not in line:
            continue
        key, value = line.split(':', 1)
        key = key.strip()
        value = value.strip()

        if value.startswith('"') and value.endswith('"'):
            value = value[1:-1]
        elif value.startswith('[') and value.endswith(']'):
            # Parse inline YAML array
            value = [v.strip().strip('"\'') for v in value[1:-1].split(',') if v.strip()]

        fm[key] = value

    return fm


# ---------------------------------------------------------------------------
# Indexing
# ---------------------------------------------------------------------------

def index_vault(vault_path: str, db_path: str) -> dict:
    """Index all vault notes into SQLite. Returns stats dict."""
    vault = Path(vault_path)
    notes_dir = vault / 'notes'

    if not notes_dir.exists():
        print(f"Error: {notes_dir} not found", file=sys.stderr)
        sys.exit(1)

    # Connect and create schema
    db = sqlite3.connect(db_path)
    db.execute("PRAGMA journal_mode=WAL")
    db.execute("PRAGMA foreign_keys=ON")
    db.executescript(SCHEMA)

    # Clear existing data for full rebuild
    db.execute("DELETE FROM note_tags")
    db.execute("DELETE FROM notes")

    stats = {'indexed': 0, 'skipped': 0, 'errors': 0, 'tags': 0}

    # Index notes (recursive to handle subdirectories)
    for md_file in sorted(notes_dir.glob('**/*.md')):
        try:
            content = md_file.read_text(encoding='utf-8')
            fm = parse_frontmatter(content)

            if not fm.get('id') or not fm.get('type') or not fm.get('title'):
                stats['skipped'] += 1
                continue

            filepath = str(md_file.relative_to(vault))

            db.execute(
                "INSERT OR REPLACE INTO notes (id, type, title, summary, source, created, filepath) "
                "VALUES (?, ?, ?, ?, ?, ?, ?)",
                (
                    fm['id'],
                    fm['type'],
                    fm['title'],
                    fm.get('summary', ''),
                    fm.get('source', ''),
                    fm.get('created', ''),
                    filepath,
                )
            )

            # Index tags
            tags = fm.get('tags', [])
            if isinstance(tags, list):
                for tag in tags:
                    if tag:
                        db.execute(
                            "INSERT INTO note_tags (note_id, tag) VALUES (?, ?)",
                            (fm['id'], tag)
                        )
                        stats['tags'] += 1

            stats['indexed'] += 1

        except Exception as e:
            stats['errors'] += 1
            print(f"  Error indexing {md_file.name}: {e}", file=sys.stderr)

    # Also index sources and MOCs
    for extra_dir in ['sources', 'mocs']:
        extra_path = vault / extra_dir
        if not extra_path.exists():
            continue
        for md_file in sorted(extra_path.glob('*.md')):
            try:
                content = md_file.read_text(encoding='utf-8')
                fm = parse_frontmatter(content)
                note_id = fm.get('id', md_file.stem)
                note_type = fm.get('type', extra_dir.rstrip('s'))
                title = fm.get('title', md_file.stem)
                filepath = str(md_file.relative_to(vault))

                db.execute(
                    "INSERT OR REPLACE INTO notes (id, type, title, summary, source, created, filepath) "
                    "VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (note_id, note_type, title, fm.get('summary', ''),
                     fm.get('source', ''), fm.get('created', ''), filepath)
                )

                tags = fm.get('tags', [])
                if isinstance(tags, list):
                    for tag in tags:
                        if tag:
                            db.execute(
                                "INSERT INTO note_tags (note_id, tag) VALUES (?, ?)",
                                (note_id, tag)
                            )
                            stats['tags'] += 1

                stats['indexed'] += 1
            except Exception as e:
                stats['errors'] += 1

    db.commit()

    # Record index metadata
    db.execute("""
        CREATE TABLE IF NOT EXISTS _meta (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    """)
    now = datetime.now(timezone.utc).isoformat()
    db.execute("INSERT OR REPLACE INTO _meta VALUES ('last_indexed', ?)", (now,))
    db.execute("INSERT OR REPLACE INTO _meta VALUES ('vault_path', ?)", (str(vault.resolve()),))
    db.execute("INSERT OR REPLACE INTO _meta VALUES ('note_count', ?)", (str(stats['indexed']),))
    db.commit()
    db.close()

    return stats


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 scripts/vault_indexer.py <vault_path> [--db <db_path>]")
        sys.exit(1)

    vault_path = sys.argv[1]

    # Parse --db flag
    db_path = str(Path(vault_path).parent / 'vault.db')
    if '--db' in sys.argv:
        idx = sys.argv.index('--db')
        if idx + 1 < len(sys.argv):
            db_path = sys.argv[idx + 1]

    print(f"Indexing vault: {vault_path}")
    print(f"Database: {db_path}")

    stats = index_vault(vault_path, db_path)

    print(f"\nDone:")
    print(f"  Indexed: {stats['indexed']} notes")
    print(f"  Tags:    {stats['tags']} tag entries")
    print(f"  Skipped: {stats['skipped']}")
    print(f"  Errors:  {stats['errors']}")

    # Show DB size
    db_size = Path(db_path).stat().st_size
    print(f"  DB size: {db_size / 1024:.0f} KB")

    # Quick verification
    db = sqlite3.connect(db_path)
    count = db.execute("SELECT COUNT(*) FROM notes").fetchone()[0]
    type_counts = db.execute(
        "SELECT type, COUNT(*) FROM notes GROUP BY type ORDER BY COUNT(*) DESC"
    ).fetchall()
    print(f"\nVerification — {count} total records:")
    for t, c in type_counts:
        print(f"  {t}: {c}")
    db.close()


if __name__ == '__main__':
    main()
