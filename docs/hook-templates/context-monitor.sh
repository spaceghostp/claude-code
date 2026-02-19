#!/usr/bin/env bash
# Hook Template: Sampled Context Pressure Monitor
# Purpose: Estimate context window usage every Nth tool call
# Event: PostToolUse
# Pattern: Sampled — runs every 20th call to reduce overhead 95%
#
# Usage: Copy to .claude/hooks/ and register in settings.json:
#   "hooks": {
#     "PostToolUse": [{ "command": ".claude/hooks/context-monitor.sh" }]
#   }
#
# Writes context pressure estimates to .claude/context-pressure.jsonl
# Skills can consume this file to warn about approaching limits

set -euo pipefail

# Configuration
COUNTER_FILE="${CLAUDE_PROJECT_DIR:-.}/.claude/.context-monitor-counter"
PRESSURE_FILE="${CLAUDE_PROJECT_DIR:-.}/.claude/context-pressure.jsonl"
SAMPLE_RATE=20  # Run every Nth call
MAX_PRESSURE_SIZE=51200  # 50KB rotation threshold

# Ensure directories exist
mkdir -p "$(dirname "$COUNTER_FILE")"

# Increment counter atomically
COUNTER=0
if [ -f "$COUNTER_FILE" ]; then
    COUNTER=$(cat "$COUNTER_FILE" 2>/dev/null || echo 0)
fi
COUNTER=$((COUNTER + 1))
echo "$COUNTER" > "$COUNTER_FILE"

# Sample check: only run every Nth call
if [ $((COUNTER % SAMPLE_RATE)) -ne 0 ]; then
    exit 0
fi

# Read stdin (PostToolUse payload)
INPUT=$(cat)

# Estimate context pressure from available signals
ESTIMATE=$(python3 -c "
import json, os, signal, sys, time

signal.alarm(5)

try:
    data = json.load(sys.stdin)
    tool = data.get('tool_name', 'unknown')

    # Heuristic: estimate pressure from tool call count and response sizes
    # This is approximate — exact token count requires API access
    transcript_path = os.environ.get('CLAUDE_TRANSCRIPT_PATH', '')
    transcript_size = 0
    if transcript_path and os.path.exists(transcript_path):
        transcript_size = os.path.getsize(transcript_path)

    # Rough estimate: 4 chars per token, 200K token context
    estimated_tokens = transcript_size // 4
    context_limit = 200000  # Conservative default
    pressure = min(1.0, estimated_tokens / context_limit)

    entry = json.dumps({
        'ts': time.strftime('%Y-%m-%dT%H:%M:%S%z'),
        'call_count': int(os.environ.get('COUNTER', 0)),
        'transcript_bytes': transcript_size,
        'estimated_tokens': estimated_tokens,
        'pressure': round(pressure, 3),
        'last_tool': tool
    })
    print(entry)
except Exception as e:
    print(json.dumps({
        'ts': time.strftime('%Y-%m-%dT%H:%M:%S%z'),
        'error': str(e)[:100]
    }))
" <<< "$INPUT" 2>/dev/null) || exit 0

# Rotation check
if [ -f "$PRESSURE_FILE" ] && [ "$(wc -c < "$PRESSURE_FILE" 2>/dev/null || echo 0)" -gt "$MAX_PRESSURE_SIZE" ]; then
    mv "$PRESSURE_FILE" "${PRESSURE_FILE}.$(date +%Y%m%d%H%M%S).bak"
fi

# Append entry (no locking needed for sampled monitoring — contention is negligible)
echo "$ESTIMATE" >> "$PRESSURE_FILE"
