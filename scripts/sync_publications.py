#!/usr/bin/env python3
"""Synchronise the publication list from Jiayi Ma's public Google Sites page.

The generated JSON is deliberately kept separate from the layout so the webpage
can remain a static GitHub Pages site while its publication data is refreshed by
GitHub Actions.
"""

from __future__ import annotations

import argparse
import html
import json
import re
import sys
from datetime import UTC, datetime
from html.parser import HTMLParser
from pathlib import Path
from urllib.request import Request, urlopen


SOURCE_URL = (
    "https://sites.google.com/site/jiayima2013/"
    "jiayi-ma-%E9%A9%AC%E4%BD%B3%E4%B9%89-professor/publications"
)


class PublicationPageParser(HTMLParser):
    """Extract individual Google Sites list items and year paragraphs."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.blocks: list[dict] = []
        self._capture_tag: str | None = None
        self._parts: list[str] = []
        self._links: list[dict[str, str]] = []
        self._active_link: str | None = None
        self._link_text: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attr = dict(attrs)
        if tag in {"li", "p"} and self._capture_tag is None:
            self._capture_tag = tag
            self._parts = []
            self._links = []
            return
        if self._capture_tag:
            if tag == "a" and attr.get("href"):
                self._active_link = attr["href"]
                self._link_text = []
            elif tag == "br":
                self._parts.append(" ")

    def handle_endtag(self, tag: str) -> None:
        if not self._capture_tag:
            return
        if tag == "a" and self._active_link:
            label = "".join(self._link_text).strip()
            if label:
                self._links.append({"label": label, "url": self._active_link})
            self._active_link = None
            self._link_text = []
        if tag == self._capture_tag:
            text = re.sub(r"\s+", " ", "".join(self._parts)).strip()
            if text:
                self.blocks.append({"text": html.unescape(text), "links": self._links})
            self._capture_tag = None

    def handle_data(self, data: str) -> None:
        if self._capture_tag:
            self._parts.append(data)
            if self._active_link:
                self._link_text.append(data)


def fetch(url: str) -> str:
    request = Request(url, headers={"User-Agent": "JiayiMaHomepageBot/1.0 (+GitHub Pages)"})
    with urlopen(request, timeout=45) as response:
        return response.read().decode("utf-8", errors="replace")


def classify_blocks(blocks: list[dict]) -> list[dict]:
    """Turn the source's visual blocks into year-grouped publication records."""
    publications: list[dict] = []
    year: str | None = None
    seen: set[str] = set()
    for block in blocks:
        text = block["text"]
        compact = re.sub(r"\s+", " ", text).strip()
        year_match = re.fullmatch(r"20\s?(\d{2})", compact)
        if year_match:
            year = f"20{year_match.group(1)}"
            continue
        # Publication entries always contain a quoted title; this prevents
        # navigation, sidebar copy, and explanatory text from entering the list.
        if not year or '"' not in compact or len(compact) < 45:
            continue
        key = re.sub(r"\W+", "", compact).lower()
        if key in seen:
            continue
        seen.add(key)
        publications.append({"year": year, "citation": compact, "links": block["links"]})
    return publications


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default="docs/data/publications.json")
    parser.add_argument("--url", default=SOURCE_URL)
    args = parser.parse_args()

    source = fetch(args.url)
    extractor = PublicationPageParser()
    extractor.feed(source)
    publications = classify_blocks(extractor.blocks)
    if len(publications) < 30:
        raise RuntimeError(
            f"Only extracted {len(publications)} records; source structure may have changed."
        )
    output = {
        "source": args.url,
        "syncedAt": datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "publications": publications,
    }
    destination = Path(args.out)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Synced {len(publications)} publications to {destination}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as error:
        print(f"Publication synchronisation failed: {error}", file=sys.stderr)
        raise SystemExit(1)
