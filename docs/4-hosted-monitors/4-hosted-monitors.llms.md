---
name: 4-hosted-monitors
description: Hosted uptime monitors in 2026 — UptimeRobot (free default), Better Stack (modern + status-page-first), Better Uptime (incident-management-first), Hyperping (small-team simple). Pricing, monitor types, status pages, on-call, defense-in-depth pattern.
type: summary
---

# Core Content

core_features:

- UptimeRobot: the default free option; 50 monitors at 5-min interval; utilitarian UI; Pro tier at ~$7/mo unlocks 1-min interval
- Better Stack: modern, status-page-first; HTTP(S), TCP, ICMP, keyword, JSON path, SSL expiry checks; 30-second intervals on the cheapest paid tier
- Better Uptime: shaped like Better Stack but with incident-management opinionation; on-call schedules + Sentry-like postmortems
- Hyperping: smallest of the four; ~half the cost of UptimeRobot Pro; tight product for tiny teams
- Comparison table covering free tier / cheapest paid / min interval / monitor types / status pages / on-call / incident workflow
- The "hosted monitor single-point-of-failure" problem and the GitHub Actions cron defense-in-depth mitigation

## Key Information

highlights:

- UptimeRobot free tier is 50 monitors at 5-minute interval — the bottleneck for most free users is the 5-minute granularity, not the monitor count
- Better Stack's differentiator is the status page editor (manual + auto-detected incidents); Better Uptime's differentiator is the incident-management workflow
- All four vendors publish a status page of their own — a hosted monitor's status page going red is the canary that the monitor itself is broken
- A hosted monitor is one more vendor in your dependency graph; pair it with a GH Actions cron that probes the monitor's status page
- Break-even between hosted and self-hosted: if you have no dedicated ops and no existing infrastructure, hosted almost always wins; the moment you have either, self-hosted starts to win on cost

## Use Cases

use_cases:

- Choosing a hosted monitor for a personal site, a side project, or a small business
- Picking between Better Stack (status-page-first) and Better Uptime (incident-management-first) for a small team
- Pairing UptimeRobot Pro's 1-minute interval with a GH Actions cron for defense in depth
- Estimating when a self-hosted Kuma install becomes cheaper than a paid Better Stack / Better Uptime plan

## Related Resources

official:
  website: <https://x-cmd.com/uptime>
  repo: <https://github.com/x-cmd/uptime>
related:
  uptimerobot: <https://uptimerobot.com/>
  better_stack: <https://betterstack.com/uptime>
  better_uptime: <https://betteruptime.com/>
  hyperping: <https://hyperping.com/>

## Summary

The fourth article in the x-cmd/uptime topic library. It treats hosted monitoring as four distinct picks in 2026: UptimeRobot (the default free option, 50 monitors at 5-minute interval, utilitarian UI), Better Stack (the modern, status-page-first choice with the polished incident-posting editor), Better Uptime (incident-management-first, on-call schedules and Sentry-like postmortems built in), and Hyperping (the small-team simple option). The article includes a five-row comparison table on free tier / cheapest paid / min interval / monitor types / status pages / on-call / incident workflow, and a worked argument for when hosted beats self-hosted (no ops, no existing infra → hosted; otherwise self-hosted starts winning on cost). It ends with the "hosted monitor single-point-of-failure" warning and points to article 6 for the GitHub Actions cron defense-in-depth pattern that mitigates it.
