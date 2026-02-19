#!/usr/bin/env bash
# YouTube Batch Runner
# Processes multiple YouTube URLs through /youtube-extract with rate limiting
#
# Usage:
#   bash scripts/youtube-batch-runner.sh .claude/youtube-sources.txt
#   bash scripts/youtube-batch-runner.sh .claude/youtube-sources.txt --dry-run
#   bash scripts/youtube-batch-runner.sh .claude/youtube-sources.txt --resume
#   bash scripts/youtube-batch-runner.sh --playlist "PLCd0h680dr2gzkb4jVbyXSO0AJkub_Xmn"
#
# Input file format:
#   One URL per line. Lines starting with # are ignored.
#   Playlist URLs are expanded to individual video URLs.
#
# Rate limiting:
#   6 minutes between videos (configurable via RATE_LIMIT_SECONDS)
#   Maximum 10 videos per hour

set -euo pipefail

# Graceful shutdown on SIGTERM/SIGINT
SHUTDOWN=false
trap 'SHUTDOWN=true; echo -e "\n${YELLOW:-}Signal received — finishing current video...${NC:-}" >&2' INT TERM

# Configuration
RATE_LIMIT_SECONDS="${RATE_LIMIT_SECONDS:-360}"  # 6 minutes default
STATE_FILE=".claude/youtube-extract-state.jsonl"
LOG_FILE=".claude/youtube-batch-log.txt"
PLAYLIST_ID=""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Parse arguments
SOURCES_FILE=""
DRY_RUN=false
RESUME=false

while [[ $# -gt 0 ]]; do
    case "$1" in
        --playlist)
            PLAYLIST_ID="${2:-}"
            shift 2
            ;;
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        --resume)
            RESUME=true
            shift
            ;;
        -*)
            echo "Unknown option: $1"
            exit 1
            ;;
        *)
            SOURCES_FILE="$1"
            shift
            ;;
    esac
done

# Default sources file if no playlist and no file specified
if [[ -z "$PLAYLIST_ID" && -z "$SOURCES_FILE" ]]; then
    SOURCES_FILE=".claude/youtube-sources.txt"
fi

# Validate input - either playlist or file
if [[ -z "$PLAYLIST_ID" && ! -f "$SOURCES_FILE" ]]; then
    echo -e "${RED}Error: Sources file not found: $SOURCES_FILE${NC}"
    echo "Usage: $0 [sources.txt] [--dry-run] [--resume]"
    echo "       $0 --playlist <playlist_id> [--dry-run] [--resume]"
    exit 1
fi

