---
x-title: Decision guide — which monitor for which scenario
x-desc: Pick the right monitoring strategy by scenario. Personal site, small business, SaaS, internal tool, batch job. Cost table. Defense-in-depth patterns.
x-sidebar: Decision guide
x-keywords: decision guide, scenario, personal site, small business, saas, internal tool, batch job, defense in depth, cost
x-json-ld:
  '@context': https://schema.org
  '@graph':
    - '@type': TechArticle
      headline: 'Decision guide — which monitor for which scenario'
      inLanguage: 'en'
      about: 'Choosing the right monitoring strategy'
---

# Decision guide — which monitor for which scenario

> **What this article covers.** The previous six articles walk each
> option in depth. This one is the synthesis: **which monitoring
> strategy fits which scenario**, what each costs, and when to
> combine multiple tools for defense in depth.

The aim is a one-page lookup table that maps "I am a ___ with a
___ monitoring need" to "the right tool for the job". Most
real-world setups need **two** tools — a primary monitor and an
independent second layer.

## 1. The five scenarios

The split below covers ~95% of personal and small-team monitoring
needs in 2026. Larger enterprises have dedicated SRE teams and
likely already run Prometheus + an enterprise vendor — those
cases are out of scope for this article.

| # | Scenario | "What am I monitoring?" |
|---|---|---|
| A | **Personal site** | One URL, low stakes, no team |
| B | **Small business / agency** | A handful of client sites, billing depends on uptime |
| C | **SaaS with paying users** | A product's web app + APIs + status page is part of the product |
| D | **Internal tool / dev infra** | Jenkins, internal APIs, dev dashboards |
| E | **Scheduled jobs** | Nightly backups, ETL pipelines, batch reports |

Each scenario below lists the primary recommendation, the optional
second layer, and the cron-style tool (when applicable).

## 2. Scenario A — personal site

**The job:** One personal site, low stakes, you're the only person
who'll notice an outage. Cost matters.

