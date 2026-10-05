---
x-title: Uptime, status pages, and monitoring
x-desc: What uptime means at three levels — the local `uptime(1)` command, the catalog of provider status pages in this repo, and the practical how-to of monitoring your own services (self-hosted tools, GitHub Actions).
x-sidebar: Uptime — basics & monitoring
x-keywords: uptime, status page, monitoring, uptime-kuma, github actions, cron, health check, observability
x-json-ld:
  '@context': https://schema.org
  '@graph':
    - '@type': TechArticle
      headline: 'Uptime, status pages, and monitoring'
      inLanguage: 'en'
      about: 'Uptime and service monitoring'
---

# Uptime, status pages, and monitoring

> **TL;DR.** Uptime is the same word at three different scales. (1) The local
> [`uptime(1)`](https://man.x-cmd.com/man1/uptime) command tells you how long
> your box has been running. (2) A **status page** tells you whether a service
> you depend on is alive. (3) A **monitor** tells you, automatically, the
> moment something you care about stops responding. This page covers all three,
> with copy-paste recipes for the third.

This is the first article in the uptime topic library. Articles here are
content-only and open for modification PRs — see
[`CONTRIBUTING.md`](../../CONTRIBUTING.md).

## 1. Local `uptime(1)` and `x uptime`

### The standard `uptime(1)` command

Every Unix-like system ships with a small program called `uptime`. It
reads `/proc/uptime` and prints three things:

- how long the system has been up (in `dd:hh:mm` form),
- how many users are logged in,
- the load average over the last 1, 5, and 15 minutes.

```sh
$ uptime
22:14:03 up 47 days,  3:12,  4 users,  load average: 0.12, 0.18, 0.21
```

The man page at
[`man.x-cmd.com/man1/uptime`](https://man.x-cmd.com/man1/uptime) is the
canonical reference. The output is identical across `uptime`,
`w`, and `top`'s first line — they all read the same kernel state.

### `x uptime` — the x-cmd enhancement

[`x uptime`](https://x-cmd.com/mod/uptime) is the x-cmd wrapper. It
adds formatting options, JSON output for piping, and (in the future)
the ability to overlay provider status from this repo's catalog.

```sh
# Same as `uptime(1)`:
x uptime

# Machine-readable:
x uptime --json

# Pretty / colorized:
x uptime --pretty
```

The planned deeper integration: `x uptime` reads
[`data/index.tsv`](../../data/index.tsv) from this repo and lets you
ask "is OpenAI alive right now?" with a single call — the same
question the upcoming live panel at `x-cmd.com/uptime` answers in
the browser.

## 2. The provider status-page catalog

### What is in this repo

This repo holds a hand-curated catalog of developer-service status
pages under [`data/index.yml`](../../data/index.yml). The catalog is
grouped into three top-level categories:

| Category | What it covers |
|---|---|
| `cloud` | Cloud providers (Aliyun, AWS, GCP, Azure, Cloudflare, etc.) |
| `ai` | AI model providers (OpenAI, Anthropic, Gemini, DeepSeek, Qwen) |
| `other` | Adjacent tools (GitHub, GitLab, Vercel, Stripe, ...) |

The flat, generated form is
[`data/index.tsv`](../../data/index.tsv) — one row per provider,
seven columns. The schema is documented in
[`SKILL.md`](../../SKILL.md).

### Why a curated catalog

When something you depend on breaks, you want one URL to open, not
a guess at which subdomain of which vendor hosts their status page.
This repo solves the "where do I check?" question by centralizing
the answers:

```sh
# What providers are tracked?
curl -fsSL https://raw.githubusercontent.com/x-cmd/uptime/main/data/index.tsv \
  | awk -F'\t' 'NR > 1 { print $1 }'

# Where do I check OpenAI's status?
curl -fsSL https://raw.githubusercontent.com/x-cmd/uptime/main/data/index.tsv \
  | awk -F'\t' '$1 == "openai" { print $4 }'
# → https://status.openai.com
```

The `api_url` column is what a future GitHub Action will hit every
ten minutes to fetch the live indicator (green / yellow / red). The
first version of that pipeline is the next phase of this repo.

### The upcoming live panel at x-cmd.com/uptime

The static catalog above is the **first** view. The **second** view
— currently under construction — is a live panel at
[`x-cmd.com/uptime`](https://x-cmd.com/uptime) that shows red /
yellow / green lights for every provider in the catalog, with
search, a card layout, and slots for sponsored providers. The
panel will read `status-live.json` (also produced by a future
GitHub Action in this repo) and render it client-side.

If you maintain a provider and want it included, open a PR adding
it to `data/index.yml` — see [`CONTRIBUTING.md`](../../CONTRIBUTING.md).

## 3. Monitoring your own website

For your own services, the question is the inverse: instead of
checking on someone else, you want something that pings **you** and
screams when **you** go down. The options fall into three buckets.

### Self-hosted: a server you run

| Tool | Stack | Notes |
|---|---|---|
| [**Uptime Kuma**](https://github.com/louislam/uptime-kuma) | Node.js + SQLite | The default modern choice. Beautiful UI, Docker image, status page as a side effect. ~50k GitHub stars, very active. |
| [**Beszel**](https://github.com/henrygd/beszel) | Go + SQLite | Lightweight, adds server-resource monitoring (CPU, RAM, disk) alongside HTTP checks. |
| **statping / statping-ng** | Go | The original "self-hosted status page". Maintenance is patchy; consider uptime-kuma instead. |
| **Prometheus + blackbox_exporter** | Go | The "heavy" option. Worth it when you already run Prometheus. |

For most small-to-medium sites, **Uptime Kuma** is the right answer:
one `docker run`, a status page comes out the other side, and you
get Telegram / Slack / email / Discord alerts in the same UI.

### Cron-style: just notify if a heartbeat stops

When you care about "did my cron job actually run?" rather than "is
my HTTP endpoint responding?", a different class of tool fits:

- [**Healthchecks.io**](https://healthchecks.io/) — free for open
  use; you ping a URL when a job starts, ends, or fails. Alerts you
  when a ping doesn't arrive.
- [**Cronitor**](https://cronitor.io/) — similar shape, more
  enterprise-oriented.
- **Dead Man's Snitch** — the original commercial offering;
  acquired by Sentry.

These are the right answer when the failure mode is "the job didn't
run at all" rather than "the server is down."

### Hosted: pay someone else to do it

If you don't want to run anything yourself:

- [**UptimeRobot**](https://uptimerobot.com/) — free tier covers 50
  monitors at 5-minute intervals.
- [**Better Stack**](https://betterstack.com/uptime) — modern
  hosted alternative with status-page-as-a-product.
- [**Better Uptime**](https://betteruptime.com/) — on-call + status
  page bundle.

Hosted monitors have one downside the self-hosted ones don't: when
**your** account with the hosted monitor is down (or you've been
billed past the grace period), your monitoring is also down. A
defense-in-depth setup pairs a hosted monitor with a GitHub Actions
cron (see below) — two independent systems.

## 4. Monitoring via GitHub Actions

GitHub Actions cron triggers aren't a replacement for a real monitor,
but they are a useful **second layer** of defense: independent of
your hosting provider, independent of your DNS, and free up to the
Actions minute cap.

### Minimal: ping a URL every 5 minutes

```yaml
# .github/workflows/uptime-ping.yml
name: uptime-ping
on:
  schedule:
    # Every 5 minutes. GitHub's cron is UTC; leading minute offset
    # avoids collisions with the rest of the ecosystem.
    - cron: '7,12,17,22,27,32,37,42,47,52,57 * * * *'
  workflow_dispatch:

jobs:
  ping:
    runs-on: ubuntu-latest
    timeout-minutes: 2
    steps:
      - name: Probe target
        run: |
          status=$(curl -fsSL -o /dev/null -w '%{http_code}' \
                    --max-time 10 \
                    https://example.com/healthz)
          if [ "$status" != "200" ]; then
            echo "::error::target returned $status"
            exit 1
          fi
```

Save this as `.github/workflows/uptime-ping.yml` in any repo and it
will probe the URL every 5 minutes. If the probe fails, the run
fails and shows up in the Actions tab.

**Caveat:** GitHub does not guarantee cron trigger timing. The
[official docs](https://docs.github.com/actions/using-workflows/events-that-trigger-workflows#schedule)
explicitly note that "the longest time you should expect is around
40 minutes on average, but it can be as long as several hours." For
true SLA-grade monitoring, use a dedicated monitor. For "I want a
cheap second opinion," GitHub Actions cron is fine.

### Better: open a GitHub Issue on failure

Email is unreliable in 2026. Issue-tracking survives.

```yaml
# .github/workflows/uptime-alert.yml
name: uptime-alert
on:
  schedule:
    - cron: '*/5 * * * *'

jobs:
  alert:
    runs-on: ubuntu-latest
    timeout-minutes: 2
    steps:
      - name: Probe
        id: probe
        run: |
          code=$(curl -fsSL -o /dev/null -w '%{http_code}' \
                  --max-time 10 https://example.com/healthz || echo 000)
          echo "code=$code" >> "$GITHUB_OUTPUT"
      - name: Open issue if down
        if: steps.probe.outputs.code != '200'
        uses: actions/github-script@v7
        with:
          script: |
            await github.rest.issues.create({
              owner: context.repo.owner,
              repo: context.repo.repo,
              title: `Target returned ${process.env.CODE}`,
              body: 'The uptime cron detected a non-200 response. ' +
                    'Inspect the run, then close this issue when fixed.',
              labels: ['uptime', 'incident']
            });
        env:
          CODE: ${{ steps.probe.outputs.code }}
```

Each outage produces an issue. You pin the issue to the repo, tag
it `incident`, and the team's notification flow picks it up.

### Even better: a status badge from a public endpoint

For a public-facing badge ("99.9% uptime") you'll need historical
state. The cheapest option that does not require running a server:

- Use the GitHub workflow to push a row into a CSV in the repo
  (one commit per probe — squash in a daily workflow to keep noise
  down).
- Or use a third-party like
  [atlassian-statuspage](https://www.statuspage.io) which itself
  consumes the probe output via webhook.

This is enough for a personal site. For a product with paying
customers, the table in §3 is the right starting point.

## Related resources

- [`data/index.tsv`](../../data/index.tsv) — the curated catalog.
- [`data/index.yml`](../../data/index.yml) — the YAML source.
- [`SKILL.md`](../../SKILL.md) — schema + common agent queries.
- [`CONTRIBUTING.md`](../../CONTRIBUTING.md) — add a provider or article.
- [Uptime Kuma](https://github.com/louislam/uptime-kuma) — the
  default self-hosted monitor.
- [GitHub Actions: scheduled events](https://docs.github.com/actions/using-workflows/events-that-trigger-workflows#schedule)
  — the timing caveats.

## License

This article is part of the `x-cmd/uptime` repo and is licensed under
Apache License 2.0.
