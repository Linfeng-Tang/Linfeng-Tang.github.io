#!/usr/bin/env python3
"""Resolve direct publisher links from exact-title Crossref DOI metadata.

Crossref is always queried first. Its ``resource.primary.URL`` is preferred,
followed by its publisher-provided link metadata, before falling back to the
DOI resolver. Google Scholar is optional and used only when Crossref has no
exact-title record.
"""

from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor
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
    with urlopen(request, timeout=10) as response:
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
            primary = (item.get("resource") or {}).get("primary") or {}
            if primary.get("URL", "").startswith("http"):
                return primary["URL"]
            for link in item.get("link") or []:
                url = link.get("URL", "")
                if url.startswith("http"):
                    return url
            return f"https://doi.org/{doi}"
    return None


def needs_resolution(paper: dict) -> bool:
    return not paper.get("paperChecked") and paper.get("paperSource") not in {"curated-publisher", "crossref", "google-scholar"}


def resolve_one(title: str, scholar_fallback: bool) -> tuple[str | None, str | None]:
    try:
        url = crossref_link(title)
        if url:
            return url, "crossref"
    except Exception:
        pass
    if scholar_fallback:
        try:
            url = scholar_link(title)
            if url:
                return url, "google-scholar"
        except Exception:
            pass
    return None, None


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", default="docs/data/publications.json")
    parser.add_argument("--limit", type=int, default=12)
    parser.add_argument("--offset", type=int, default=None, help="Start position in the unresolved publication list")
    parser.add_argument("--delay", type=float, default=1.0)
    parser.add_argument("--workers", type=int, default=1)
    parser.add_argument("--scholar-fallback", action="store_true")
    parser.add_argument("--quiet", action="store_true")
    args = parser.parse_args()
    path = Path(args.file)
    content = json.loads(path.read_text(encoding="utf-8"))
    candidates = [paper for paper in content["publications"] if needs_resolution(paper) and title_of(paper["citation"])]
    offset = args.offset if args.offset is not None else int(time.time() // 86400) * args.limit
    offset %= max(1, len(candidates))
    queue = (candidates[offset:] + candidates[:offset])[:args.limit]
    found = 0
    titles = [title_of(paper["citation"]) for paper in queue]
    workers = max(1, min(args.workers, 8))
    if workers == 1:
        results = []
        for title in titles:
            results.append(resolve_one(title, args.scholar_fallback) if title else (None, None))
            time.sleep(args.delay)
    else:
        with ThreadPoolExecutor(max_workers=workers) as executor:
            results = list(executor.map(
                lambda title: resolve_one(title, args.scholar_fallback) if title else (None, None), titles
            ))
    for paper, title, result in zip(queue, titles, results):
        url, source = result
        paper["paperChecked"] = True
        if url:
            paper["paper"] = url
            paper["paperSource"] = source
            found += 1
            if not args.quiet:
                print(f"Matched: {title} -> {url}")
    path.write_text(json.dumps(content, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Resolved {found} direct Paper links.")


if __name__ == "__main__":
    main()
