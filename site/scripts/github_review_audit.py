#!/usr/bin/env python3
"""Read-only GitHub PR review audit. Never approves, merges or publishes."""
import argparse
import json
import os
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

def latest_reviews(reviews):
    latest = {}
    for review in sorted(reviews, key=lambda r: r.get("submitted_at") or ""):
        login = (review.get("user") or {}).get("login")
        if login and review.get("state") in {"APPROVED", "CHANGES_REQUESTED", "DISMISSED"}:
            latest[login.lower()] = review
    return latest

def audit(pr, reviews):
    author = ((pr.get("user") or {}).get("login") or "").lower()
    latest = latest_reviews(reviews)
    approved = sorted(login for login, review in latest.items()
                      if review.get("state") == "APPROVED" and login != author
                      and review.get("commit_id") == (pr.get("head") or {}).get("sha"))
    changes = sorted(login for login, review in latest.items()
                     if review.get("state") == "CHANGES_REQUESTED")
    return {
        "pr_number": pr.get("number"),
        "draft": pr.get("draft") is True,
        "head_sha": (pr.get("head") or {}).get("sha"),
        "approved_reviewers": approved,
        "changes_requested_by": changes,
        "independent_approvals": len(approved),
        "approval_scope": "current_head_sha_only",
        "human_release_authorized": False,
        "merge_authorized": False,
        "publish_authorized": False,
        "decision": "blocked_pending_explicit_owner_approval",
        "note": "GitHub review approvals do not constitute explicit owner approval for merge or publication."
    }

def github_json(path, token):
    request = Request("https://api.github.com" + path, headers={
        "Authorization": "Bearer " + token,
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "agentic-sdlc-editorial-audit"
    })
    with urlopen(request, timeout=15) as response:
        return json.load(response)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--repository", required=True)
    parser.add_argument("--pr", required=True, type=int)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if len(args.repository.split("/")) != 2 or not all(args.repository.split("/")):
        parser.error("repository must be owner/name")
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        print("GitHub audit unavailable: missing read-only token")
        return 1
    base = f"/repos/{args.repository}/pulls/{args.pr}"
    try:
        pr = github_json(base, token)
        reviews = []
        page = 1
        while True:
            batch = github_json(base + f"/reviews?per_page=100&page={page}", token)
            reviews.extend(batch)
            if len(batch) < 100:
                break
            page += 1
            if page > 20:
                raise ValueError("review pagination limit exceeded")
    except (HTTPError, URLError, ValueError) as exc:
        print(f"GitHub review audit unavailable: {type(exc).__name__}")
        return 1
    result = audit(pr, reviews)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "
", encoding="utf-8")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
