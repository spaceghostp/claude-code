#!/usr/bin/env python3
"""Extract high-value claims from WS-000-02 YouTube corpus.

Reads all extractions.jsonl files, filters by confidence and type,
groups by keyword cluster, and outputs a ranked manifest for vault capture.
"""

import json
import glob
import os
import sys
from collections import defaultdict
from pathlib import Path

WS002_YOUTUBE = "/Users/coppervessel/Desktop/WS-000-02/.claude/youtube-work"
TARGET_TYPES = {"technique", "pattern", "warning", "anti-pattern", "philosophy"}
MIN_CONFIDENCE = 0.77
OUTPUT_PATH = "/Users/coppervessel/Desktop/WS-000-03/scripts/claims-manifest.json"


def load_video_meta(video_dir):
    """Load video title from meta.json."""
    meta_path = os.path.join(video_dir, "meta.json")
    if os.path.exists(meta_path):
        try:
            with open(meta_path) as f:
                meta = json.load(f)
                return meta.get("title", "Unknown")
        except (json.JSONDecodeError, KeyError):
            pass
    return "Unknown"


def load_all_claims():
    """Load and filter claims from all extractions.jsonl files."""
    claims = []
    extraction_files = glob.glob(os.path.join(WS002_YOUTUBE, "*/extractions.jsonl"))

    for fpath in extraction_files:
        video_dir = os.path.dirname(fpath)
        video_id = os.path.basename(video_dir)
        video_title = load_video_meta(video_dir)

        with open(fpath) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    claim = json.loads(line)
                except json.JSONDecodeError:
                    continue

                claim_type = claim.get("type", "")
                confidence = claim.get("confidence", 0)

                if claim_type in TARGET_TYPES and confidence > MIN_CONFIDENCE:
                    claim["_video_id"] = video_id
                    claim["_video_title"] = video_title
                    claims.append(claim)

    return claims


def cluster_by_keywords(claims):
    """Group claims by their keywords, tracking keyword frequency."""
    keyword_claims = defaultdict(list)
    for claim in claims:
        for kw in claim.get("keywords", []):
            keyword_claims[kw].append(claim["id"])

    # Sort keywords by number of claims (cross-video patterns)
    keyword_freq = {kw: len(ids) for kw, ids in keyword_claims.items()}
    return keyword_claims, keyword_freq


def deduplicate_by_title(claims):
    """Remove near-duplicate claims (same title from different extractions)."""
    seen_titles = {}
    unique = []
    for c in claims:
        title = c.get("title", "").lower().strip()
        if title in seen_titles:
            # Keep the higher-confidence one
            existing = seen_titles[title]
            if c.get("confidence", 0) > existing.get("confidence", 0):
                unique.remove(existing)
                unique.append(c)
                seen_titles[title] = c
        else:
            seen_titles[title] = c
            unique.append(c)
    return unique


def score_claim(claim, keyword_freq):
    """Score a claim based on confidence, keyword frequency, and visual support."""
    conf = claim.get("confidence", 0)
    # Keyword breadth: how many high-frequency keywords does this claim touch?
    kw_score = sum(
        keyword_freq.get(kw, 0) for kw in claim.get("keywords", [])
    )
    # Normalize keyword score (log-ish)
    kw_norm = min(kw_score / 20.0, 1.0)
    # Visual support bonus (OCR-enriched claims are higher signal)
    visual = 0.05 if claim.get("has_visual_support") else 0
    return conf * 0.5 + kw_norm * 0.35 + visual + 0.1


def build_manifest(claims, keyword_freq, top_n=80):
    """Build ranked manifest of top claims."""
    for claim in claims:
        claim["_score"] = score_claim(claim, keyword_freq)

    ranked = sorted(claims, key=lambda c: c["_score"], reverse=True)[:top_n]

    manifest = []
    for claim in ranked:
        manifest.append({
            "id": claim["id"],
            "title": claim.get("title", ""),
            "type": claim.get("type", ""),
            "confidence": claim.get("confidence", 0),
            "score": round(claim["_score"], 3),
            "keywords": claim.get("keywords", []),
            "video_id": claim.get("_video_id", ""),
            "video_title": claim.get("_video_title", ""),
            "has_visual_support": claim.get("has_visual_support", False),
            "content_preview": claim.get("content", "")[:200],
            "content_full": claim.get("content", ""),
        })

    return manifest


def print_summary(manifest, keyword_freq):
    """Print human-readable summary."""
    print(f"\n{'='*70}")
    print(f"WS-000-02 Claims Manifest")
    print(f"{'='*70}")
    print(f"Total high-value claims: {len(manifest)}")
    print(f"\nType distribution:")
    type_counts = defaultdict(int)
    for m in manifest:
        type_counts[m["type"]] += 1
    for t, c in sorted(type_counts.items(), key=lambda x: -x[1]):
        print(f"  {t}: {c}")

    print(f"\nTop 20 keywords (cross-video frequency):")
    top_kw = sorted(keyword_freq.items(), key=lambda x: -x[1])[:20]
    for kw, freq in top_kw:
        print(f"  {kw}: {freq} claims")

    print(f"\nTop 15 claims by score:")
    for i, m in enumerate(manifest[:15], 1):
        print(f"  {i:2d}. [{m['type']:12s}] {m['confidence']:.2f} | {m['title'][:60]}")
        print(f"      video: {m['video_title'][:50]}")
        print(f"      keywords: {', '.join(m['keywords'][:5])}")

    print(f"\nManifest written to: {OUTPUT_PATH}")


def main():
    print("Loading claims from WS-000-02 YouTube corpus...")
    claims = load_all_claims()
    print(f"  {len(claims)} claims match filters (type in {TARGET_TYPES}, confidence > {MIN_CONFIDENCE})")

    print("Deduplicating...")
    claims = deduplicate_by_title(claims)
    print(f"  {len(claims)} unique claims after dedup")

    print("Clustering by keywords...")
    keyword_claims, keyword_freq = cluster_by_keywords(claims)
    print(f"  {len(keyword_freq)} unique keywords")

    print("Building ranked manifest...")
    manifest = build_manifest(claims, keyword_freq, top_n=80)

    with open(OUTPUT_PATH, "w") as f:
        json.dump(manifest, f, indent=2)

    print_summary(manifest, keyword_freq)


if __name__ == "__main__":
    main()