**Primary:** [UptimeRobot](https://uptimerobot.com/) free tier
(50 monitors, 5-minute interval) — most personal sites have well
under 50 endpoints to watch.

**Optional second layer:** A
[GitHub Actions cron at `*/15 * * * *`](https://docs.github.com/actions/using-workflows/events-that-trigger-workflows#schedule)
that probes your status page URL. Costs ~5 minutes/month of free
Actions minutes for a public repo.

**Why not self-hosted?** Running Uptime Kuma on your own VPS to
watch your personal site is operational debt. The hosted option
is free; the self-hosted option consumes hours you don't have.

**Total cost: $0/mo.**

## 3. Scenario B — small business / agency

**The job:** A handful of client sites; clients notice outages;
uptime is a billable concern.

**Primary:** [UptimeRobot Pro](https://uptimerobot.com/) at ~$7/mo
gets you 1-minute interval, SMS alerts, and multiple status pages
(one per client).

**Alternative primary:** Self-hosted
[Uptime Kuma](https://github.com/louislam/uptime-kuma) on a $5/mo
VPS — equivalent cost, more alert channels, more setup time.

**Second layer:** GitHub Actions cron at `*/15 * * * *` that probes
the public status page URL of each client. Costs a few minutes per
month.

**Why this combo?** The hosted primary has rich alerting. The
GitHub layer catches the case where your monitor's account lapses
or the monitor itself is down.

**Total cost: $7-12/mo, all hosted.**

## 4. Scenario C — SaaS with paying users

**The job:** Your product has paying users; the status page is part
of the product surface; downtime costs revenue.

**Primary:** [Better Stack](https://betterstack.com/uptime) or
[Better Uptime](https://betteruptime.com/) — both ship a polished
status page, incident posting, and on-call schedules. Pick Better
Stack for status-page-first; Better Uptime for incident-management
opinionation.

**Alternative primary:** Self-hosted Uptime Kuma + a
self-hosted status page. Cheaper, but you write the status-page
UI and incident workflow yourself.

**Second layer:** GitHub Actions cron at `*/5 * * * *` for public
repo (free), or `*/15 * * * *` for private repo on Team plan
(paid). The cron probes the status page URL, not your application
URL — that way GitHub's view is independent of your SaaS.

**Cron-style add-on (if applicable):** [Healthchecks.io](https://healthchecks.io/)
for any nightly ETL, billing, or scheduled reporting jobs. Free
for open-source projects, ~$20/mo otherwise.

**Why this combo?** Polished primary for the team and the
customer-visible status page; independent second layer that
catches "the monitor itself is down"; cron-style for the
question "did my nightly job run?" which an HTTP monitor cannot
answer.

**Total cost: $25-50/mo for the hosted monitor + $0-20/mo for
Healthchecks.io.**

## 5. Scenario D — internal tool / dev infra

**The job:** Internal dashboards, Jenkins, dev APIs. Outages hurt
your team's velocity but don't directly lose revenue. Visibility
matters; "monitoring of the monitor" matters less.

**Primary:** Self-hosted
[Uptime Kuma](https://github.com/louislam/uptime-kuma) on a
container you already operate. Slack alerts go to the engineering
channel.

**Optional pair:** Self-hosted [Beszel](https://github.com/henrygd/beszel)
on the same host — adds per-server resource monitoring for the
boxes running Jenkins, the database, etc.

**Second layer:** A lighter cadence GitHub Actions cron
(`*/30 * * * *`) is enough; the team's notification flow is the
real second layer.

**Why not hosted?** Most internal infra is not exposed to the
public internet — Better Stack / UptimeRobot's external probes
can't see it. Self-hosted is the natural shape.

**Total cost: $0/mo software + the cost of the box you already
operate.**

## 6. Scenario E — scheduled jobs

**The job:** Nightly backups, ETL pipelines, periodic reports,
scheduled cleanups. The question is "did the job run?", not "is
the endpoint up?".

**Primary:** [Healthchecks.io](https://healthchecks.io/) — open
source, free for OSS, OSS-self-hostable. Each job gets a UUID,
pings `/start`, `/`, `/fail`.

**Alternative primary:** [Cronitor](https://cronitor.io/) when you
have a fleet of cron entries and want schedule-parsing + run-time
metrics.

**When to add an HTTP monitor:** If any of your scheduled jobs
push to an HTTP endpoint you care about (a webhook receiver, an
analytics ingestion), probe that endpoint with Uptime Kuma or
UptimeRobot too. The HTTP probe catches "the receiver is down"
separately from "the job didn't run".

**Total cost: $0-25/mo for Healthchecks.io (free for OSS).**

## 7. Cost table

| Scenario | Primary | Second layer | Cron add-on | Total |
|---|---|---|---|---|
| A. Personal site | UptimeRobot free | GH Actions `*/15` | — | **$0/mo** |
| B. Small business | UptimeRobot Pro $7 | GH Actions `*/15` | — | **$7-12/mo** |
| C. SaaS w/ paying users | Better Stack $25-50 | GH Actions `*/5` (public) | Healthchecks.io $0-20 | **$25-70/mo** |
| D. Internal tool | Uptime Kuma self-host | GH Actions `*/30` | — | **$0 + box cost** |
| E. Scheduled jobs | Healthchecks.io $0-20 | UptimeRobot/Kuma if HTTP | — | **$0-20/mo** |

Numbers are order-of-magnitude at time of writing (late 2026).
Re-check vendor pricing pages before budgeting.

## 8. Defense-in-depth — why "two" is the floor

The recurring theme across scenarios: every primary monitor has a
single point of failure that the primary monitor cannot itself
catch. The two modes:

- **The monitor itself is down.** Happens rarely for hosted
  monitors, more often for self-hosted (the box it runs on).
- **Your account with the monitor lapses.** Forgets happen.

The cheapest independent second layer is GitHub Actions cron
(article 6). The cron probes the **status page URL** the primary
monitor publishes, not your application URL. The status page
going red on the GitHub side tells you the primary monitor is
itself broken — without waiting for someone to notice the primary
monitor is silent.

For scenarios A, B, and C, this second layer is a no-brainer; the
cost is a few Actions minutes per month. For scenario D, the
team's notification flow is a sufficient second layer in practice.
For scenario E, cron-style monitoring's job is to detect
"didn't run" — add an HTTP monitor only when there's a downstream
HTTP endpoint to watch.

## 9. The decision tree, in one paragraph

> *I am a personal site / small business / SaaS / internal tool
> / batch-job operator.* I want to monitor **HTTP endpoints**:
> self-host Kuma if I already operate a server and have an ops
> person, otherwise pick UptimeRobot free (personal) or Pro
> (small business), or Better Stack / Better Uptime (SaaS).
> Add a **GitHub Actions cron at `*/15`** to probe my status page
> URL as a second layer. If I have **scheduled jobs**, layer
> **Healthchecks.io** on top — `/start`, `/`, `/fail` per job —
> because HTTP probes cannot answer "did my cron run?". For
> **internal-only services** that aren't reachable from the public
> internet, self-host Uptime Kuma + pair with a lighter GitHub
> Actions cadence.

## Related resources

- [`1-uptime-content`](../1-uptime-content/en.md) — overview
- [`2-the-catalog`](../2-the-catalog/en.md) — this repo's catalog
- [`3-self-hosted-monitors`](../3-self-hosted-monitors/en.md) — self-hosted picks
- [`4-hosted-monitors`](../4-hosted-monitors/en.md) — hosted picks
- [`5-cron-style-monitoring`](../5-cron-style-monitoring/en.md) — cron-style picks
- [`6-github-actions-as-monitor`](../6-github-actions-as-monitor/en.md) — second-layer recipes

## License

This article is part of the `x-cmd/uptime` repo and is licensed under
Apache License 2.0.
