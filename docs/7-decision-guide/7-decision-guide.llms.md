---
name: 7-decision-guide
description: Pick the right monitoring strategy by scenario. Personal site, small business, SaaS with paying users, internal tool, scheduled jobs. Cost table. Defense-in-depth pattern. A one-paragraph decision tree.
type: summary
---

# Core Content

core_features:

- Five scenarios: personal site, small business / agency, SaaS with paying users, internal tool, scheduled jobs
- Each scenario lists primary recommendation, optional second layer, and cron-style add-on
- Cost table: 5 rows × 4 columns (primary / second layer / cron add-on / total)
- Defense-in-depth rationale: every primary monitor has a single point of failure it cannot itself catch
- One-paragraph decision tree that compresses the whole article

## Key Information

highlights:

- Personal site → UptimeRobot free + GH Actions cron → $0/mo
- Small business → UptimeRobot Pro ($7) + GH Actions cron → $7-12/mo
- SaaS with paying users → Better Stack / Better Uptime ($25-50) + GH Actions cron + Healthchecks.io → $25-70/mo
- Internal tool → self-hosted Uptime Kuma (already operated box) → $0 + box cost
- Scheduled jobs → Healthchecks.io (open source, free for OSS) → $0-20/mo
- "Two tools" is the floor, not the ceiling — the recurring theme is that every primary monitor has a single point of failure it cannot itself catch
- The cheapest independent second layer is a GitHub Actions cron probing the primary monitor's status page URL, not your application URL

## Use Cases

use_cases:

- Picking the right monitor for a personal site, side project, or homelab
- Picking the right monitor for a small business or agency with multiple client sites
- Picking the right monitor for a SaaS with paying users and a customer-facing status page
- Picking the right monitor for an internal tool not exposed to the public internet
- Picking the right monitor for scheduled jobs (the failure mode "the job didn't run at all")
- Composing two tools for defense in depth (primary + independent GH Actions cron)

## Related Resources

official:
  website: <https://x-cmd.com/uptime>
  repo: <https://github.com/x-cmd/uptime>
related:
  uptimerobot: <https://uptimerobot.com/>
  uptime_kuma: <https://github.com/louislam/uptime-kuma>
  better_stack: <https://betterstack.com/uptime>
  better_uptime: <https://betteruptime.com/>
  hyperping: <https://hyperping.com/>
  healthchecks_io: <https://healthchecks.io/>
  cronitor: <https://cronitor.io/>
  beszel: <https://github.com/henrygd/beszel>

## Summary

The seventh and synthesis article in the x-cmd/uptime topic library. It treats five scenarios — personal site, small business / agency, SaaS with paying users, internal tool, scheduled jobs — and maps each to a primary monitor, an optional second layer, and an optional cron-style add-on. The cost table covers all five scenarios in one row each, with totals ranging from $0/mo (personal site, internal tool) to $25-70/mo (SaaS with paying users). The defense-in-depth rationale: every primary monitor has a single point of failure it cannot itself catch, and the cheapest independent second layer is a GitHub Actions cron probing the primary monitor's status page URL. The article closes with a one-paragraph decision tree that compresses all of the above into a single lookup: "self-host Kuma if I already operate a server and have an ops person, otherwise pick UptimeRobot / Better Stack / Better Uptime; add GH Actions cron as second layer; layer Healthchecks.io on top if I have scheduled jobs."
