---
x-title: Cron-style heartbeat monitoring
x-desc: Healthchecks.io, Cronitor, Dead Man's Snitch — for the failure mode "the job didn't run at all". Batch jobs, ETL, scheduled scripts, backups.
x-sidebar: Cron-style monitoring
x-keywords: healthchecks io, cronitor, dead man's snitch, heartbeat monitoring, cron job monitoring, batch job monitoring, ping url
x-json-ld:
  '@context': https://schema.org
  '@graph':
    - '@type': TechArticle
      headline: 'Cron-style heartbeat monitoring'
      inLanguage: 'en'
      about: 'Heartbeat / cron-style monitoring'
---

# Cron-style heartbeat monitoring

> **What this article covers.** The first article
> ([`1-uptime-content`](../1-uptime-content/en.md))
> mentioned cron-style monitors briefly. This one dives in: when
> "did the job run?" is the right question (and HTTP probes are
> the wrong tool), the three vendors that matter in 2026 —
> **Healthchecks.io**, **Cronitor**, **Dead Man's Snitch** — and
> what each costs.

Cron-style monitoring answers a different question from HTTP
uptime: **"did my scheduled job run?"** not "is my HTTP endpoint
responding?". The two are easy to confuse and easy to use the
wrong tool for. This article is about when the cron-style question
is what you actually need.

## 1. When cron-style is the right answer

You have a scheduled job — a cron entry, an ETL pipeline, a
backup script, a periodic data refresh. The failure modes that
matter are:

- The job **didn't run at all** (the cron daemon crashed, the
  container was unscheduled, the deploy disabled the schedule).
- The job **started but never finished** (hung on a network call,
  OOM-killed, lost its DB connection).
- The job **finished but failed** (a row count was off, an exit
  code was non-zero).

HTTP probes don't catch any of these. HTTP probes can tell you
that your **web server** is up; they can't tell you whether
yesterday's 3am backup completed.

The cron-style tools solve this by **flipping the relationship
between job and monitor**:

```
HTTP monitor:    monitor → pings → target           (monitor is active)
Cron monitor:    job     → pings → monitor         (job is active)
```

Your job pings the monitor at start, at success, and at failure.
The monitor alerts you when an expected ping doesn't arrive.

## 2. Healthchecks.io — the open-source option

