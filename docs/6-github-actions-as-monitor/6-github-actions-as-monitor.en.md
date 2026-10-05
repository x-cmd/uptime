---
x-title: GitHub Actions as a monitor
x-desc: "A second layer of defense, independent of your host and your DNS. Recipes: minimal ping, open-issue on failure, CSV row for badge, Slack webhook. Timing caveats, minute caps, security."
x-sidebar: GitHub Actions monitor
x-keywords: github actions, cron, scheduled events, uptime probe, slack webhook, status badge, csv, defense in depth
x-json-ld:
  '@context': https://schema.org
  '@graph':
    - '@type': TechArticle
      headline: 'GitHub Actions as a monitor'
      inLanguage: 'en'
      about: 'Using GitHub Actions cron as an uptime monitor'
---

# GitHub Actions as a monitor

> **What this article covers.** GitHub Actions cron is **not** a
> replacement for a dedicated monitor. It is a useful **second
> layer of defense**: independent of your hosting provider,
> independent of your DNS, free within the Actions minute cap.
> This article walks the recipes and the caveats.

The first article
([`1-uptime-content`](../1-uptime-content/1-uptime-content.en.md))
showed two minimal recipes. This one expands them and covers the
real-world pieces: how to use cron timing you can rely on,
minute caps, security around exposing tokens, and four escalation
patterns for when a probe fails.

## 1. Why GitHub Actions is a useful second layer

Every self-hosted and hosted monitor in
[`3-self-hosted-monitors`](../3-self-hosted-monitors/3-self-hosted-monitors.en.md)
and
[`4-hosted-monitors`](../4-hosted-monitors/4-hosted-monitors.en.md)
has a single point of failure in common: **the monitor and the
target run in the same network**. A GitHub Actions cron breaks
that:

- The probe runs on GitHub's infrastructure, not yours.
- The probe's DNS resolution is GitHub's, not yours.
- The probe sees your endpoint from a real, external IP, which
  catches cases where your endpoint is up on localhost but
  unreachable from the public internet.

The cost: GitHub does not guarantee cron trigger timing. The
[official docs](https://docs.github.com/actions/using-workflows/events-that-trigger-workflows#schedule)
say:

> The longest time you should expect is around 40 minutes on
> average, but it can be as long as several hours.

So GitHub Actions cron is **not** the right primary monitor for
SLA-grade needs. It is the right **second layer** to pair with a
Kuma / UptimeRobot / Better Stack install.

## 2. Recipe: minimal ping

The first article's recipe, expanded with cron that doesn't fight
the rest of the ecosystem:

```yaml
# .github/workflows/uptime-ping.yml
name: uptime-ping
on:
  schedule:
    # Every 5 minutes. Use offset minutes (not 0/30) to avoid
    # colliding with the Actions cron herd at round-number times.
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

Notes:

- **`workflow_dispatch`** lets you trigger the workflow manually
  from the Actions UI — useful for testing before merging.
- **`timeout-minutes: 2`** caps the run; a hanging curl would
  otherwise stall the whole job.
- **`--max-time 10`** caps the curl call inside the run.
- **Cron with offset minutes** (7, 12, 17, ...) avoids the GitHub
  Actions "herd effect" at `:00` / `:30` minute marks. Picking
  a non-round minute puts your workflow ahead of the crowd.

### Cron expressions you can actually rely on

| Cadence | Cron expression | What it triggers |
|---|---|---|
| Every 5 min | `*/5 * * * *` | 12 triggers/hour — beware minute cap |
| Every 5 min, offset | `7,12,17,22,27,32,37,42,47,52,57 * * * *` | 12 triggers/hour, offset |
| Every 15 min | `*/15 * * * *` | 4 triggers/hour |
| Hourly | `0 * * * *` | 1 trigger/hour |
| Daily at 03:00 UTC | `0 3 * * *` | 1 trigger/day |

Even the "every 5 min offset" pattern can be delayed by GitHub's
scheduler. If your SLA can tolerate a 30-minute detection window,
**`*/15 * * * *`** is the sweet spot: 4 triggers/hour, well under
the minute cap, and the worst-case delay is documented.

## 3. Recipe: open a GitHub Issue on failure

Email is unreliable in 2026. Issue tracking survives:

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

Each outage produces a fresh issue tagged `uptime` / `incident`.
Pin it to the repo, and your team's notification flow picks it up.

### Avoiding alert storms

A failed probe at 3am that opens an issue every 5 minutes will
spam your repo. Mitigation patterns:

- **Check for an open issue first.** Use `gh issue list --label
  uptime --state open` and skip if any exist.
- **Cooldown step.** Track the last-failed timestamp in a workflow
  artifact, only open a new issue if N hours have passed.
- **Group by signature.** If the failure mode is the same across
  consecutive probes (e.g., 504), open one issue and add comments.

## 4. Recipe: append a CSV row (for a status badge)

For a public-facing "99.9% uptime" badge, you need historical
state. The cheapest serverless option:

```yaml
# .github/workflows/uptime-csv.yml
name: uptime-csv
on:
  schedule:
    - cron: '*/5 * * * *'

jobs:
  record:
    runs-on: ubuntu-latest
    timeout-minutes: 2
    steps:
      - name: Probe
        id: probe
        run: |
          code=$(curl -fsSL -o /dev/null -w '%{http_code}' \
                  --max-time 10 https://example.com/healthz || echo 000)
          echo "code=$code" >> "$GITHUB_OUTPUT"
          echo "ts=$(date -u +%Y-%m-%dT%H:%M:%SZ)" >> "$GITHUB_OUTPUT"

      - name: Append to history
        run: |
          echo "${{ steps.probe.outputs.ts }},${{ steps.probe.outputs.code }}" \
            >> uptime-history.csv
      - name: Commit (squashed nightly)
        if: github.event_name == 'schedule' && startsWith(steps.probe.outputs.ts, format('{0}', github.event.repository.updated_at))
        run: |
          git config user.name "x-cmd-bot"
          git config user.email "bot@x-cmd.com"
          git add uptime-history.csv
          git diff --cached --quiet || git commit -m "uptime: append probe result"
          git push
```

This workflow pushes one row per probe. If 5-minute probes would
create too many commits per day (~288 commits/day), add a
**daily squash workflow** at `0 0 * * *` that aggregates the rows
into a single daily commit. The badge generator can read either
form.

## 5. Recipe: Slack / Discord webhook

For teams that already live in Slack or Discord:

```yaml
# .github/workflows/uptime-slack.yml
name: uptime-slack
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
      - name: Post to Slack
        if: steps.probe.outputs.code != '200'
        env:
          SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK_URL }}
        run: |
          curl -fsSL -X POST -H 'Content-Type: application/json' \
            --data "{\"text\":\":rotating_light: target returned ${{ steps.probe.outputs.code }}\"}" \
            "$SLACK_WEBHOOK_URL"
