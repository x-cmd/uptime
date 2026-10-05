---
x-title: The x-cmd/uptime catalog — schema, queries, contributions
x-desc: A deep dive on data/index.yml (the curated source) and data/index.tsv (the generated flat catalog). Schema reference, awk query recipes, api_type taxonomy, region filtering, and the contribution flow.
x-sidebar: The catalog
x-keywords: data index yml, data index tsv, schema, awk queries, atlassian statuspage, statuspal, region filter, contributing
x-json-ld:
  '@context': https://schema.org
  '@graph':
    - '@type': TechArticle
      headline: 'The x-cmd/uptime catalog — schema, queries, contributions'
      inLanguage: 'en'
      about: 'The data catalog inside x-cmd/uptime'
---

# The `x-cmd/uptime` catalog

> **What this article covers.** The first article
> ([`1-uptime-content`](../1-uptime-content/1-uptime-content.en.md))
> gave the high-level picture. This one dives into the catalog itself —
> every field, every query pattern, every contribution knob.

The catalog is the **first view** of this repo. It is a small
YAML file, [`data/index.yml`](../../data/index.yml), and a flat
TSV generated from it,
[`data/index.tsv`](../../data/index.tsv). The TSV is what a future
`x uptime` shell command and the live panel at
[`x-cmd.com/uptime`](https://x-cmd.com/uptime) will consume.

## 1. `data/index.yml` — the curated source

The YAML is grouped by category. There are three categories today
(`cloud`, `ai`, `other`); adding a fourth is a one-line change. Each
entry is a flat mapping.

```yaml
cloud:
  - name: aliyun
    homepage: https://www.aliyun.com
    statuspage: https://status.aliyun.com
    api_type: custom-json
    api_url: https://status.aliyun.com/api/v1/status
    region: cn
```

### Field reference

| Field | Required | Type | Meaning |
|---|---|---|---|
| `name` | yes | str | Lowercase slug used as the row's primary key. Stable — don't rename without a heads-up in the PR. |
| `homepage` | yes | url | Vendor's main website (not the status page). |
| `statuspage` | yes | url | Vendor's human-readable status page. The URL a user would open in a browser. |
| `api_type` | yes | enum | One of `atlassian-statuspage`, `custom-json`, `statuspal`, `rss`. See §3 for when to pick each. |
| `api_url` | yes | url | The machine-readable status endpoint. For `atlassian-statuspage` the convention is `<statuspage-host>/api/v2/summary.json`. |
| `region` | no | str | `cn` for mainland-China vendors, `global` for everywhere else. Used by the upcoming live panel's region filter. Empty is allowed for vendors that span both. |

CI rejects duplicates within a category — `(category, name)` must
be unique across the file. CI also rejects entries that miss a
required field; the error message names the file and the field.

## 2. `data/index.tsv` — the generated flat form

The TSV is a 7-column file regenerated on every push that touches
`data/index.yml` or the build script. The full pipeline lives in
[`.github/workflows/index-tsv.yml`](../../.github/workflows/index-tsv.yml).

```
name    category    homepage    statuspage    api_type    api_url    region
aliyun  cloud       https://www.aliyun.com    https://status.aliyun.com    custom-json    https://status.aliyun.com/api/v1/status    cn
aws     cloud       https://aws.amazon.com    https://health.aws.amazon.com    custom-json    https://health.aws.amazon.com/public/currentevent    global
openai  ai          https://openai.com    https://status.openai.com    atlassian-statuspage    https://status.openai.com/api/v2/summary.json    global
```

**Always edit `index.yml`.** Manual edits to `index.tsv` will be
silently overwritten on the next push. The CI's `--check` flag also
fails any PR that ships a stale `index.tsv`.

### Why a separate TSV

The YAML is for humans; the TSV is for `awk`, `grep`, `sort`, and
shell pipelines. A flat, sorted, tab-separated file is the simplest
form that supports both human inspection and machine processing
without parsing YAML at every shell call.

## 3. The `api_type` taxonomy

Four values, each with a strict meaning:

| `api_type` | When to use | URL shape |
|---|---|---|
| `atlassian-statuspage` | The status page is hosted on Atlassian Statuspage (the product behind statuspage.io). Most major SaaS vendors. | `<host>/api/v2/summary.json` returns JSON with `status.indicator` (`none` / `minor` / `major` / `critical`) and `status.description`. |
| `custom-json` | The vendor has a bespoke JSON endpoint that does not match the Atlassian format. AWS, GCP, and Aliyun are in this bucket. | Varies; the live panel will normalize this with per-vendor parsers. |
| `statuspal` | The vendor is on [Statuspal](https://statuspal.com). | `<host>/api/v1/status` (JSON). |
| `rss` | The vendor publishes only an Atom/RSS feed (no JSON). Rare. | The live panel will need a feed parser. |

If you find a vendor whose endpoint does not fit any of these, add
a new `api_type` value and mention the normalization needed in the
PR — the live panel's parser table is the contract that has to grow.

## 4. Common `awk` queries

The TSV has a header row; skip it with `NR > 1`.

```sh
BASE='https://raw.githubusercontent.com/x-cmd/uptime/main/data/index.tsv'

# All providers, name + status URL only
curl -fsSL "$BASE" | awk -F'\t' 'NR > 1 { print $1, $4 }'

# Where do I check OpenAI's status?
curl -fsSL "$BASE" | awk -F'\t' '$1 == "openai" { print $4 }'

# All cn-region cloud providers
curl -fsSL "$BASE" | awk -F'\t' '$2 == "cloud" && $7 == "cn"'

# All providers whose status JSON follows the atlassian pattern
curl -fsSL "$BASE" | awk -F'\t' '$5 == "atlassian-statuspage" { print $1, $6 }'

# Count providers per category
curl -fsSL "$BASE" | awk -F'\t' 'NR > 1 { print $2 }' \
  | sort | uniq -c | sort -rn

# Which vendors use the same API shape? (group by api_type)
curl -fsSL "$BASE" | awk -F'\t' 'NR > 1 { print $5 }' \
  | sort | uniq -c | sort -rn
```

These recipes work on the file as-fetched; no parsing, no Python,
no jq. If you want JSON instead, the future `x uptime` shell
command will produce it from the same TSV.

## 5. Region filtering

Two regions today: `cn` and `global`. The intended use:

- The live panel at `x-cmd.com/uptime` will expose a region
  toggle. `cn` shows mainland-China vendors that may be slow or
  blocked outside the GFW; `global` shows everywhere else. Some
  vendors (those with both a global and a cn status surface, like
  Aliyun's overseas presence) are `global`.
- If a vendor has a separate status page per region, the entry
  should either pick one canonical surface (preferred) or list the
  vendors under multiple names — but the latter is currently
  disallowed by the uniqueness check.

To find the `cn` slice today:

```sh
curl -fsSL "$BASE" | awk -F'\t' 'NR > 1 && $7 == "cn" { print $1, $4 }'
```

## 6. Contributing a new provider

Open a PR that touches **only** `data/index.yml`. CI handles the
rest. The full rule set is in
[`CONTRIBUTING.md`](../../CONTRIBUTING.md), but the short version:

1. Append one entry under the right category.
2. All required fields present; correct `api_type` enum value.
3. The `statuspage` URL must resolve (a typo here breaks the live
   panel for that provider).
4. The `api_url` must exist (the live panel will probe it; a 404
   will light up red on the first cycle and stay red).

PR template (please include):

```
- provider: <name>
- category: <cloud | ai | other>
- api_type: <enum>
- statuspage: <URL you verified by opening in a browser>
- api_url: <URL you verified by curl-ing a 2xx response>
```

If you find that a vendor's `api_url` has changed since the entry
was last curated, that's a one-line fix — same flow.

## 7. How the catalog feeds the live panel

The flow today:

1. PR touches `data/index.yml`.
2. CI validates schema, regenerates `data/index.tsv`, commits.

The flow planned for the next phase:

1. A separate GitHub Action reads `data/index.tsv`, fans out to
   each `api_url`, normalizes the response into `{status, fetched_at,
   indicator}`, and writes `status-live.json`.
2. The live panel at `x-cmd.com/uptime` reads `status-live.json`,
   joins it with `data/index.tsv` for the human-friendly fields,
   and renders red / yellow / green per provider.

`status-live.json` will be published to a `gh-pages` branch (the
working hypothesis) so the panel can fetch it without
authentication. The contract is documented here as it firms up.

## Related resources

- [`data/index.yml`](../../data/index.yml) — the curated source.
- [`data/index.tsv`](../../data/index.tsv) — the generated TSV.
- [`.x-cmd/build-index-tsv.py`](../../.x-cmd/build-index-tsv.py) — the generator.
- [`.github/workflows/index-tsv.yml`](../../.github/workflows/index-tsv.yml) — CI.
- [`CONTRIBUTING.md`](../../CONTRIBUTING.md) — adding a provider.
- [`SKILL.md`](../../SKILL.md) — TSV schema reference.

## License

This article is part of the `x-cmd/uptime` repo and is licensed under
Apache License 2.0.
