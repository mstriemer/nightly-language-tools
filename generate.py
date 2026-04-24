"""
Generate language-tools.json from Mozilla's Nightly FTP directory.

Output mimics the Mozilla Addons API format (/api/v4/addons/language-tools/)
so existing consumers require no changes.

Usage:
    python generate.py                      # writes data/language-tools.json
    python generate.py --out path/to/file   # writes to a custom path
    python generate.py --check              # exits 1 if output would change
"""

import argparse
import json
import re
import sys
from pathlib import Path

import httpx

FTP_BASE = "https://ftp.mozilla.org/pub/firefox/nightly/latest-mozilla-central-l10n/linux-x86_64/xpi/"
DEFAULT_OUT = Path(__file__).parent / "data" / "language-tools.json"


def fetch_langpacks() -> list:
    with httpx.Client(timeout=30) as client:
        resp = client.get(FTP_BASE)
        resp.raise_for_status()
        html = resp.text

    highest_version = "100.0a1"
    pattern = r"firefox-(\d+\.\d+a\d+)\.([\w-]+)\.langpack\.xpi"
    matches = re.findall(pattern, html)

    seen = set()
    unique_matches = []
    for m in matches:
        if m not in seen:
            seen.add(m)
            unique_matches.append(m)
            if m[0] > highest_version:
                highest_version = m[0]

    unique_matches = [match for match in unique_matches if match[0] == highest_version]

    results = []
    for i, (version, locale) in enumerate(unique_matches, start=1):
        xpi_url = f"{FTP_BASE}firefox-{version}.{locale}.langpack.xpi"
        results.append(
            {
                "id": i,
                "current_compatible_version": {
                    "id": i,
                    "file": {"url": xpi_url},
                    "files": [{"url": xpi_url, "platform": "all"}],
                    "reviewed": None,
                    "version": version,
                },
                "default_locale": "en-US",
                "name": {"en-US": f"Firefox Language Pack for {locale}"},
                "guid": f"langpack-{locale}@firefox.mozilla.org",
                "slug": f"firefox-langpack-{locale.lower()}",
                "target_locale": locale,
                "type": "language",
                "url": f"https://addons.mozilla.org/en-US/firefox/addon/firefox-langpack-{locale.lower()}/",
            }
        )

    return results


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument(
        "--check",
        action="store_true",
        help="Exit 1 if the output would change (dry-run)",
    )
    args = parser.parse_args()

    results = fetch_langpacks()
    payload = json.dumps({"results": results}, indent=2)

    if args.check:
        existing = args.out.read_text() if args.out.exists() else ""
        if payload != existing:
            print("Output has changed.")
            sys.exit(1)
        print("Output is up to date.")
        return

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(payload)
    print(f"Wrote {len(results)} langpacks to {args.out}")


if __name__ == "__main__":
    main()
