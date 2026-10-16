---
name: 6-github-actions-as-monitor
description: Using GitHub Actions cron as an uptime monitor. Independent of host and DNS — a useful second layer of defense. Recipes for minimal ping, open-issue on failure, CSV row for badge, Slack webhook. Timing caveats, minute caps by tier, IP allowlists, secrets handling.
type: summary
---

# Core Content

core_features:

- Why GitHub Actions cron is a useful second layer: independent of your host's network, independent of your DNS, external IP
- The official caveat: cron timing is not guaranteed; "the longest time you should expect is around 40 minutes on average, but it can be as long as several hours"
- Recipe 1: minimal ping (offset-minute cron to avoid the Actions cron herd)
- Recipe 2: open GitHub Issue on failure (with alert-storm mitigation)
- Recipe 3: append CSV row for status badge (with daily squash pattern)
- Recipe 4: post to Slack / Discord webhook
- Minute caps by repo visibility (2,000 / 500 / 3,000 / 50,000 per month)
- Security patterns: public side-effect, HMAC-signed probe, GitHub IP allowlist

## Key Information

highlights:

- GH Actions cron is a SECOND layer, not a primary monitor — pair it with Kuma / UptimeRobot / Better Stack
- Use offset-minute cron (7, 12, 17, ... not 0, 30) to avoid the Actions cron herd at round-number minutes
- `*/15 * * * *` is the sweet spot for private repos on the free tier: 4 triggers/hour, well under the 500-minute cap
- A probe runs on GitHub's infrastructure — the probe sees the endpoint from a real, external IP, which catches "up on localhost but unreachable from the public internet"
- Three secrets patterns for private endpoints: public side-effect, HMAC signature, IP allowlist — never put secrets in the workflow file
- Alert-storm mitigation: check for open issue first, cooldown step, group by failure signature

## Use Cases

use_cases:

- Pairing a GH Actions cron with a self-hosted Kuma or hosted UptimeRobot install for defense in depth
- Detecting "up on localhost but unreachable from the public internet" by probing from GitHub's external IP
- Cheap no-server status-badge CSV for a personal site
- Slack / Discord webhook alerts without standing up a notification service
- Monitoring a private endpoint using GitHub's published runner IP allowlist

## Related Resources

official:
  website: <https://x-cmd.com/uptime>
  repo: <https://github.com/x-cmd/uptime>
related:
  gh_actions_schedule: <https://docs.github.com/actions/using-workflows/events-that-trigger-workflows#schedule>
  gh_actions_ip_allowlist: <https://docs.github.com/actions/security-guides/security-harden-deployments/using-ip-allow-lists-with-github-hosted-runners>
  gh_actions_billing: <https://docs.github.com/billing/managing-billing-for-github-actions/about-billing-for-github-actions>

## Summary

The sixth article in the x-cmd/uptime topic library. It treats GitHub Actions cron as a useful second layer of defense — independent of your host and DNS — but explicitly NOT a replacement for a dedicated monitor. The article includes four copy-paste recipes: minimal ping with offset-minute cron, open GitHub Issue on failure with alert-storm mitigation, append CSV row for a status badge with daily squash pattern, and Slack / Discord webhook. The official caveat is cited: cron timing can be delayed by "around 40 minutes on average, but it can be as long as several hours." The article ends with a minute-cap table (2,000 / 500 / 3,000 / 50,000 by repo visibility), three secrets patterns for private endpoints (public side-effect, HMAC signature, GitHub IP allowlist), and three cases where GH Actions cron is the wrong choice (sub-minute SLA, multi-region probes, status-page-as-a-product). The recommendation: pair GH Actions cron with Kuma or a hosted monitor for defense in depth.
