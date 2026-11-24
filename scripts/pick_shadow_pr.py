#!/usr/bin/env python3
"""Spoiler-free Shadow PR candidate extractor using Python stdlib only.

Requires no external packages and no `gh` CLI. Optionally reads `GITHUB_TOKEN`
from the environment to lift the unauthenticated GitHub API limit (60 req/hr).
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request

PRESETS: dict[str, dict[str, str]] = {
    "tokio": {
        "repo": "tokio-rs/tokio",
        "query": (
            "repo:tokio-rs/tokio is:pr is:merged label:C-bug label:A-tokio "
            "comments:>=5 (loom OR miri OR race OR deadlock OR cancel OR ordering) "
            "-label:C-docs"
        ),
        "test_hint": "cargo test --workspace (or RUSTFLAGS='--cfg loom' / cargo +nightly miri test)",
    },
    "vllm": {
        "repo": "vllm-project/vllm",
        "query": (
            'repo:vllm-project/vllm is:pr is:merged comments:>=5 '
            '("v1/core" OR "scheduler" OR "kv_cache" OR "prefix_cache") '
            "(fix OR bug OR race OR leak OR preempt OR evict) -cuda -rocm -tpu"
        ),
        "test_hint": "VLLM_TARGET_DEVICE=cpu pytest tests/v1/core/test_scheduler.py",
    },
    "sglang": {
        "repo": "sgl-project/sglang",
        "query": (
            'repo:sgl-project/sglang is:pr is:merged comments:>=4 '
            '("sgl-router" OR "sgl-model-gateway" OR "radix" OR "rust") '
            "(fix OR race OR deadlock OR leak OR evict OR lock)"
        ),
        "test_hint": "cd sgl-router && cargo test  # or cd sgl-model-gateway && cargo test",
    },
}

ISSUE_REF_RE = re.compile(
    r"(?:close[sd]?|fix(?:e[sd])?|resolve[sd]?)\s+#(\d+)", re.IGNORECASE
)


def github_get(url: str) -> dict:
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "rust-ai-infra-training-shadow-pr-picker",
    }
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"

    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"GitHub API HTTP {exc.code}: {body[:240]}") from exc


def find_candidates(
    repo: str,
    query: str,
    *,
    inspect_limit: int,
    min_lines: int,
    max_lines: int,
    min_files: int,
    max_files: int,
    show_title: bool,
) -> list[dict]:
    encoded = urllib.parse.urlencode(
        {"q": query, "sort": "updated", "order": "desc", "per_page": inspect_limit}
    )
    search_data = github_get(f"https://api.github.com/search/issues?{encoded}")
    items = search_data.get("items", [])

    matches: list[dict] = []
    for item in items:
        pr_num = item["number"]
        pr = github_get(f"https://api.github.com/repos/{repo}/pulls/{pr_num}")

        total_lines = int(pr.get("additions", 0)) + int(pr.get("deletions", 0))
        changed_files = int(pr.get("changed_files", 0))
        merge_sha = pr.get("merge_commit_sha")

        if not merge_sha:
            continue
        if not (min_lines <= total_lines <= max_lines):
            continue
        if not (min_files <= changed_files <= max_files):
            continue

        body = pr.get("body") or ""
        linked_issues = sorted({int(m) for m in ISSUE_REF_RE.findall(body)})
        entry = {
            "pr_number": pr_num,
            "merged_at": (pr.get("merged_at") or "")[:10],
            "lines_changed": total_lines,
            "changed_files": changed_files,
            "review_comments": int(pr.get("review_comments", 0))
            + int(pr.get("comments", 0)),
            "checkout_cmd": f"git checkout {merge_sha}~1",
            "linked_issues": [
                f"https://github.com/{repo}/issues/{n}" for n in linked_issues
            ],
            "postmortem_pr_url": f"https://github.com/{repo}/pull/{pr_num}",
        }
        if show_title:
            entry["title"] = pr.get("title", "")
        matches.append(entry)

    return matches


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Pick spoiler-free merged PR candidates for Shadow PR training."
    )
    parser.add_argument(
        "--preset",
        choices=sorted(PRESETS.keys()),
        default="tokio",
        help="Target repository preset (default: tokio).",
    )
    parser.add_argument(
        "--inspect-limit",
        "--limit",
        dest="inspect_limit",
        type=int,
        default=8,
        help="Max search items to inspect via PR API (keeps rate-limit safe; default: 8).",
    )
    parser.add_argument("--min-lines", type=int, default=20)
    parser.add_argument("--max-lines", type=int, default=300)
    parser.add_argument("--min-files", type=int, default=2)
    parser.add_argument("--max-files", type=int, default=8)
    parser.add_argument(
        "--show-title",
        action="store_true",
        help="Include PR titles (off by default to minimize root-cause spoilers).",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print machine-readable JSON output.",
    )
    args = parser.parse_args()

    preset = PRESETS[args.preset]
    try:
        matches = find_candidates(
            preset["repo"],
            preset["query"],
            inspect_limit=args.inspect_limit,
            min_lines=args.min_lines,
            max_lines=args.max_lines,
            min_files=args.min_files,
            max_files=args.max_files,
            show_title=args.show_title,
        )
    except RuntimeError as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps(matches, ensure_ascii=False, indent=2))
        return 0

    print(f"=== Shadow PR Candidates ({preset['repo']}) ===")
    print(f"Test hint: {preset['test_hint']}\n")
    if not matches:
        print(
            "No PR matched the size/file filter within --inspect-limit. "
            "Try increasing --inspect-limit (with GITHUB_TOKEN set) or widening --max-lines."
        )
        return 0

    for idx, m in enumerate(matches, 1):
        print(
            f"[{idx}] PR #{m['pr_number']} | merged={m['merged_at']} | "
            f"lines={m['lines_changed']} | files={m['changed_files']} | "
            f"comments={m['review_comments']}"
        )
        if args.show_title:
            print(f"    Title       : {m['title']}")
        print(f"    Checkout    : {m['checkout_cmd']}")
        if m["linked_issues"]:
            print(f"    Issues ONLY : {', '.join(m['linked_issues'])}")
        else:
            print("    Issues ONLY : (none auto-linked; ask agent to summarize symptom without spoiler)")
        print(f"    After Done  : {m['postmortem_pr_url']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
