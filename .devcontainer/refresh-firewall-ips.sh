#!/bin/bash
set -euo pipefail
IFS=$'\n\t'

# Refresh GitHub IP ranges and approved domain IPs atomically using ipset swap.
# Designed to run hourly via background loop in postStartCommand.

FALLBACK_FILE="/usr/local/share/github-meta-fallback.json"
CACHE_FILE="/tmp/github-meta-cache.json"

validate_cidr() {
    local cidr="$1"
    if [[ ! "$cidr" =~ ^([0-9]+)\.([0-9]+)\.([0-9]+)\.([0-9]+)/([0-9]+)$ ]]; then
        return 1
    fi
    local o1="${BASH_REMATCH[1]}" o2="${BASH_REMATCH[2]}" o3="${BASH_REMATCH[3]}" o4="${BASH_REMATCH[4]}" prefix="${BASH_REMATCH[5]}"
    if (( o1 > 255 || o2 > 255 || o3 > 255 || o4 > 255 || prefix > 32 )); then
        return 1
    fi
    return 0
}

validate_ip() {
    local ip="$1"
    if [[ ! "$ip" =~ ^([0-9]+)\.([0-9]+)\.([0-9]+)\.([0-9]+)$ ]]; then
        return 1
    fi
    local o1="${BASH_REMATCH[1]}" o2="${BASH_REMATCH[2]}" o3="${BASH_REMATCH[3]}" o4="${BASH_REMATCH[4]}"
    if (( o1 > 255 || o2 > 255 || o3 > 255 || o4 > 255 )); then
        return 1
    fi
    return 0
}

echo "[$(date -Iseconds)] Starting IP refresh..."

# Fetch GitHub meta
gh_ranges=$(curl --connect-timeout 10 -s https://api.github.com/meta 2>/dev/null) || true
if [ -z "$gh_ranges" ] || ! echo "$gh_ranges" | jq -e '.web and .api and .git' >/dev/null 2>&1; then
    echo "[$(date -Iseconds)] WARNING: Live GitHub fetch failed, using cache/fallback"
    if [ -f "$CACHE_FILE" ]; then
        gh_ranges=$(cat "$CACHE_FILE" 2>/dev/null) || true
    fi
    if [ -z "$gh_ranges" ] || ! echo "$gh_ranges" | jq -e '.web and .api and .git' >/dev/null 2>&1; then
        if [ -f "$FALLBACK_FILE" ]; then
            gh_ranges=$(cat "$FALLBACK_FILE" 2>/dev/null) || true
        fi
    fi
    if [ -z "$gh_ranges" ] || ! echo "$gh_ranges" | jq -e '.web and .api and .git' >/dev/null 2>&1; then
        echo "[$(date -Iseconds)] ERROR: No valid GitHub IP source available, skipping refresh"
        exit 1
    fi
else
    echo "$gh_ranges" > "$CACHE_FILE" 2>/dev/null || true
fi

# Build new ipset
ipset create allowed-domains-new hash:net 2>/dev/null || ipset flush allowed-domains-new

while read -r cidr; do
    if validate_cidr "$cidr"; then
        ipset add allowed-domains-new "$cidr" 2>/dev/null || true
    fi
done < <(echo "$gh_ranges" | jq -r '(.web + .api + .git)[]' | aggregate -q)

# Resolve approved domains
for domain in \
    "registry.npmjs.org" \
    "api.anthropic.com" \
    "sentry.io" \
    "statsig.anthropic.com" \
    "statsig.com" \
    "marketplace.visualstudio.com" \
    "vscode.blob.core.windows.net" \
    "update.code.visualstudio.com"; do
    ips=$(dig +noall +answer A "$domain" 2>/dev/null | awk '$4 == "A" {print $5}') || true
    while read -r ip; do
        if [ -n "$ip" ] && validate_ip "$ip"; then
            ipset add allowed-domains-new "$ip" 2>/dev/null || true
        fi
    done < <(echo "$ips")
done

# Atomic swap
ipset swap allowed-domains-new allowed-domains
ipset destroy allowed-domains-new 2>/dev/null || true

echo "[$(date -Iseconds)] IP refresh complete"
