#!/usr/bin/env python3
"""
Download dinosauriosdelarioja.com brochure PDFs and update site CSV associations.
"""

import csv
import json
import os
import shutil
import urllib.request
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
BROCHURE_DIR = DATA_DIR / "brochures"
MAPPINGS_PATH = DATA_DIR / "brochure_mappings.json"
CSV_PATH = DATA_DIR / "eclipse_site_data.csv"


def load_mappings():
    with open(MAPPINGS_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def download_file(url: str, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
        },
    )
    with urllib.request.urlopen(req, timeout=30) as response, open(destination, "wb") as out:
        shutil.copyfileobj(response, out)


def update_csv_associations(mappings: dict) -> None:
    if not CSV_PATH.exists():
        raise FileNotFoundError(f"CSV not found: {CSV_PATH}")

    with open(CSV_PATH, "r", encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
        fieldnames = list(rows[0].keys()) if rows else []

    for field in ["brochure_file", "brochure_title", "brochure_url", "brochure_source_url"]:
        if field not in fieldnames:
            fieldnames.append(field)

    code_to_brochure = {}
    for brochure in mappings.get("brochures", []):
        relative_url = f"data/brochures/{brochure['filename']}"
        for code in brochure.get("site_codes", []):
            code_to_brochure[code.upper()] = {
                "brochure_file": brochure["filename"],
                "brochure_title": brochure["title"],
                "brochure_url": relative_url,
                "brochure_source_url": brochure["source_url"],
            }

    for row in rows:
        brochure = code_to_brochure.get(row.get("code", "").upper())
        if brochure:
            row.update(brochure)
        else:
            row.setdefault("brochure_file", "")
            row.setdefault("brochure_title", "")
            row.setdefault("brochure_url", "")
            row.setdefault("brochure_source_url", "")

    with open(CSV_PATH, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main():
    mappings = load_mappings()
    brochures = mappings.get("brochures", [])
    if not brochures:
        print("No brochure mappings found.")
        return

    print(f"Downloading {len(brochures)} brochure PDF(s) to {BROCHURE_DIR}...")
    for brochure in brochures:
        destination = BROCHURE_DIR / brochure["filename"]
        print(f"  -> {brochure['title']}: {brochure['source_url']}")
        download_file(brochure["source_url"], destination)

    print("Updating CSV brochure associations...")
    update_csv_associations(mappings)
    print("Done.")


if __name__ == "__main__":
    main()

# Made with Bob