```

The webhook URL is a GitHub Actions secret — see §7. Discord is
the same shape; only the payload format differs.

## 6. Limits: the minute cap

GitHub Actions free minutes, by repo visibility:

| Visibility | Free minutes / month |
|---|---|
| Public | 2,000 |
| Private (free plan) | 500 |
| Private (Team plan) | 3,000 |
| Private (Enterprise plan) | 50,000 |

A 5-minute probe burns ~30 seconds of runner time per execution.
At `*/5 * * * *` (~8,640 runs/month) that's ~70 hours/month of
runner time, well within 2,000 free minutes for a public repo.
For private repos, you'll burn through the 500-minute free tier
in a week. Pick a 30-minute cadence (`*/30 * * * *`) or pay for
a Team plan.

## 7. Security around exposing tokens

If your probe needs to hit a private endpoint (a `/healthz` that
isn't public), three patterns:

- **Status check via public side-effect.** The `/healthz` endpoint
  returns 200 to any caller — just for monitoring. Not ideal for
  apps that need auth.
- **HMAC-signed probe.** The probe signs a known token; the
  endpoint validates it. The token lives in GitHub Actions
  secrets. Anyone with the workflow file can see the variable
  names, but not the secret values.
- **IP allowlist.** GitHub publishes
  [a list of runner IPs](https://docs.github.com/actions/security-guides/security-harden-deployments/using-ip-allow-lists-with-github-hosted-runners).
  Configure your endpoint to accept probes from those IPs only.
  This is the cleanest pattern for internal services with auth
  requirements elsewhere.

For all three, store the secret under
`Settings → Secrets and variables → Actions`, not in the workflow
file. Reference it as `${{ secrets.NAME }}` — never echo it to
logs.

## 8. When GitHub Actions is the wrong choice

- You need **SLA-grade detection** under one minute. The cron
  timing is too loose.
- You need **probes from many regions**. GitHub-hosted runners are
  in a few regions; for full geographic coverage, use a hosted
  monitor or self-host in multiple data centers.
- You want **status pages as a product**. The actions cron can
  detect failures but cannot render a polished public status page
  — that's Uptime Kuma / Better Stack's job.

For all three, treat GitHub Actions cron as the second layer
alongside a primary monitor.

## Related resources

- [`1-uptime-content`](../1-uptime-content/1-uptime-content.en.md) — overview + first recipes
- [`3-self-hosted-monitors`](../3-self-hosted-monitors/3-self-hosted-monitors.en.md) — primary monitor choices
- [`4-hosted-monitors`](../4-hosted-monitors/4-hosted-monitors.en.md) — hosted primary monitors
- [`7-decision-guide`](../7-decision-guide/7-decision-guide.en.md) — pick by scenario
- [GitHub Actions: scheduled events](https://docs.github.com/actions/using-workflows/events-that-trigger-workflows#schedule)
- [GitHub Actions: IP allowlists](https://docs.github.com/actions/security-guides/security-harden-deployments/using-ip-allow-lists-with-github-hosted-runners)
- [GitHub Actions: billing](https://docs.github.com/billing/managing-billing-for-github-actions/about-billing-for-github-actions)

## License

This article is part of the `x-cmd/uptime` repo and is licensed under
Apache License 2.0.
