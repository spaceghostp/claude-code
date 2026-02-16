#!/bin/bash
set -euo pipefail  # Exit on error, undefined vars, and pipeline failures
IFS=$'\n\t'       # Stricter word splitting

FALLBACK_FILE="/usr/local/share/github-meta-fallback.json"
CACHE_FILE="/tmp/github-meta-cache.json"

# --- Validation helpers ---

validate_cidr() {
    local cidr="$1"
    # Must match N.N.N.N/P structure
    if [[ ! "$cidr" =~ ^([0-9]+)\.([0-9]+)\.([0-9]+)\.([0-9]+)/([0-9]+)$ ]]; then
        return 1
    fi
    local o1="${BASH_REMATCH[1]}" o2="${BASH_REMATCH[2]}" o3="${BASH_REMATCH[3]}" o4="${BASH_REMATCH[4]}" prefix="${BASH_REMATCH[5]}"
    # Validate octet range 0-255
    if (( o1 > 255 || o2 > 255 || o3 > 255 || o4 > 255 )); then
        return 1
    fi
    # Validate prefix length 0-32
    if (( prefix > 32 )); then
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

# --- GitHub meta fetch with fallback ---

fetch_github_meta() {
    local gh_ranges=""

    # Try live fetch first
    gh_ranges=$(curl --connect-timeout 10 -s https://api.github.com/meta 2>/dev/null) || true
    if [ -n "$gh_ranges" ] && echo "$gh_ranges" | jq -e '.web and .api and .git' >/dev/null 2>&1; then
        echo "Using live GitHub IP ranges"
        # Update cache on successful live fetch
        echo "$gh_ranges" > "$CACHE_FILE" 2>/dev/null || true
        echo "$gh_ranges"
        return 0
    fi

    # Try cached file
    if [ -f "$CACHE_FILE" ]; then
        gh_ranges=$(cat "$CACHE_FILE" 2>/dev/null) || true
        if [ -n "$gh_ranges" ] && echo "$gh_ranges" | jq -e '.web and .api and .git' >/dev/null 2>&1; then
            echo "WARNING: Using cached GitHub IP ranges (live fetch failed)" >&2
            echo "$gh_ranges"
            return 0
        fi
    fi

    # Try baked-in fallback
    if [ -f "$FALLBACK_FILE" ]; then
        gh_ranges=$(cat "$FALLBACK_FILE" 2>/dev/null) || true
        if [ -n "$gh_ranges" ] && echo "$gh_ranges" | jq -e '.web and .api and .git' >/dev/null 2>&1; then
            echo "WARNING: Using fallback GitHub IP ranges (live fetch and cache failed)" >&2
            echo "$gh_ranges"
            return 0
        fi
    fi

    echo "ERROR: Failed to fetch GitHub IP ranges from all sources" >&2
    return 1
}


# 1. Extract Docker DNS info BEFORE any flushing
DOCKER_DNS_RULES=$(iptables-save -t nat | grep "127\.0\.0\.11" || true)

# Flush existing rules and delete existing ipsets
iptables -F
iptables -X
iptables -t nat -F
iptables -t nat -X
iptables -t mangle -F
iptables -t mangle -X
ipset destroy allowed-domains 2>/dev/null || true

# 2. Selectively restore ONLY internal Docker DNS resolution
if [ -n "$DOCKER_DNS_RULES" ]; then
    echo "Restoring Docker DNS rules..."
    iptables -t nat -N DOCKER_OUTPUT 2>/dev/null || true
    iptables -t nat -N DOCKER_POSTROUTING 2>/dev/null || true
    echo "$DOCKER_DNS_RULES" | xargs -L 1 iptables -t nat
else
    echo "No Docker DNS rules to restore"
fi

# First allow DNS and localhost before any restrictions
# Allow outbound DNS
iptables -A OUTPUT -p udp --dport 53 -j ACCEPT
# Allow inbound DNS responses
iptables -A INPUT -p udp --sport 53 -j ACCEPT
# Allow outbound SSH
iptables -A OUTPUT -p tcp --dport 22 -j ACCEPT
# Allow inbound SSH responses
iptables -A INPUT -p tcp --sport 22 -m state --state ESTABLISHED -j ACCEPT
# Allow localhost
iptables -A INPUT -i lo -j ACCEPT
iptables -A OUTPUT -o lo -j ACCEPT

# Create ipset with CIDR support
ipset create allowed-domains hash:net

# Fetch GitHub meta information with fallback chain
echo "Fetching GitHub IP ranges..."
gh_ranges=$(fetch_github_meta)
if [ $? -ne 0 ]; then
    echo "ERROR: Cannot proceed without GitHub IP ranges"
    exit 1
fi

echo "Processing GitHub IPs..."
while read -r cidr; do
    if ! validate_cidr "$cidr"; then
        echo "ERROR: Invalid CIDR range from GitHub meta: $cidr"
        exit 1
    fi
    echo "Adding GitHub range $cidr"
    ipset add allowed-domains "$cidr"
done < <(echo "$gh_ranges" | jq -r '(.web + .api + .git)[]' | aggregate -q)

# Resolve and add other allowed domains
for domain in \
    "registry.npmjs.org" \
    "api.anthropic.com" \
    "sentry.io" \
    "statsig.anthropic.com" \
    "statsig.com" \
    "marketplace.visualstudio.com" \
    "vscode.blob.core.windows.net" \
    "update.code.visualstudio.com"; do
    echo "Resolving $domain..."
    # Check DNSSEC (warning only, not blocking)
    dig_output=$(dig +dnssec +noall +answer +comments A "$domain" 2>/dev/null) || true
    if ! echo "$dig_output" | grep -q "flags:.*ad" 2>/dev/null; then
        echo "WARNING: DNSSEC validation not confirmed for $domain"
    fi
    ips=$(echo "$dig_output" | awk '$4 == "A" {print $5}')
    if [ -z "$ips" ]; then
        echo "ERROR: Failed to resolve $domain"
        exit 1
    fi

    while read -r ip; do
        if ! validate_ip "$ip"; then
            echo "ERROR: Invalid IP from DNS for $domain: $ip"
            exit 1
        fi
        echo "Adding $ip for $domain"
        ipset add allowed-domains "$ip"
    done < <(echo "$ips")
done

# Get host IP from default route
HOST_IP=$(ip route | grep default | cut -d" " -f3)
if [ -z "$HOST_IP" ]; then
    echo "ERROR: Failed to detect host IP"
    exit 1
fi

HOST_NETWORK=$(echo "$HOST_IP" | sed "s/\.[0-9]*$/.0\/24/")
echo "Host network detected as: $HOST_NETWORK"

# Set up remaining iptables rules
iptables -A INPUT -s "$HOST_NETWORK" -j ACCEPT
iptables -A OUTPUT -d "$HOST_NETWORK" -j ACCEPT

# Set default policies to DROP first
iptables -P INPUT DROP
iptables -P FORWARD DROP
iptables -P OUTPUT DROP

# First allow established connections for already approved traffic
iptables -A INPUT -m state --state ESTABLISHED,RELATED -j ACCEPT
iptables -A OUTPUT -m state --state ESTABLISHED,RELATED -j ACCEPT

# Then allow only specific outbound traffic to allowed domains
iptables -A OUTPUT -m set --match-set allowed-domains dst -j ACCEPT

# Explicitly REJECT all other outbound traffic for immediate feedback
iptables -A OUTPUT -j REJECT --reject-with icmp-admin-prohibited

echo "Firewall configuration complete"
echo "Verifying firewall rules..."
if curl --connect-timeout 5 https://example.com >/dev/null 2>&1; then
    echo "ERROR: Firewall verification failed - was able to reach https://example.com"
    exit 1
else
    echo "Firewall verification passed - unable to reach https://example.com as expected"
fi

# Verify GitHub API access
if ! curl --connect-timeout 5 https://api.github.com/zen >/dev/null 2>&1; then
    echo "ERROR: Firewall verification failed - unable to reach https://api.github.com"
    exit 1
else
    echo "Firewall verification passed - able to reach https://api.github.com as expected"
fi
