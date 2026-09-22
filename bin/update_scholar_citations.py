#!/usr/bin/env python3
"""Refresh the website's Scholar snapshot with one public-page request."""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from html import unescape
from pathlib import Path
from urllib.request import Request, urlopen

import yaml


ROOT = Path(__file__).resolve().parent.parent
SOCIALS_FILE = ROOT / "_data" / "socials.yml"
CITATIONS_FILE = ROOT / "_data" / "citations.yml"
PUBLIC_SNAPSHOT_FILE = ROOT / "assets" / "json" / "scholar.json"


def scholar_user_id() -> str:
    data = yaml.safe_load(SOCIALS_FILE.read_text(encoding="utf-8")) or {}
    user_id = data.get("scholar_userid")
    if not user_id:
        raise RuntimeError("Missing scholar_userid in _data/socials.yml")
    return str(user_id)


def normalise(value: str) -> str:
    return re.sub(r"[^a-z0-9]", "", value.lower())


def load_snapshot() -> dict:
    try:
        return json.loads(PUBLIC_SNAPSHOT_FILE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {"profile": {}, "papers": {}}


def write_if_changed(path: Path, content: str) -> bool:
    if path.exists() and path.read_text(encoding="utf-8") == content:
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return True


def profile_metrics(source: str) -> dict | None:
    values = re.findall(r'class="gsc_rsb_std"[^>]*>\s*([\d,]+)', source)
    if len(values) < 6:
        return None
    return {
        "citations": int(values[0].replace(",", "")),
        "hindex": int(values[2].replace(",", "")),
        "i10index": int(values[4].replace(",", "")),
    }


def paper_metrics(source: str) -> dict[str, int]:
    rows = re.findall(
        r'class="gsc_a_at"[^>]*>(.*?)</a>.*?class="gsc_a_ac[^>]*>(.*?)</a>',
        source,
        flags=re.DOTALL,
    )
    counts: dict[str, int] = {}
    for raw_title, raw_count in rows:
        title = re.sub(r"<.*?>", "", unescape(raw_title)).strip()
        count = re.sub(r"\D", "", unescape(raw_count))
        if title and count:
            counts[normalise(title)] = int(count)
    return counts


def main() -> None:
    user_id = scholar_user_id()
    url = f"https://scholar.google.com/citations?user={user_id}&hl=en&pagesize=100"
    request = Request(url, headers={"User-Agent": "Mozilla/5.0 (compatible; academic-homepage-updater/1.0)"})
    try:
        with urlopen(request, timeout=45) as response:
            source = response.read().decode("utf-8", errors="replace")
    except Exception as error:
        print(f"Scholar unavailable; preserving last successful snapshot ({error}).")
        return

    if "captcha" in source.lower() or "not a robot" in source.lower():
        print("Scholar challenged this request; preserving last successful snapshot.")
        return

    profile = profile_metrics(source)
    papers_from_scholar = paper_metrics(source)
    if not profile or not papers_from_scholar:
        print("Scholar response was incomplete; preserving last successful snapshot.")
        return

    snapshot = load_snapshot()
    snapshot.setdefault("profile", {})
    snapshot.setdefault("papers", {})
    changed = False
    for key, value in profile.items():
        if snapshot["profile"].get(key) != value:
            snapshot["profile"][key] = value
            changed = True

    checked = 0
    for paper in snapshot["papers"].values():
        count = papers_from_scholar.get(normalise(str(paper.get("title", ""))))
        if count is not None:
            checked += 1
            if paper.get("citations") != count:
                paper["citations"] = count
                changed = True

    if not changed:
        print(f"Scholar data is unchanged ({checked} papers checked).")
        return

    snapshot["profile"]["updated"] = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    write_if_changed(PUBLIC_SNAPSHOT_FILE, json.dumps(snapshot, ensure_ascii=False, indent=2, sort_keys=True) + "\n")
    write_if_changed(
        CITATIONS_FILE,
        yaml.safe_dump({"metadata": snapshot["profile"], "papers": snapshot["papers"]}, allow_unicode=True, sort_keys=True, width=1000),
    )
    print(f"Updated Scholar profile and {checked} checked paper records.")


if __name__ == "__main__":
    main()
