#!/usr/bin/env python3
"""Resolve direct publisher links from exact-title Google Scholar results.

The static site keeps a Google Scholar query as its safe client-side fallback.
This scheduled resolver replaces it with an actual paper landing page only when
the first Scholar result has an exact title match.  Crossref DOI links provide
a conservative fallback when Scholar is temporarily rate limited.
"""

from __future__ import annotations

import argparse
import html
import json
import re
import time
from pathlib import Path
from urllib.parse import quote
from urllib.request import Request, urlopen


def title_of(citation: str) -> str | None:
    match = re.search(r'"(.+?)"', citation)
    return match.group(1) if match else None


def normalised(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", value.lower())


def fetch(url: str) -> str:
    request = Request(url, headers={"User-Agent": "Mozilla/5.0 (compatible; JiayiMaPublicationBot/1.0)"})
    with urlopen(request, timeout=30) as response:
        return response.read().decode("utf-8", errors="replace")


def scholar_link(title: str) -> str | None:
    page = fetch(f"https://scholar.google.com/scholar?q={quote(chr(34) + title + chr(34))}&hl=en")
    if "unusual traffic" in page.lower() or "not a robot" in page.lower():
        raise RuntimeError("Google Scholar temporarily rate limited the resolver")
    match = re.search(r'<h3[^>]*class="gs_rt"[^>]*>\s*<a href="([^"]+)"[^>]*>(.*?)</a>', page, re.S)
    if not match:
        return None
    result_title = re.sub(r"<[^>]+>", "", html.unescape(match.group(2)))
    if normalised(result_title) != normalised(title):
        return None
    url = html.unescape(match.group(1))
    return url if url.startswith("http") and "scholar.google" not in url else None


def crossref_link(title: str) -> str | None:
    payload = json.loads(fetch(f"https://api.crossref.org/works?query.bibliographic={quote(title)}&rows=3"))
    for item in payload.get("message", {}).get("items", []):
        candidate = (item.get("title") or [""])[0]
        doi = item.get("DOI")
        if doi and normalised(candidate) == normalised(title):
            return f"https://doi.org/{doi}"
    return None


def needs_resolution(paper: dict) -> bool:
    url = paper.get("paper", "")
    return not url or "scholar.google.com/scholar?" in url


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", default="docs/data/publications.json")
    parser.add_argument("--limit", type=int, default=12)
    args = parser.parse_args()
    path = Path(args.file)
    content = json.loads(path.read_text(encoding="utf-8"))
    candidates = [paper for paper in content["publications"] if needs_resolution(paper) and title_of(paper["citation"])]
    offset = (int(time.time() // 86400) * args.limit) % max(1, len(candidates))
    queue = (candidates[offset:] + candidates[:offset])[:args.limit]
    found = 0
    for paper in queue:
        title = title_of(paper["citation"])
        try:
            url = scholar_link(title) if title else None
            source = "google-scholar"
        except Exception as error:
            print(f"Scholar lookup unavailable: {error}")
            url = None
            source = "crossref"
        if not url and title:
            try:
                url = crossref_link(title)
                source = "crossref"
            except Exception as error:
                print(f"Crossref lookup unavailable: {error}")
        if url:
            paper["paper"] = url
            paper["paperSource"] = source
            found += 1
            print(f"Matched: {title} -> {url}")
        time.sleep(5)
    path.write_text(json.dumps(content, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Resolved {found} direct Paper links.")


if __name__ == "__main__":
    main()
