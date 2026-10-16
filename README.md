# x-cmd/uptime

<!-- uptime-catalog-as-of:START -->
**Catalog as of: 2026-10-06** _(16 providers across 3 categories: cloud, ai, other)_
<!-- uptime-catalog-as-of:END -->

> 🌐 **中文版：[README.cn.md](./README.cn.md)** —— same catalog, Chinese front matter.

>
> - **[The 16 providers](#the-16-providers)** — what the catalog covers today, grouped by category.
> - **[API surface](#api-surface)** — how many providers expose each `api_type` shape.
> - **[Regional coverage](#regional-coverage)** — `cn` vs `global` split.
> - **[Reports](#reports)** — the raw TSV behind the tables above.
> - **[About x-cmd/uptime](#about-xcmduptime)** — this repo is the producer.
> - **[FAQ](#faq)** — the questions people actually ask.
>
> For end users: [`SKILL.md`](./SKILL.md) (raw TSV recipes). For developers: [`CONTRIBUTING.md`](./CONTRIBUTING.md) (catalog schema + 4-tuple article convention).

## The 16 providers

> The catalog below is generated from [`data/index.yml`](./data/index.yml)
> and rendered into [`data/index.tsv`](./data/index.tsv) on every push via
> [`.github/workflows/index-tsv.yml`](./.github/workflows/index-tsv.yml).
> Open `data/index.tsv` for the machine-readable form, or read on for the
> human-readable snapshot.

<!-- BEGIN data/catalog.snapshot.md -->

### ai (5)

| Provider | Status page |
| --- | --- |
| anthropic | https://status.anthropic.com |
| deepseek | https://status.deepseek.com |
| gemini | https://status.gemini.google.com |
| openai | https://status.openai.com |
| qwen | https://status.alibabacloud.com |

### cloud (7)

| Provider | Status page |
| --- | --- |
| aliyun | https://status.aliyun.com |
| aws | https://health.aws.amazon.com |
| azure | https://status.azure.com |
| cloudflare | https://www.cloudflarestatus.com |
| gcp | https://status.cloud.google.com |
| huawei-cloud | https://status.huaweicloud.com |
| tencent-cloud | https://status.cloud.tencent.com |

### other (4)

| Provider | Status page |
| --- | --- |
| github | https://www.githubstatus.com |
| gitlab | https://status.gitlab.com |
| stripe | https://status.stripe.com |
| vercel | https://www.vercel-status.com |

<!-- END data/catalog.snapshot.md -->

## API surface

> Each provider exposes one of four `api_type` values — the shape
> the future live-status pipeline will have to parse. The table
> below is regenerated from `data/index.tsv`.

<!-- BEGIN data/api-type.snapshot.md -->

| `api_type` | Count | Examples |
| --- | ---: | --- |
| `atlassian-statuspage` | 10 | anthropic, azure, cloudflare, gemini, github, gitlab, openai, stripe, tencent-cloud, vercel |
| `custom-json` | 6 | aliyun, aws, deepseek, gcp, huawei-cloud, qwen |

<!-- END data/api-type.snapshot.md -->

For a worked example of parsing each `api_type`, see
[`docs/2-the-catalog/en.md`](./docs/2-the-catalog/en.md#3-the-api_type-taxonomy).

## Regional coverage

<!-- BEGIN data/region.snapshot.md -->

| Region | Count |
| --- | ---: |
| `cn` | 5 |
| `global` | 11 |

<!-- END data/region.snapshot.md -->

The future live panel at `x-cmd.com/uptime` will expose a region
toggle that filters by this column. Vendors with separate status
pages per region should pick one canonical surface.

## Reports

The catalog lives in two forms, both committed to the repo:

| File | Format | Purpose |
| --- | --- | --- |
| [`data/index.yml`](./data/index.yml) | YAML (hand-curated) | The source of truth — edit this to add a provider. |
| [`data/index.tsv`](./data/index.tsv) | TSV (auto-generated) | The flat form for `awk` / `x uptime` shell consumption. |

Planned for the next phase (not in this repo yet):

| File | Format | Purpose |
| --- | --- | --- |
| `status-live.json` | JSON (auto-generated) | Live indicator per provider, refreshed every 10 minutes by a separate GitHub Action. The `x-cmd.com/uptime` panel will read this. |

## About x-cmd/uptime

This repo is the **producer** for the upcoming status-page hub at
[`x-cmd.com/uptime`](https://x-cmd.com/uptime):

1. It holds the hand-curated catalog of provider status pages
   ([`data/index.yml`](./data/index.yml)).
2. CI regenerates [`data/index.tsv`](./data/index.tsv) on every
   push ([`.github/workflows/index-tsv.yml`](./.github/workflows/index-tsv.yml)).
3. A separate GitHub Action (planned) will fetch live status from
   each provider's `api_url` every 10 minutes and produce
   `status-live.json`.
4. The consumer is the future Web App at `x-cmd.com/uptime` —
   cards with red / yellow / green lights, search, and slots for
   sponsored providers.
5. The companion shell module is [`x uptime`](https://x-cmd.com/mod/uptime).

### How users get uptime data (the 4 ways)

```sh
# 1. Browse — open README.md or x-cmd.com/uptime directly.

# 2. Fetch the TSV over HTTPS — pipe into awk for filtering.
curl -fsSL https://raw.githubusercontent.com/x-cmd/uptime/main/data/index.tsv

# 3. Read the topic articles — see docs/ for the 7 articles that
#    cover self-hosted / hosted / cron-style / GitHub Actions monitoring.

# 4. Use the shell module (planned) — `x uptime <provider>` returns
#    the live status of one provider; `x uptime ls` lists all known.
```

No API keys, no auth, no background services. The catalog TSV is
plain text — `awk -F'\t'` works directly.

## Developer docs

- Adding a provider: [`CONTRIBUTING.md`](./CONTRIBUTING.md#1-add-a-provider)
- TSV schema + agent recipe: [`SKILL.md`](./SKILL.md)
- Article workflow + frontmatter spec: [`CONTRIBUTING.md`](./CONTRIBUTING.md#2-write-an-article)
- Pipeline scripts: [`.x-cmd/build-index-tsv.py`](./.x-cmd/build-index-tsv.py)

## License

Apache License 2.0 — see [`LICENSE`](./LICENSE).

## Related

- [`x-cmd/cve`](https://github.com/x-cmd/cve) — topic library (canonical pattern reference).
- [`x-cmd/seo`](https://github.com/x-cmd/seo) — topic library (canonical pattern reference).
- [`x-cmd/mneme/AGENTS.md`](https://github.com/x-cmd/mneme/blob/main/AGENTS.md) — public org map and topic-library convention.
- Rendered site: <https://x-cmd.com/uptime>
- Upcoming shell module: <https://x-cmd.com/mod/uptime>

## FAQ

### What is this repo?

`x-cmd/uptime` is the source repo for `x-cmd.com/uptime` — a status-page hub and the data feed for the upcoming `x uptime` shell module. It holds a hand-curated catalog of provider status pages (cloud / AI / other), the topic articles on uptime and monitoring under `docs/`, and (planned) live status JSON that a separate GitHub Action will refresh every 10 minutes.

### Is the live status panel live yet?

Not yet. As of Phase A, the catalog and topic articles are in place; the live status panel at `x-cmd.com/uptime` is the next phase. PRs that touch `data/index.yml` trigger CI to regenerate `data/index.tsv` immediately.

### How do I add a provider?

Edit [`data/index.yml`](./data/index.yml), append one entry under the right category with the required fields (`name`, `homepage`, `statuspage`, `api_type`, `api_url`), and open a PR. CI validates the schema, regenerates `data/index.tsv`, and auto-commits. See [`CONTRIBUTING.md`](./CONTRIBUTING.md).

### Where do I check vendor X's status right now?

```sh
curl -fsSL https://raw.githubusercontent.com/x-cmd/uptime/main/data/index.tsv \
  | awk -F'\t' '$1 == "<name>" { print $4 }'
# returns the human-readable status page URL
```

The fourth column of `data/index.tsv` is the status page URL. The
sixth column is the machine-readable status JSON endpoint that the
future live pipeline will probe.

### What's the difference between `atlassian-statuspage`, `custom-json`, `statuspal`, and `rss`?

These are the four `api_type` values in the catalog. `atlassian-statuspage` is the most common (Statuspage.io / Atlassian Statuspage). `custom-json` is for vendors with a bespoke endpoint. `statuspal` is the [Statuspal](https://statuspal.com) shape. `rss` is for vendors that publish only a feed. See [`docs/2-the-catalog`](./docs/2-the-catalog/en.md#3-the-api_type-taxonomy).

### What's `region` for?

It tags providers as `cn` (mainland China) or `global`. The future live panel at `x-cmd.com/uptime` will expose a region toggle. Empty is allowed for vendors that span both.

### Where are the topic articles?

Under [`docs/`](./docs). The first article (`1-uptime-content`) is the overview; `2-the-catalog` dives into the data; `3-` to `6-` cover self-hosted, hosted, cron-style, and GitHub Actions monitors; `7-decision-guide` is the synthesis. Each article is a 4-tuple: `en.md`, `cn.md`, `llms.md`, `faq.yml` (the slot name is carried by the folder, not the files inside).
