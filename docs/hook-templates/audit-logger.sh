#!/usr/bin/env bash
# Hook Template: PreToolUse Audit Logger
# Purpose: Log all tool invocations with timestamps, parameter hashes, and rotation
# Event: PreToolUse
# Pattern: Handles all tool calls; filter by tool_name if needed
#
# Usage: Copy to .claude/hooks/ and register in settings.json:
#   "hooks": {
#     "PreToolUse": [{ "command": ".claude/hooks/audit-logger.sh" }]
#   }
#
# Reads JSON from stdin with fields: tool_name, tool_input
# Writes JSONL to .claude/audit.jsonl with POSIX atomic locking

set -euo pipefail

# Configuration
AUDIT_FILE="${CLAUDE_PROJECT_DIR:-.}/.claude/audit.jsonl"
LOCK_DIR="${AUDIT_FILE}.lock"
MAX_SIZE=102400  # 100KB rotation threshold
MAX_LOCK_ATTEMPTS=10
LOCK_WAIT=0.1

# Ensure audit directory exists
mkdir -p "$(dirname "$AUDIT_FILE")"

# Read stdin (hook receives JSON payload)
INPUT=$(cat)

# Single-pass JSON extraction with timeout
ENTRY=$(python3 -c "
import json, hashlib, signal, sys, time

signal.alarm(5)  # 5-second timeout

try:
    data = json.load(sys.stdin)
    tool = data.get('tool_name', 'unknown')
    params = json.dumps(data.get('tool_input', {}), sort_keys=True)
    param_hash = hashlib.sha256(params.encode()).hexdigest()[:12]

    entry = json.dumps({
        'ts': time.strftime('%Y-%m-%dT%H:%M:%S%z'),
        'tool': tool,
        'param_hash': param_hash,
        'param_size': len(params)
    })
    print(entry)
except Exception as e:
    # Graceful degradation: log the error, don't block the agent
    print(json.dumps({
        'ts': time.strftime('%Y-%m-%dT%H:%M:%S%z'),
        'tool': 'parse_error',
        'error': str(e)[:100]
    }))
" <<< "$INPUT" 2>/dev/null) || exit 0

# POSIX atomic locking via mkdir
acquired=0
for i in $(seq 1 $MAX_LOCK_ATTEMPTS); do
    if mkdir "$LOCK_DIR" 2>/dev/null; then
        acquired=1
        # Ensure lock is removed on exit
        trap 'rmdir "$LOCK_DIR" 2>/dev/null' EXIT
        break
    fi
    sleep "$LOCK_WAIT"
done

# Graceful degradation: if lock unavailable, skip logging (don't block agent)
if [ "$acquired" -eq 0 ]; then
    exit 0
fi

# Rotation check
if [ -f "$AUDIT_FILE" ] && [ "$(wc -c < "$AUDIT_FILE" 2>/dev/null || echo 0)" -gt "$MAX_SIZE" ]; then
    mv "$AUDIT_FILE" "${AUDIT_FILE}.$(date +%Y%m%d%H%M%S).bak"
fi

# Append entry
echo "$ENTRY" >> "$AUDIT_FILE"

# Lock released by trap
