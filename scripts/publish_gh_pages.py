#!/usr/bin/env python3
"""Publish a static directory into a subdirectory of a GitHub Pages branch.

Files are written through GitHub's Contents API. The entry HTML file is always
written last so an initial deployment never exposes a partly uploaded page.
"""

from __future__ import annotations

import argparse
import base64
import json
import os
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen


def api(method: str, endpoint: str, token: str, data: dict | None = None) -> dict:
    payload = None if data is None else json.dumps(data).encode("utf-8")
    request = Request(
        f"https://api.github.com{endpoint}",
        data=payload,
        method=method,
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "jiayi-ma-homepage-publisher",
            **({"Content-Type": "application/json"} if payload else {}),
        },
    )
    with urlopen(request, timeout=60) as response:
        response_data = response.read().decode("utf-8")
        return json.loads(response_data) if response_data else {}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", required=True, help="Directory whose contents will be published")
    parser.add_argument("--prefix", default="jiayi-ma", help="Target directory in the Pages branch")
    parser.add_argument("--branch", default="gh-pages")
    parser.add_argument("--repository", default=os.environ.get("GITHUB_REPOSITORY", "Linfeng-Tang/Linfeng-Tang.github.io"))
    parser.add_argument("--message", default="Deploy Jiayi Ma academic homepage")
    args = parser.parse_args()

    token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    if not token:
        raise RuntimeError("GH_TOKEN or GITHUB_TOKEN is required")
    source = Path(args.source)
    files = sorted(path for path in source.rglob("*") if path.is_file())
    if not files:
        raise RuntimeError(f"No files found in {source}")

    # Upload index.html last: it is the only page entry point, so visitors do
    # not encounter an incomplete initial release while companion assets arrive.
    files.sort(key=lambda path: path.name == "index.html")
    commits = []
    for file_path in files:
        relative_path = file_path.relative_to(source).as_posix()
        prefix = "" if args.prefix in {"", "."} else args.prefix.rstrip("/")
        target_path = f"{prefix}/{relative_path}" if prefix else relative_path
        payload = {
            "message": args.message,
            "branch": args.branch,
            "content": base64.b64encode(file_path.read_bytes()).decode("ascii"),
        }
        try:
            existing = api("GET", f"/repos/{args.repository}/contents/{target_path}?ref={args.branch}", token)
            payload["sha"] = existing["sha"]
        except HTTPError as error:
            if error.code != 404:
                raise
        result = api("PUT", f"/repos/{args.repository}/contents/{target_path}", token, payload)
        commits.append(result["commit"]["sha"])
    print(commits[-1])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
