#!/usr/bin/env python3
"""
build-catalog-report.py — Generate report/catalog.report.md from data/index.tsv
and inject each section into README.md between matching BEGIN/END markers.

Output report sections:
    ## Catalog by category   ←→  <!-- BEGIN data/catalog.snapshot.md -->
    ## API surface           ←→  <!-- BEGIN data/api-type.snapshot.md -->
    ## Regional coverage     ←→  <!-- BEGIN data/region.snapshot.md -->

The script regenerates report/catalog.report.md on every run, then replaces
the content between the matching BEGIN/END markers in README.md. The markers
themselves stay — only the inner content rotates.

For the cve repo this pattern lives in `.github/workflows/release.yml`;
for uptime (Phase A, no live data yet) the trigger is the catalog itself:
whenever data/index.yml changes, CI regenerates index.tsv, then this script
regenerates the report and updates README.md in the same commit.

Usage:
    python3 .x-cmd/build-catalog-report.py
    python3 .x-cmd/build-catalog-report.py --check    # exit non-zero if README.md would change
    python3 .x-cmd/build-catalog-report.py --stdout   # write report to stdout, do not touch files
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

DEFAULT_TSV = Path(__file__).resolve().parent.parent / "data" / "index.tsv"
DEFAULT_REPORT = Path(__file__).resolve().parent.parent / "report" / "catalog.report.md"
DEFAULT_README = Path(__file__).resolve().parent.parent / "README.md"

# (marker_name, report_section_header). The order here is also the order in
# the generated report. Marker names must match exactly the strings used in
# README.md between <!-- BEGIN ... --> and <!-- END ... -->.
MARKER_PAIRS = [
    ("data/catalog.snapshot.md", "Catalog by category"),
    ("data/api-type.snapshot.md", "API surface"),
    ("data/region.snapshot.md", "Regional coverage"),
]


def load_tsv(path: Path) -> list[dict]:
    """Load the catalog TSV into a list of dicts. The first line is the header."""
    text = path.read_text(encoding="utf-8")
    lines = text.strip().split("\n")
    if len(lines) < 2:
        return []
    headers = lines[0].split("\t")
    return [dict(zip(headers, line.split("\t"))) for line in lines[1:]]


def section_catalog_by_category(rows: list[dict]) -> str:
    """Render a per-category breakdown: each category is its own H3 block
    with a name + statuspage table."""
    by_cat: dict[str, list[dict]] = {}
    for row in rows:
        by_cat.setdefault(row["category"], []).append(row)

    parts = ["## Catalog by category", ""]
    for cat in sorted(by_cat.keys(), key=str.lower):
        entries = sorted(by_cat[cat], key=lambda r: r["name"].lower())
        parts.append(f"### {cat} ({len(entries)})")
        parts.append("")
        parts.append("| Provider | Status page |")
        parts.append("| --- | --- |")
        for e in entries:
            parts.append(f"| {e['name']} | {e['statuspage']} |")
        parts.append("")
    return "\n".join(parts)


def section_api_type(rows: list[dict]) -> str:
    """Render the api_type distribution table."""
    by_type: dict[str, list[str]] = {}
    for row in rows:
        by_type.setdefault(row["api_type"], []).append(row["name"])

    parts = ["## API surface", ""]
    parts.append("| `api_type` | Count | Examples |")
    parts.append("| --- | ---: | --- |")
    for api_type in sorted(by_type.keys()):
        names = sorted(by_type[api_type], key=str.lower)
        if not names:
            examples = "_(none yet)_"
        elif len(names) <= 10:
            examples = ", ".join(names)
        else:
            examples = ", ".join(names[:10]) + f", … (+{len(names) - 10} more)"
        parts.append(f"| `{api_type}` | {len(names)} | {examples} |")
    parts.append("")
    return "\n".join(parts)


def section_region(rows: list[dict]) -> str:
    """Render the region distribution table."""
    by_region: dict[str, int] = {}
    for row in rows:
        region = (row.get("region") or "").strip() or "_(empty)_"
        by_region[region] = by_region.get(region, 0) + 1

    parts = ["## Regional coverage", ""]
    parts.append("| Region | Count |")
    parts.append("| --- | ---: |")
    for region in sorted(by_region.keys(), key=str.lower):
        parts.append(f"| `{region}` | {by_region[region]} |")
    parts.append("")
    return "\n".join(parts)


def render_report(rows: list[dict]) -> str:
    """Compose the full report file (header line + three sections)."""
    return "\n".join([
        "# Catalog report",
        "",
        "_Auto-generated from `data/index.tsv` by `.x-cmd/build-catalog-report.py`._",
        "",
        section_catalog_by_category(rows),
        section_api_type(rows),
        section_region(rows),
    ])


def extract_section(report_text: str, header: str) -> str:
    """Return the content of the H2 section whose header matches `header`,
    up to the next H2 or end of file. The returned content does NOT include
    the H2 line itself — only the body that lives between BEGIN/END markers."""
    pattern = re.compile(
        rf"## {re.escape(header)}\n(.*?)(?=\n## |\Z)",
        re.DOTALL,
    )
    m = pattern.search(report_text)
    if not m:
        raise ValueError(f"section {header!r} not found in report")
    return m.group(1).rstrip("\n") + "\n"


def inject_into_readme(readme_text: str, report_text: str) -> str:
    """For each marker pair, replace the content between the BEGIN/END markers
    with the corresponding section body from the report. The markers themselves
    are preserved."""
    for marker_name, header in MARKER_PAIRS:
        begin_marker = f"<!-- BEGIN {marker_name} -->"
        end_marker = f"<!-- END {marker_name} -->"

        begin_idx = readme_text.find(begin_marker)
        if begin_idx == -1:
            raise ValueError(f"{begin_marker!r} not found in README")
        end_idx = readme_text.find(end_marker, begin_idx)
        if end_idx == -1:
            raise ValueError(f"{end_marker!r} not found after {begin_marker!r}")

        section_body = extract_section(report_text, header)
        # Drop the BEGIN line itself, keep the newline, replace body, drop the
        # END line. Layout: "<!-- BEGIN ... -->\n<body>\n<!-- END ... -->"
        body_start = begin_idx + len(begin_marker)
        body_end = end_idx
        readme_text = (
            readme_text[:body_start]
            + "\n" + section_body
            + "\n" + readme_text[body_end:]
        )
    return readme_text


def main() -> int:
    parser = argparse.ArgumentParser(description="Build report/catalog.report.md from data/index.tsv and inject into README.md.")
    parser.add_argument("--tsv", type=Path, default=DEFAULT_TSV)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--readme", type=Path, default=DEFAULT_README)
    parser.add_argument("--check", action="store_true", help="exit non-zero if README.md or report would change")
    parser.add_argument("--stdout", action="store_true", help="write report to stdout, do not touch files")
    args = parser.parse_args()

    rows = load_tsv(args.tsv)
    report_text = render_report(rows)
    current_readme = args.readme.read_text(encoding="utf-8") if args.readme.is_file() else ""
    new_readme = inject_into_readme(current_readme, report_text) if current_readme else ""

    if args.stdout:
        sys.stdout.write(report_text)
        return 0

    args.report.parent.mkdir(parents=True, exist_ok=True)
    if args.check:
        current_report = args.report.read_text(encoding="utf-8") if args.report.is_file() else ""
        if current_report != report_text or current_readme != new_readme:
            sys.stderr.write(f"--check: {args.report} or {args.readme} would change; run without --check\n")
            return 1
        return 0

    args.report.write_text(report_text, encoding="utf-8")
    if new_readme and new_readme != current_readme:
        args.readme.write_text(new_readme, encoding="utf-8")
    sys.stderr.write(f"wrote {args.report}; updated {args.readme} ({len(rows)} rows)\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
