#!/usr/bin/env python3
"""Find conservative GitHub Code links for Jiayi Ma publications.

The scheduled job uses a rotating batch, so it gradually checks every paper
without exceeding GitHub's search limit.  Existing source/curated links always
take priority, and a result is accepted only when several title words appear
in its repository name or description.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import time
from pathlib import Path
from urllib.parse import quote
from urllib.request import Request, urlopen


STOP_WORDS = {"a", "an", "and", "for", "of", "the", "to", "via", "with", "in", "on", "from", "based"}
GITHUB_URL = re.compile(r"https?://(?:www\.)?github\.com/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", re.I)


def title_of(citation: str) -> str | None:
    match = re.search(r'"(.+?)"', citation)
    return match.group(1) if match else None


def distinctive_words(title: str) -> list[str]:
    words = re.findall(r"[A-Za-z0-9][A-Za-z0-9+-]*", title.lower())
    return [word for word in words if len(word) >= 5 and word not in STOP_WORDS]


def normalised(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", value.lower())


def github_url_in(text: str | None) -> str | None:
    if not text:
        return None
    match = GITHUB_URL.search(text)
    return match.group(0).rstrip(".,;:)") if match else None


def generic_profile(url: str | None) -> bool:
    return bool(url and re.fullmatch(r"https?://github\.com/[^/?#]+/?(?:\?tab=repositories)?", url, re.I))


def github_json(url: str, token: str) -> dict:
    request = Request(url, headers={
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "jiayi-ma-homepage-link-discovery",
    })
    with urlopen(request, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))


def public_json(url: str) -> dict:
    request = Request(url, headers={"User-Agent": "JiayiMaHomepageBot/1.0"})
    with urlopen(request, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))


def candidate_url(title: str, token: str) -> str | None:
    words = distinctive_words(title)
    if len(words) < 2:
        return None
    query = " ".join(words[:5]) + " in:name,description"
    result = github_json(f"https://api.github.com/search/repositories?q={quote(query)}&per_page=5", token)
    title_words = set(words)
    for repo in result.get("items", []):
        haystack = f"{repo.get('name', '')} {repo.get('description') or ''}".lower()
        overlap = sum(word in haystack for word in title_words)
        if overlap >= min(3, len(title_words)):
            return repo["html_url"]
    return None


def abstract_code_url(title: str, token: str) -> str | None:
    """Inspect public paper metadata and arXiv abstracts for explicit links."""
    fields = "title,externalIds,abstract"
    try:
        data = public_json(
            f"https://api.semanticscholar.org/graph/v1/paper/search?query={quote(title)}&limit=3&fields={fields}",
        )
    except Exception:
        return None
    wanted = normalised(title)
    for paper in data.get("data", []):
        if normalised(paper.get("title", "")) != wanted:
            continue
        found = github_url_in(paper.get("abstract"))
        if found:
            return found
        arxiv_id = (paper.get("externalIds") or {}).get("ArXiv")
        if arxiv_id:
            request = Request(
                f"https://arxiv.org/abs/{quote(arxiv_id)}",
                headers={"User-Agent": "JiayiMaHomepageBot/1.0"},
            )
            try:
                with urlopen(request, timeout=30) as response:
                    found = github_url_in(response.read().decode("utf-8", errors="replace"))
            except Exception:
                continue
            if found:
                return found
    return None


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", default="docs/data/publications.json")
    parser.add_argument("--limit", type=int, default=25)
    args = parser.parse_args()
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if not token:
        print("GitHub token unavailable; skipping discovery.")
        return

    path = Path(args.file)
    content = json.loads(path.read_text(encoding="utf-8"))
    missing = [
        paper for paper in content["publications"]
        if (not paper.get("code") or generic_profile(paper.get("code"))) and title_of(paper["citation"])
    ]
    offset = (int(time.time() // 86400) * args.limit) % max(1, len(missing))
    queue = (missing[offset:] + missing[:offset])[:args.limit]
    found = 0
    for paper in queue:
        title = title_of(paper["citation"])
        try:
            url = candidate_url(title, token) if title else None
            source = "github-title-search"
            if not url and title:
                url = abstract_code_url(title, token)
                source = "paper-abstract"
        except Exception as error:
            print(f"Search stopped: {error}")
            break
        if url:
            paper["code"] = url
            paper["codeSource"] = source
            found += 1
            print(f"Matched: {title} -> {url}")
        time.sleep(2.1)
    path.write_text(json.dumps(content, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"GitHub discovery added {found} Code links.")


if __name__ == "__main__":
    main()
