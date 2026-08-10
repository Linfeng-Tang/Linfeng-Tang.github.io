#!/usr/bin/env python3
"""Fetch public citation counts from the linked Google Scholar profile.

Google Scholar may return a CAPTCHA or rate-limit automated requests. In that
case the script exits successfully without replacing the last known counts.
This protects the published site from losing data due to a transient block.
"""

from __future__ import annotations

import json
import re
import sys
import argparse
from datetime import UTC, datetime
from html import unescape
from pathlib import Path
from urllib.request import Request, urlopen


PROFILE_URL = "https://scholar.google.com/citations?user=73trMQkAAAAJ&hl=en"

def normalise(value: str) -> str:
    return re.sub(r"[^a-z0-9]", "", value.lower())


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", default="docs/data/publications.json")
    args = parser.parse_args()
    path = Path(args.file)
    request = Request(PROFILE_URL, headers={"User-Agent": "Mozilla/5.0 (compatible; JiayiMaHomepageBot/1.0)"})
    try:
        with urlopen(request, timeout=45) as response:
            source = response.read().decode("utf-8", errors="replace")
    except Exception as error:
        print(f"Scholar unavailable; preserving previous citation counts ({error}).")
        return 0
    if "captcha" in source.lower() or "not a robot" in source.lower():
        print("Scholar challenged this run; preserving previous citation counts.")
        return 0

    # The profile's public listing has rows with gsc_a_at (title) and gsc_a_ac
    # (citation count). This intentionally updates only exact-normalised matches.
    matches = re.findall(
        r'class="gsc_a_at"[^>]*>(.*?)</a>.*?class="gsc_a_ac[^>]*>(.*?)</a>',
        source,
        flags=re.DOTALL,
    )
    counts = {}
    for raw_title, raw_count in matches:
        title = re.sub(r"<.*?>", "", unescape(raw_title)).strip()
        count = re.sub(r"\D", "", unescape(raw_count))
        if title and count:
            counts[normalise(title)] = int(count)
    if not counts:
        print("Scholar response contained no publication counts; preserving previous values.")
        return 0

    content = json.loads(path.read_text(encoding="utf-8"))
    updated = 0
    for publication in content["publications"]:
        title_match = re.search(r'"(.+?)"', publication["citation"])
        if not title_match:
            continue
        count = counts.get(normalise(title_match.group(1)))
        if count is not None:
            publication["citations"] = count
            updated += 1
    content["citationSyncedAt"] = datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    path.write_text(json.dumps(content, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Updated {updated} citation counts.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
