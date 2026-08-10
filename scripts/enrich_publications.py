#!/usr/bin/env python3
"""Apply verified manual Paper/Code links and retain citation information.

Citation counts are supplied by ``sync_scholar.py``.  This file intentionally
does not guess missing links: showing no badge is preferable to a wrong link.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


CURATED_LINKS = {
    "GText-IF: Leveraging Text-Driven Semantics for Degradation-Aware Image Fusion": {
        "paper": "https://scholar.google.com/scholar?q=%22GText-IF%22",
    },
    "Mask-DiFuser: A Masked Diffusion Model for Unified Unsupervised Image Fusion": {
        "paper": "https://scholar.google.com/scholar?q=%22Mask-DiFuser%22",
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
    args = parser.parse_args()
    path = Path(args.file)
    content = json.loads(path.read_text(encoding="utf-8"))
    for publication in content["publications"]:
        parts = publication["citation"].split('"')
        if len(parts) >= 3 and parts[1] in CURATED_LINKS:
            publication.update(CURATED_LINKS[parts[1]])
    path.write_text(json.dumps(content, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
