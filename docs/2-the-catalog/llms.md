---
name: 2-the-catalog
description: Deep dive on the data/index.yml schema (every field explained), the api_type taxonomy (atlassian-statuspage / custom-json / statuspal / rss), awk query recipes for data/index.tsv, region filtering (cn / global), and the contribution flow.
type: summary
---

# Core Content

core_features:

- 7-column TSV schema: name, category, homepage, statuspage, api_type, api_url, region
- Required vs optional fields with strict validation (CI rejects duplicates and missing fields)
- api_type taxonomy of 4 values with a strict meaning each
- awk query recipes that work on the file as-fetched (no Python, no jq)
- Region filter (`cn` vs `global`) that the live panel at x-cmd.com/uptime will expose
- Contribution flow: edit data/index.yml only; CI regenerates data/index.tsv; PR template provided
- Two-phase pipeline: catalog TSV (today) → status-live.json from a separate GitHub Action (planned)

## Key Information

highlights:

- The catalog lives in two forms: YAML for humans, TSV for awk/grep/sort
- Always edit data/index.yml; CI will overwrite any hand-edits to data/index.tsv
- The 4 api_type values map to vendor status-API shapes (atlassian-statuspage is the most common)
- atlassian-statuspage responses have `status.indicator` (`none` / `minor` / `major` / `critical`) — the live panel will read this
- Region tagging is single-valued today; a vendor that splits by region should pick one canonical surface
- The status-live.json pipeline (separate from the index.tsv pipeline) is the next phase and will live on a `gh-pages` branch

## Use Cases

use_cases:

- Looking up "where do I check vendor X's status?" without guessing subdomains
- Filtering the catalog by region (`cn` / `global`) for a panel UI
- Grouping vendors by API shape to estimate work for the live-panel parser
- Contributing a new provider via PR with a documented schema
- Auditing which providers have changed their `api_url` over time (`git log -p data/index.yml`)

## Related Resources

official:
  website: <https://x-cmd.com/uptime>
  repo: <https://github.com/x-cmd/uptime>
related:
  index_yml: <https://github.com/x-cmd/uptime/blob/main/data/index.yml>
  index_tsv: <https://github.com/x-cmd/uptime/blob/main/data/index.tsv>
  build_script: <https://github.com/x-cmd/uptime/blob/main/.x-cmd/build-index-tsv.py>
  workflow: <https://github.com/x-cmd/uptime/blob/main/.github/workflows/index-tsv.yml>
  contributing: <https://github.com/x-cmd/uptime/blob/main/CONTRIBUTING.md>

## Summary

The second article in the x-cmd/uptime topic library. It treats the data catalog as the central asset of the repo: a hand-curated YAML (`data/index.yml`) that is regenerated into a flat TSV (`data/index.tsv`) on every push via `.github/workflows/index-tsv.yml`. The article is the canonical reference for the 7-column TSV schema, the 4-value `api_type` taxonomy (atlassian-statuspage / custom-json / statuspal / rss), and the awk query recipes that work without parsing. It also documents the contribution flow (edit YAML only) and the planned second pipeline — a separate GitHub Action that will fan out to each `api_url`, normalize responses into `status-live.json`, and feed the live panel at x-cmd.com/uptime. Each recipe and PR-template ships ready to copy.
