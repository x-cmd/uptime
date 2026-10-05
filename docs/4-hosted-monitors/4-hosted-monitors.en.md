---
x-title: Hosted uptime monitors
x-desc: UptimeRobot, Better Stack, Better Uptime, Hyperping — pricing, monitor types, alert channels, status-page-as-a-product. When hosted beats self-hosted.
x-sidebar: Hosted monitors
x-keywords: uptimerobot, better stack, better uptime, hyperping, hosted monitoring, status page as a product, saas monitor
x-json-ld:
  '@context': https://schema.org
  '@graph':
    - '@type': TechArticle
      headline: 'Hosted uptime monitors'
      inLanguage: 'en'
      about: 'Hosted / SaaS uptime monitors'
---

# Hosted uptime monitors

> **What this article covers.** The first article
> ([`1-uptime-content`](../1-uptime-content/1-uptime-content.en.md))
> mentioned hosted monitors briefly. This one walks the four that
> matter in 2026 — **UptimeRobot**, **Better Stack**, **Better
> Uptime**, and **Hyperping** — covers what each is good at, what
> each costs, and when "pay someone else to do it" beats running a
> container yourself.

A hosted monitor is the right answer when you don't want to operate
any infrastructure yourself: someone else's boxes probe your
endpoints and call your phone when they fail. The trade-off — which
the self-hosted tools in
[`3-self-hosted-monitors`](../3-self-hosted-monitors/3-self-hosted-monitors.en.md)
don't have — is that **when your hosted-monitor account is
itself down (or past the grace period), your monitoring is also
down**. The recommended mitigation is in
[`6-github-actions-as-monitor`](../6-github-actions-as-monitor/6-github-actions-as-monitor.en.md).

## 1. UptimeRobot — the default free option

