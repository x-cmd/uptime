# Contributing to x-cmd/uptime

Thanks for helping. There are two kinds of contributions:

1. **Add a provider** to the catalog (`data/index.yml`).
2. **Write or fix an article** under `docs/`.

Both kinds of PRs go through the same review flow — open a PR against `main`, CI runs schema validation, a maintainer merges.

## 1. Add a provider

Edit `data/index.yml` and append one entry under the right category. The schema:

```yaml
cloud:                              # category (top-level key)
  - name: my-provider               # required — lowercase slug
    homepage: https://example.com   # required
    statuspage: https://status.example.com   # required — human-readable
    api_type: atlassian-statuspage  # required — see enum below
    api_url: https://status.example.com/api/v2/summary.json   # required
    region: global                  # optional — cn | global
```

Allowed `api_type` values:

| Value | When to use |
|---|---|
| `atlassian-statuspage` | Hosted on `statuspage.io` / Atlassian Statuspage; the `api_url` follows the `<host>/api/v2/summary.json` pattern. |
| `custom-json` | Vendor's bespoke JSON endpoint (shape not yet normalized). |
| `statuspal` | Hosted on `statuspal.com`. |
| `rss` | Only an RSS/Atom feed is exposed; no JSON endpoint. |

The `.github/workflows/index-tsv.yml` workflow will:

- Validate every required field is present.
- Reject duplicate `(category, name)` pairs.
- Regenerate `data/index.tsv` and auto-commit it on push.

You do not need to (and should not) edit `data/index.tsv` by hand — CI regenerates it. Manual edits to `data/index.tsv` will be silently overwritten on the next push.

If you find that a vendor's `api_url` has changed, please update `index.yml` and open a PR. This is the canonical source.

## 2. Write an article

Article slots live under `docs/<n>-<slug>/` (the leading integer is reading order). Each slot is **four files kept in sync**:

```
docs/<n>-<slug>/
├── <n>-<slug>.en.md        # English article body
├── <n>-<slug>.cn.md        # Chinese translation
├── <n>-<slug>.llms.md      # LLM-friendly summary (flat sections)
└── <n>-<slug>.faq.yml      # structured bilingual Q&A
```

Frontmatter (`.en.md` / `.cn.md`):

```yaml
---
x-title: <headline>
x-desc: <one-sentence summary>
x-sidebar: <sidebar label>
x-keywords: [comma, separated, keywords]
x-json-ld:
  '@context': https://schema.org
  '@graph':
    - '@type': TechArticle
      headline: <headline>
      inLanguage: <en | cn>
---
```

Frontmatter (`.llms.md`):

```yaml
---
name: <n>-<slug>
description: <one-line summary>
type: summary
---
```

Body uses flat sections: `core_features`, `highlights`, `use_cases`, `related_resources`, `summary`. See `x-cmd/cve/docs/0-cve-for-ai-builders.llms.md` for a worked example.

FAQ (`.faq.yml`): top-level `id: x-uptime-<n>-<slug>`, then `<data>:` (a list of groups). Each group has `name: {en, cn}` and a `qa:` list. Each QA entry has `id`, `question: {en, cn}`, `answer: {en, cn}`, `confidence` (1-9), and `reference:` (a list of files). Group by topic, not by FAQ-style alone.

The `.faq.yml` is rendered as the last section of the page body (not as a sidebar or accordion). Each entry should be self-contained — a reader scrolling to the FAQ section should not need to have read the body to follow.

If you change one file in the slot, change all four in the same commit.

## Data discipline

- `data/index.tsv` is generated. Do not edit it by hand.
- `data/` is for catalog data only — do not put scripts, screenshots, or vendor-specific blobs there.
- This is a public repo. Per `x-cmd/mneme/AGENTS.md`, all prose must be content-only: facts, tool usage, links. No strategic direction, no commercialization.

## Local sanity check

Before opening a PR:

```sh
python3 .x-cmd/build-index-tsv.py --check   # index.tsv is up to date
```

If `--check` fails, run without `--check` to regenerate, commit both files, and push.