[**Healthchecks.io**](https://healthchecks.io/) is the default
choice. It is open-source (you can
[self-host](https://github.com/healthchecks/healthchecks) the
exact same backend) and has a generous free tier.

### The ping model

Each check is a unique URL. Three events your job can signal:

- **Start** — `curl -fsSL https://hc-ping.com/<uuid>/start`
- **Success** — `curl -fsSL https://hc-ping.com/<uuid>`
- **Failure** — `curl -fsSL https://hc-ping.com/<uuid>/fail`

You tell Healthchecks.io the **period** (e.g., "every day") and
the **grace** (e.g., "1 hour"). If the period passes without a
ping, you get an alert. The grace covers the legitimate case
where the job runs late by a few minutes.

### A worked example

A nightly database backup at 03:00, with a 2-hour grace:

```sh
#!/bin/sh
# /etc/cron.d/backup-db
UUID='<paste-from-healthchecks-ui>'

curl -fsSL "https://hc-ping.com/$UUID/start"

pg_dump --file=/backups/db-$(date +%Y%m%d).sql.gz mydb \
  || curl -fsSL "https://hc-ping.com/$UUID/fail"

# Only ping success after the work is actually done.
curl -fsSL "https://hc-ping.com/$UUID"
```

If the cron entry stops running, the next morning Healthchecks.io
will email / Slack / PagerDuty you. If the cron entry runs but
the backup fails, the `/fail` ping moves the alert from "job is
late" to "job failed" — useful when triaging.

### Pricing

- **Free** for open-source projects (20 checks at any interval).
- **Standard** ($20/mo at time of writing) for 200 checks at
  1-minute minimum period.
- Higher tiers for very large check counts.

The OSS self-host option is the same code, your own Postgres, your
own cost — a few hours to set up if you've never done it before.

## 3. Cronitor — opinionated cron-job observability

[**Cronitor**](https://cronitor.io/) is older and more
enterprise-shaped. It ships the same ping model but adds:

- A cron-expression parser that detects impossible schedules
  (e.g., "Feb 30") at definition time.
- Run-time metrics: did the job run faster / slower than last
  week? Did its log output change shape?
- Telemetry-style integrations with Kubernetes CronJobs, ECS,
  Airflow, etc.

### Pricing

- **Free** for 5 checks.
- **Startup** ($25/mo at time of writing) for 25 checks plus the
  schedule-parsing features.
- Higher tiers for teams with thousands of cron entries.

### When to pick Cronitor over Healthchecks.io

You have a **fleet of scheduled jobs** and want a single pane of
glass that catches schedule-defined-impossible and slow runs.
For a handful of cron entries, Healthchecks.io is the simpler
fit.

## 4. Dead Man's Snitch — the original (now in Sentry)

[**Dead Man's Snitch**](https://deadmanssnitch.com/) is the
original commercial offering in this category. It was acquired by
[Sentry](https://sentry.io/) in 2023 and now ships as part of
Sentry's Cron Monitoring product.

If you're already a Sentry customer, you may already have Cron
Monitoring enabled — the same ping model, integrated with Sentry
issues.

If you're not on Sentry and want a focused cron-monitoring
vendor, Healthchecks.io is the more obvious choice. Dead Man's
Snitch / Sentry Cron Monitoring makes sense when you want cron
alerts to flow into the same incident pipeline as your
application errors.

## 5. Comparison table

| | Healthchecks.io | Cronitor | Dead Man's Snitch |
|---|---|---|---|
| Open-source backend | yes | no | no |
| Free tier | OSS projects: 20 checks, any interval | 5 checks | limited via Sentry |
| Cheapest paid | ~$20/mo | ~$25/mo | via Sentry plan |
| Ping endpoints | /start, / (success), /fail | similar | similar |
| Schedule parsing | basic | strong (detects impossible) | basic |
| Run-time metrics | basic | yes (duration, log shape) | basic |
| Self-host option | yes (Postgres + Docker) | no | no |
| Best when | default; OSS self-host available | fleet of cron entries | you're already on Sentry |

## 6. When cron-style is the **wrong** answer

Common misuses:

- **Probing an HTTP endpoint.** That's an HTTP monitor's job; see
  [`3-self-hosted-monitors`](../3-self-hosted-monitors/en.md)
  or [`4-hosted-monitors`](../4-hosted-monitors/en.md).
  Healthchecks.io will accept an external ping and treat it as
  a "ping arrived" success — but it can't tell you whether the
  endpoint is actually responding.
- **Replacing your application health checks.** A `/healthz`
  endpoint that's checked by Kuma / UptimeRobot tells you the
  app is alive. A cron-monitor ping tells you nothing about the
  app's state.
- **Monitoring interactive events.** A user-action flow
  (signup, purchase) is best instrumented with application-level
  observability, not heartbeats.

Use the right tool for the question. If the question is "did my
scheduled job run?" the cron-style tools in this article are the
answer.

## Related resources

- [`1-uptime-content`](../1-uptime-content/en.md) — overview
- [`3-self-hosted-monitors`](../3-self-hosted-monitors/en.md) — HTTP probes, self-hosted
- [`4-hosted-monitors`](../4-hosted-monitors/en.md) — HTTP probes, hosted
- [`7-decision-guide`](../7-decision-guide/en.md) — pick by scenario
- [Healthchecks.io](https://healthchecks.io/) on the web
- [Healthchecks self-host repo](https://github.com/healthchecks/healthchecks) on GitHub

## License

This article is part of the `x-cmd/uptime` repo and is licensed under
Apache License 2.0.
