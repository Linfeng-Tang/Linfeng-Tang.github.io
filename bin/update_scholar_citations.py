#!/usr/bin/env python3
"""Refresh the public Google Scholar snapshot used by the website."""

import json
from datetime import datetime, timezone
from pathlib import Path

import yaml
from scholarly import scholarly

ROOT = Path(__file__).resolve().parent.parent
SOCIALS_FILE = ROOT / "_data" / "socials.yml"
CITATIONS_FILE = ROOT / "_data" / "citations.yml"
PUBLIC_SNAPSHOT_FILE = ROOT / "assets" / "json" / "scholar.json"


def load_scholar_user_id() -> str:
    data = yaml.safe_load(SOCIALS_FILE.read_text(encoding="utf-8")) or {}
    user_id = data.get("scholar_userid")
    if not user_id:
        raise RuntimeError("Missing scholar_userid in _data/socials.yml")
    return str(user_id)


def write_if_changed(path: Path, content: str) -> bool:
    if path.exists() and path.read_text(encoding="utf-8") == content:
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return True


def main() -> None:
    user_id = load_scholar_user_id()
    print(f"Fetching Google Scholar profile: {user_id}")
    scholarly.set_timeout(20)
    scholarly.set_retries(3)
    author = scholarly.fill(scholarly.search_author_id(user_id))
    if not author:
        raise RuntimeError("Google Scholar returned no author profile")
    fetched_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    profile = {"citations": int(author.get("citedby", 0)), "hindex": int(author.get("hindex", 0)), "i10index": int(author.get("i10index", 0)), "updated": fetched_at}
    papers = {}
    for publication in author.get("publications", []):
        pub_id = publication.get("pub_id") or publication.get("author_pub_id")
        if not pub_id:
            continue
        bib = publication.get("bib", {})
        papers[pub_id] = {"title": bib.get("title", "Unknown title"), "year": str(bib.get("pub_year", "Unknown year")), "citations": int(publication.get("num_citations", 0))}
    snapshot = {"profile": profile, "papers": papers}
    json_content = json.dumps(snapshot, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    yml_content = yaml.safe_dump({"metadata": profile, "papers": papers}, allow_unicode=True, sort_keys=True, width=1000)
    print(f"Public snapshot {'updated' if write_if_changed(PUBLIC_SNAPSHOT_FILE, json_content) else 'unchanged'}: {PUBLIC_SNAPSHOT_FILE}")
    print(f"Jekyll citation data {'updated' if write_if_changed(CITATIONS_FILE, yml_content) else 'unchanged'}: {CITATIONS_FILE}")


if __name__ == "__main__":
    main()