[**UptimeRobot**](https://uptimerobot.com/) has been around since
2010. The free tier covers **50 monitors at 5-minute intervals**
with HTTP(S), ping, port, and keyword checks. Email and a small
set of webhook channels are included.

### What you get for free

- 50 monitors, 5-minute check interval (cannot be tightened on
  the free tier).
- 1 status page (UptimeRobot-branded).
- 5-minute granularity is the bottleneck for most free users — a
  failure is detected in 0-5 minutes, often close to the 5-minute
  mark.

### What you pay for

- **Pro** (around $7/mo at time of writing): 1-minute interval,
  more monitors, SMS alerts, multiple status pages.
- Higher tiers add team features, incident management, and SLA
  reporting. Pricing moves up to enterprise only at very large
  monitor counts.

### When to pick it

The default choice for personal sites, side projects, and small
businesses. The UI is utilitarian — it gets the job done. The main
frustration is that **the free tier is 5 minutes**, which means a
single failure window is up to 5 minutes before you hear about it.
For a paid SaaS where the outage itself costs you money, the Pro
tier's 1-minute interval is the right spend.

## 2. Better Stack — modern, status-page-first

[**Better Stack**](https://betterstack.com/uptime) is the
newer-generation option. The pitch is "Uptime + Status Page +
On-call" as one product:

- **Uptime** — HTTP(S), TCP, ICMP, keyword, JSON path, and SSL
  expiry checks. 30-second intervals on the cheapest paid tier.
- **Status page** — a polished, Atlassian-Statuspage-style page
  with incident posting.
- **On-call** — schedules, escalations, and integrations with
  PagerDuty / Slack / MS Teams.

### Pricing at a glance

- **Free** for the first monitor (1-minute interval) plus a status
  page.
- **Starter** tier: ~$25/mo at time of writing for a small team,
  with multiple status pages and richer alert routing.
- **Enterprise** scales to hundreds of monitors with SOC 2, audit
  logs, and SSO.

### When to pick it

You're shipping a product with paying users, and the status page
is part of the product surface — not just a side artifact. The
status page editor is the differentiator: incidents can be posted
manually, auto-detected from uptime failures, or both. If you've
ever had to paste a hand-edited HTML status page together at 3am,
the value proposition is immediate.

## 3. Better Uptime — incident-management-first

[**Better Uptime**](https://betteruptime.com/) is shaped like
Better Stack but with more weight on the on-call / incident side:

- **Uptime** checks comparable to Better Stack.
- **Status page** included.
- **On-call schedules**, escalations, and a Sentry-like incident
  workflow (postmortem templates, status updates, retros).

The differentiator is the incident-management workflow. If your
team already uses PagerDuty or Opsgenie and only needs uptime,
Better Uptime is overkill. If your team is small and wants
uptime + status + on-call in one bill, Better Uptime is more
opinionated than Better Stack about how incidents flow.

### When to pick it

Small team, no existing PagerDuty subscription, want one vendor to
cover monitoring + status + on-call + postmortems. Pricing is
comparable to Better Stack at the small end.

## 4. Hyperping — small-team simplicity

[**Hyperping**](https://hyperping.com/) is the smallest of the four
— one founder, a tight product, pricing that competes with
UptimeRobot Pro at half the cost. The features are similar to
UptimeRobot Pro: HTTP(S), keyword, ping, port, SSL checks; status
pages; email + Slack + webhook alerts.

### When to pick it

You're a single developer or a tiny team, you want better
intervals and nicer status pages than UptimeRobot's free tier,
and you don't need the incident-management stack that Better
Stack / Better Uptime add. Hyperping is the right shape for
"monitor a few sites, get nice alerts, ship a status page."

## 5. Comparison table

| | UptimeRobot | Better Stack | Better Uptime | Hyperping |
|---|---|---|---|---|
| Free tier | 50 monitors, 5-min interval | 1 monitor, 1-min interval | limited trial | none at time of writing |
| Cheapest paid | ~$7/mo (Pro, 1-min) | ~$25/mo (Starter) | ~$25/mo | ~$5-10/mo |
| Min interval (paid) | 1 min | 30 s | 30 s | 1 min |
| Monitor types | HTTP(S), ping, port, keyword | + JSON path, SSL expiry | similar | HTTP(S), ping, port, keyword |
| Status pages | yes (paid for multiple) | yes, polished | yes, polished | yes |
| On-call / scheduling | no | yes (paid) | yes (the differentiator) | no |
| Incident workflow | basic | good | best of the four | basic |
| Best when | personal site / side project | SaaS where status page is product | small team without PagerDuty | tiny team, simpler than Kuma |

## 6. Choosing hosted over self-hosted

The break-even is around the **operational cost of running a
monitor yourself**:

- A small Uptime Kuma container takes a few minutes to install
  but it does need patches, SQLite backups, and someone to watch
  the box it runs on.
- A hosted monitor takes a credit card and a few minutes to
  configure; the vendor handles the rest.

If you have **no dedicated ops person** and **no existing
infrastructure** to attach the monitor to, hosted is almost
always the right answer in 2026. The moment you have either —
a server already running Prometheus, a sysadmin who can patch a
container — self-hosted starts to win on cost and on data
residency.

If cost is the deciding factor: UptimeRobot's free tier handles
50 monitors for $0/mo. Self-hosted costs you CPU + RAM + your
time. Better Stack / Better Uptime's paid tiers start around
$25/mo, comparable to running a small VPS.

## 7. The hosted-monitor single-point-of-failure

A hosted monitor is one more vendor in your dependency graph.
Two failure modes:

- **The monitor itself is down** (rare but happens; their
  dashboard is on the same internet your target is). You won't
  see anything in their UI to alert you.
- **Your account lapses** (you forgot to renew, the credit card
  expired). The monitor stops probing. Your alerts stop.

The defense-in-depth pattern: pair the hosted monitor with a
GitHub Actions cron (article 6) that probes the **status page
URL** the monitor publishes. The status page going red on the
GitHub side tells you the host monitor is itself broken.

## Related resources

- [`1-uptime-content`](../1-uptime-content/1-uptime-content.en.md) — overview
- [`3-self-hosted-monitors`](../3-self-hosted-monitors/3-self-hosted-monitors.en.md) — if you want to run it yourself
- [`5-cron-style-monitoring`](../5-cron-style-monitoring/5-cron-style-monitoring.en.md) — for cron jobs, not HTTP endpoints
- [`6-github-actions-as-monitor`](../6-github-actions-as-monitor/6-github-actions-as-monitor.en.md) — independent second layer
- [`7-decision-guide`](../7-decision-guide/7-decision-guide.en.md) — pick by scenario

## License

This article is part of the `x-cmd/uptime` repo and is licensed under
Apache License 2.0.