# Check dependencies
check_dependencies() {
    local missing=()
    for cmd in yt-dlp ffmpeg tesseract; do
        if ! command -v "$cmd" &>/dev/null; then
            missing+=("$cmd")
        fi
    done
    if [[ ${#missing[@]} -gt 0 ]]; then
        echo -e "${RED}Missing dependencies: ${missing[*]}${NC}"
        echo "Install with: brew install ${missing[*]}"
        exit 1
    fi
}

# Extract video ID from URL (parse locally, no network call)
get_video_id() {
    local url="$1"
    # Try to extract from URL directly
    local vid
    vid=$(python3 -c "
import sys, re
from urllib.parse import urlparse, parse_qs
url = sys.argv[1]
parsed = urlparse(url)
if 'youtube.com' in parsed.netloc:
    qs = parse_qs(parsed.query)
    vid = qs.get('v', [''])[0]
elif 'youtu.be' in parsed.netloc:
    vid = parsed.path.lstrip('/')
else:
    vid = ''
print(vid)
" "$url" 2>/dev/null)
    if [[ -n "$vid" ]]; then
        echo "$vid"
    else
        # Fallback to yt-dlp for non-standard URLs
        yt-dlp --get-id "$url" 2>/dev/null || echo ""
    fi
}

# Check if video already processed
is_processed() {
    local video_id="$1"
    if [[ -f "$STATE_FILE" ]]; then
        python3 -c "
import sys, json
vid = sys.argv[1]
with open(sys.argv[2]) as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
            if obj.get('video_id') == vid and obj.get('status') == 'completed':
                sys.exit(0)
        except json.JSONDecodeError:
            continue
sys.exit(1)
" "$video_id" "$STATE_FILE" 2>/dev/null
        return $?
    fi
    return 1
}

# Log message with timestamp
log() {
    local msg="$1"
    local timestamp
    timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$timestamp] $msg" >> "$LOG_FILE"
    echo -e "$msg"
}

# Read valid URLs from file
read_urls() {
    local file="$1"
    grep -v '^#' "$file" | grep -v '^$' | grep -E 'youtube\.com|youtu\.be'
}

# Extract video URLs from playlist (uses chrome+basictext for private playlists)
get_playlist_urls() {
    local playlist_id="$1"
    yt-dlp --cookies-from-browser chrome+basictext --flat-playlist \
        --print "https://www.youtube.com/watch?v=%(id)s" \
        "https://www.youtube.com/playlist?list=$playlist_id" 2>/dev/null
}

# Main execution
main() {
    check_dependencies

    # Read all URLs - from playlist or file
    if [[ -n "$PLAYLIST_ID" ]]; then
        log "Fetching videos from playlist: $PLAYLIST_ID"
        mapfile -t urls < <(get_playlist_urls "$PLAYLIST_ID")
    else
        mapfile -t urls < <(read_urls "$SOURCES_FILE")
    fi

    if [[ ${#urls[@]} -eq 0 ]]; then
        echo -e "${YELLOW}No valid YouTube URLs found in $SOURCES_FILE${NC}"
        exit 0
    fi

    log "Found ${#urls[@]} URLs to process"

    # Count already processed
    local processed=0
    local pending=0
    local failed=0

    for url in "${urls[@]}"; do
        local video_id
        video_id=$(get_video_id "$url")
        if [[ -z "$video_id" ]]; then
            log "${RED}Failed to get video ID for: $url${NC}"
            failed=$((failed + 1))
            continue
        fi

        if is_processed "$video_id"; then
            processed=$((processed + 1))
            if $DRY_RUN; then
                log "${YELLOW}[SKIP] Already processed: $video_id${NC}"
            fi
        else
            pending=$((pending + 1))
            if $DRY_RUN; then
                log "${GREEN}[PENDING] Will process: $video_id${NC}"
            fi
        fi
    done

    if $DRY_RUN; then
        echo ""
        echo "Summary:"
        echo "  Already processed: $processed"
        echo "  Pending: $pending"
        echo "  Failed to parse: $failed"
        echo ""
        echo "Estimated time: $((pending * RATE_LIMIT_SECONDS / 60)) minutes"
        exit 0
    fi

    # Process pending videos (set +e allows signal-aware control flow)
    local current=0
    set +e
    for url in "${urls[@]}"; do
        if [ "$SHUTDOWN" = true ]; then
            log "${YELLOW}Shutdown requested — stopping after current video${NC}"
            break
        fi

        local video_id
        video_id=$(get_video_id "$url")

        if [[ -z "$video_id" ]]; then
            log "${RED}Skipping invalid URL: $url${NC}"
            continue
        fi

        if is_processed "$video_id"; then
            continue
        fi

        current=$((current + 1))
        log "${GREEN}Processing [$current/$pending]: $video_id${NC}"

        # Run the full extraction pipeline
        python3 .claude/scripts/process_video.py "$video_id" 2>&1 | while read -r line; do
            log "  $line"
        done

        # Rate limiting (interruptible sleep)
        if [[ $current -lt $pending && "$SHUTDOWN" != true ]]; then
            log "Rate limiting: waiting $RATE_LIMIT_SECONDS seconds..."
            sleep "$RATE_LIMIT_SECONDS" &
            wait $! 2>/dev/null || true
        fi
    done
    set -e

    if [ "$SHUTDOWN" = true ]; then
        log "${YELLOW}Batch interrupted by signal. Processed $current videos before shutdown.${NC}"
    else
        log "${GREEN}Batch processing complete. Processed $current videos.${NC}"
    fi

    # Post-processing: cross-linking and verification
    if [[ $current -gt 0 ]]; then
        log "Running cross-linking..."
        python3 .claude/skills/generate-notes/cross_linking.py vault/ --idf 2>&1 | while read -r line; do
            log "  $line"
        done
        log "Running verification..."
        python3 .claude/skills/obsidian-vault/vault_ops.py verify vault/ 2>&1 | while read -r line; do
            log "  $line"
        done
    fi
}

# Run main function
main
