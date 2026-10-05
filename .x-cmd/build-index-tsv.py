#!/usr/bin/env python3
"""
build-index-tsv.py — Convert data/index.yml (curated) to data/index.tsv (flat).

Output TSV columns (tab-separated):
    name        provider slug
    category    cloud | ai | other | ...
    homepage    vendor's main website
    statuspage  vendor's human-readable status page
    api_type    atlassian-statuspage | custom-json | statuspal | rss
    api_url     machine-readable status JSON endpoint
    region      cn | global (empty if not set)

Rows are sorted by (category, name) — both case-insensitive, both ascending —
so `awk`/`sort` consumers get stable output.

Required fields per entry: name, homepage, statuspage, api_type, api_url.
Optional: region.

Usage:
    python3 .x-cmd/build-index-tsv.py            # write data/index.tsv
    python3 .x-cmd/build-index-tsv.py --check    # exit non-zero if TSV is stale
    python3 .x-cmd/build-index-tsv.py --stdout   # write to stdout instead of file
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

DEFAULT_YML = Path(__file__).resolve().parent.parent / "data" / "index.yml"
DEFAULT_TSV = Path(__file__).resolve().parent.parent / "data" / "index.tsv"

REQUIRED_FIELDS = ("name", "homepage", "statuspage", "api_type", "api_url")
OPTIONAL_FIELDS = ("region",)
TSV_COLUMNS = ("name", "category", "homepage", "statuspage", "api_type", "api_url", "region")


def load_yaml(path: Path) -> dict:
    """Minimal YAML loader — only handles the subset we use:
    top-level mapping of category -> list[ flat-mapping ].

    Avoids PyYAML to keep CI on Python stdlib only.
    """
    if not path.is_file():
        raise FileNotFoundError(f"index.yml not found: {path}")

    out: dict[str, list[dict]] = {}
    current_category: str | None = None
    in_list = False

    for raw in path.read_text(encoding="utf-8").splitlines():
        # Drop comments and trailing whitespace.
        line = raw.split("#", 1)[0].rstrip()
        if not line.strip():
            continue

        # Top-level category key (e.g. "cloud:").
        if not line.startswith(" ") and line.endswith(":"):
            current_category = line[:-1].strip()
            if not current_category:
                raise ValueError(f"empty category name near: {raw!r}")
            out[current_category] = []
            in_list = True
            continue

        # Entry start (e.g. "  - name: aliyun").
        if line.lstrip().startswith("- "):
            if current_category is None:
                raise ValueError(f"list entry outside a category: {raw!r}")
            entry: dict[str, str] = {}
            rest = line.lstrip()[2:]  # strip leading "- "
            if ":" in rest:
                k, v = rest.split(":", 1)
                entry[k.strip()] = v.strip()
            out[current_category].append(entry)
            continue

        # Continuation / nested field (e.g. "    homepage: https://...").
        if in_list and current_category is not None and out[current_category]:
            if ":" in line:
                k, v = line.strip().split(":", 1)
                out[current_category][-1][k.strip()] = v.strip()
            continue

        raise ValueError(f"unrecognized line: {raw!r}")

    return out


def validate(catalog: dict[str, list[dict]]) -> list[tuple[str, str, dict]]:
    """Validate the catalog. Returns the flat list of (category, name, entry)
    rows; raises ValueError on the first missing-required-field.
    """
    rows: list[tuple[str, str, dict]] = []
    seen: set[tuple[str, str]] = set()
    for category, entries in catalog.items():
        if not isinstance(entries, list):
            raise ValueError(f"category {category!r} must map to a list, got {type(entries).__name__}")
        for entry in entries:
            for field in REQUIRED_FIELDS:
                if field not in entry or not str(entry[field]).strip():
                    raise ValueError(f"{category}/{entry.get('name', '?')}: missing required field {field!r}")
            name = str(entry["name"]).strip()
            key = (category, name)
            if key in seen:
                raise ValueError(f"duplicate entry: {category}/{name}")
            seen.add(key)
            rows.append((category, name, entry))
    return rows


def rows_for_tsv(rows: list[tuple[str, str, dict]]) -> list[list[str]]:
    """Project + sort rows into TSV-shaped lists."""
    sorted_rows = sorted(rows, key=lambda r: (r[0].lower(), r[1].lower()))
    out = []
    for category, _name, entry in sorted_rows:
        out.append([str(entry.get(col, "") if col != "category" else category).strip() for col in TSV_COLUMNS])
    return out


def render_tsv(rows: list[list[str]]) -> str:
    """Render rows as a TSV string with a header line + trailing newline."""
    lines = ["\t".join(TSV_COLUMNS)]
    for r in rows:
        # TSV: tabs in fields would break the format; replace defensively.
        lines.append("\t".join(c.replace("\t", " ").replace("\n", " ") for c in r))
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Build data/index.tsv from data/index.yml.")
    parser.add_argument("--yml", type=Path, default=DEFAULT_YML, help="input YAML path")
    parser.add_argument("--tsv", type=Path, default=DEFAULT_TSV, help="output TSV path")
    parser.add_argument("--check", action="store_true", help="exit non-zero if TSV would change")
    parser.add_argument("--stdout", action="store_true", help="write to stdout instead of file")
    args = parser.parse_args()

    catalog = load_yaml(args.yml)
    rows = validate(catalog)
    tsv_rows = rows_for_tsv(rows)
    rendered = render_tsv(tsv_rows)

    if args.stdout or args.check:
        sys.stdout.write(rendered)
        if args.check:
            try:
                existing = args.tsv.read_text(encoding="utf-8")
            except FileNotFoundError:
                sys.stderr.write(f"--check: {args.tsv} does not exist (would be created)\n")
                return 1
            if existing != rendered:
                sys.stderr.write(f"--check: {args.tsv} is stale; run without --check to regenerate\n")
                return 1
            return 0
        return 0

    args.tsv.write_text(rendered, encoding="utf-8")
    sys.stderr.write(f"wrote {args.tsv} ({len(tsv_rows)} rows)\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
