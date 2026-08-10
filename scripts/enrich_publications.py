#!/usr/bin/env python3
"""Normalise original links and apply verified Paper/Code links."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


CURATED_LINKS = {
    "HyperGCT: A Dynamic Hyper-GNN-Learned Geometric Constraint for 3D Registration": {
        "paper": "https://ieeexplore.ieee.org/abstract/document/11443336/",
        "paperSource": "curated-publisher",
    },
    "Nonrigid Point Set Registration with Robust Transformation Learning under Manifold Regularization": {
        "code": "https://github.com/jiayi-ma/MR-RPM",
    },
    "GText-IF: Leveraging Text-Driven Semantics for Degradation-Aware Image Fusion": {
    },
    "Mask-DiFuser: A Masked Diffusion Model for Unified Unsupervised Image Fusion": {
    },
    "ControlFusion: A Controllable Image Fusion Network with Language-Vision Degradation Prompts": {
        "paper": "https://arxiv.org/abs/2503.23356",
        "code": "https://github.com/Linfeng-Tang/ControlFusion",
    },
    "C2RF: Bridging Multi-modal Image Registration and Fusion via Commonality Mining and Contrastive Learning": {
        "code": "https://github.com/QinglongYan-hub/C2RF",
    },
    "U2Fusion: A Unified Unsupervised Image Fusion Network": {
        "code": "https://github.com/hanna-xu/U2Fusion",
    },
    "Locality Preserving Matching": {
        "code": "https://github.com/Jiawyang/LocalityPreservingMatching",
    },
}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", default="docs/data/publications.json")
    parser.add_argument("--previous", help="Previously enriched JSON whose verified links should be retained")
    args = parser.parse_args()
    path = Path(args.file)
    content = json.loads(path.read_text(encoding="utf-8"))
    previous_by_title = {}
    if args.previous and Path(args.previous).exists():
        prior = json.loads(Path(args.previous).read_text(encoding="utf-8"))
        for item in prior.get("publications", []):
            parts = item.get("citation", "").split('"')
            if len(parts) >= 3:
                previous_by_title[parts[1]] = item
    for publication in content["publications"]:
        retained_links = []
        for link in publication.get("links", []):
            label = link.get("label", "").strip().lower()
            if label == "code" and link.get("url"):
                publication.setdefault("code", link["url"])
                publication.setdefault("codeSource", "original-publication-page")
            elif label in {"pdf", "paper"} and link.get("url"):
                publication.setdefault("paper", link["url"])
            else:
                retained_links.append(link)
        publication["links"] = retained_links
        if "scholar.google.com/scholar?" in publication.get("paper", ""):
            publication.pop("paper", None)
            publication.pop("paperSource", None)
        generic_profile = re.fullmatch(r"https?://github\.com/[^/?#]+/?(?:\?tab=repositories)?", publication.get("code", ""), re.I)
        if generic_profile:
            publication.setdefault("codeSource", "original-publication-page")
        publication["citation"] = re.sub(r"\s*\(Code\)", "", publication["citation"], flags=re.I)
        parts = publication["citation"].split('"')
        previous = previous_by_title.get(parts[1]) if len(parts) >= 3 else None
        if previous:
            for key in ("paper", "paperSource", "paperChecked", "code", "codeSource", "citations"):
                if key in previous and key not in publication:
                    publication[key] = previous[key]
            if previous.get("paperSource") in {"curated-publisher", "crossref", "google-scholar"}:
                publication["paper"] = previous["paper"]
                publication["paperSource"] = previous["paperSource"]
        if len(parts) >= 3 and parts[1] in CURATED_LINKS:
            publication.update(CURATED_LINKS[parts[1]])
    path.write_text(json.dumps(content, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
