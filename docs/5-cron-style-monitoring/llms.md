---
name: 5-cron-style-monitoring
description: Heartbeat / cron-style monitoring for the failure mode "the job didn't run at all." Healthchecks.io (open-source, free for OSS projects), Cronitor (opinionated, schedule-parsing), Dead Man's Snitch (now in Sentry). When cron-style is right vs when HTTP probes are the right tool.
type: summary
---

# Core Content

core_features:

- The flipped relationship between job and monitor: the job pings the monitor, not the other way around
- Three failure modes cron-style catches: didn't run at all, started but didn't finish, finished but failed
- Healthchecks.io: open-source backend; OSS free tier of 20 checks; `/start`, `/`, `/fail` ping endpoints
- Cronitor: opinionated cron-job observability; cron-expression parser that catches impossible schedules; run-time metrics
- Dead Man's Snitch: the original commercial offering, now part of Sentry Cron Monitoring
- Comparison table: OSS backend / free tier / cheapest paid / ping endpoints / schedule parsing / run-time metrics / self-host option
- Three common misuses (probing HTTP endpoints, replacing health checks, monitoring interactive events)

## Key Information

highlights:

- Cron-style monitoring answers "did my scheduled job run?" — not "is my HTTP endpoint responding?"
- The relationship is flipped: the job pings the monitor, instead of the monitor pinging the target
- The `/start`, `/`, `/fail` ping model lets the job signal three states: started, succeeded, failed
- Healthchecks.io is the default; the OSS self-host backend is the same code on your own Postgres
- Cronitor's differentiator is its schedule parser (catches impossible schedules at definition time) and run-time metrics
- Dead Man's Snitch is now part of Sentry's Cron Monitoring — pick it when you're already on Sentry and want cron alerts in the same incident pipeline as application errors
- Common misuse: probing an HTTP endpoint with a cron monitor — the cron monitor can't tell you whether the endpoint is actually responding

## Use Cases

use_cases:

- Monitoring nightly database backups (cron entry that may or may not run)
- Monitoring ETL pipelines (did the pipeline start? did it finish? did it fail?)
- Monitoring scheduled data refreshes, periodic exports, periodic cleanups
- Pairing cron-style monitoring with an HTTP monitor: cron-style catches "did the job run?", HTTP catches "is the service alive?"
- Self-hosting Healthchecks.io on your own Postgres to keep monitoring metadata on-prem

## Related Resources

official:
  website: <https://x-cmd.com/uptime>
  repo: <https://github.com/x-cmd/uptime>
related:
  healthchecks_io: <https://healthchecks.io/>
  healthchecks_oss: <https://github.com/healthchecks/healthchecks>
  cronitor: <https://cronitor.io/>
  sentry_cron: <https://sentry.io/for/cron-monitoring/>

## Summary

The fifth article in the x-cmd/uptime topic library. It treats cron-style heartbeat monitoring as a separate problem from HTTP uptime: cron-style answers "did my scheduled job run?" via a flipped relationship where the job pings the monitor, not the other way around. The three vendors that matter in 2026 are Healthchecks.io (open-source, OSS free tier, self-hostable on Postgres — the default), Cronitor (more opinionated, schedule parser that catches impossible cron expressions at definition time, run-time metrics), and Dead Man's Snitch (now part of Sentry Cron Monitoring, pick when you're already on Sentry). The article includes a full worked example — a nightly PostgreSQL backup with /start, /fail, and / ping calls — and a five-row comparison table. It closes with three common misuses (probing HTTP endpoints, replacing application health checks, monitoring interactive events) to keep the tool from being deployed where it can't actually answer the question being asked.
