---
name: 3-self-hosted-monitors
description: Deep dive on four self-hosted monitor options in 2026 — Uptime Kuma, Beszel, Prometheus + blackbox_exporter, and statping-ng. Install, configure, alert channels, and a side-by-side comparison table.
type: summary
---

# Core Content

core_features:

- Uptime Kuma: Node.js + SQLite; ~90 alert channels; built-in status pages; the modern default for small-to-medium sites
- Beszel: Go + SQLite hub-and-spoke; ships a per-host agent for CPU/memory/disk/network; weak on HTTP checks
- Prometheus + blackbox_exporter: the heavy option; minimal addition when Prometheus is already running
- statping-ng: legacy Go fork; pick only for existing installs or where Uptime Kuma's footprint is unacceptable
- Side-by-side comparison table covering stack / probe richness / status page / resource monitoring / alert channels / HA

## Key Information

highlights:

- Uptime Kuma is the 2026 default for a small-to-medium site: one `docker run`, one web UI, one status page
- Pin to `louislam/uptime-kuma:1` (the 2.x rewrite is still in progress at time of writing)
- Beszel's uptime checks are intentionally thinner than Kuma's; common pattern: Beszel for fleet resources + Kuma for service uptime
- Prometheus + blackbox_exporter is the right answer only when you already pay the Prometheus tax; otherwise the operational overhead is too high
- All four tools use SQLite as the default; PostgreSQL or external TSDBs are the upgrade path for HA
- Self-hosted means "you have a new thing to keep running" — always pair self-hosted with an independent second layer (GH Actions cron, covered in article 6)

## Use Cases

use_cases:

- Choosing a self-hosted monitor for a small site, a small SaaS, or a personal homelab
- Picking between Kuma and Beszel when both fit on paper (Kuma for HTTP depth; Beszel for fleet resource monitoring)
- Adding HTTP probes to an existing Prometheus install without standing up new infrastructure
- Migrating off statping-ng to Uptime Kuma (or deciding not to)
- Designing a defense-in-depth setup that pairs self-hosted with GitHub Actions cron

## Related Resources

official:
  website: <https://x-cmd.com/uptime>
  repo: <https://github.com/x-cmd/uptime>
related:
  uptime_kuma: <https://github.com/louislam/uptime-kuma>
  beszel: <https://github.com/henrygd/beszel>
  prometheus_blackbox: <https://github.com/prometheus/blackbox_exporter>
  statping_ng: <https://github.com/statping-ng/statping-ng>

## Summary

The third article in the x-cmd/uptime topic library. It treats the self-hosted monitor space as four distinct picks in 2026: Uptime Kuma (the modern default for small-to-medium sites, rich HTTP probes, ~90 alert channels, built-in status pages), Beszel (Go + SQLite with a hub-and-spoke agent for fleet resource monitoring — uptime is secondary), Prometheus + blackbox_exporter (the heavy option that's a one-config addition when you already pay the Prometheus tax), and statping-ng (legacy Go fork, only for existing installs). The article includes Docker install commands for Kuma and Beszel, a full Prometheus + blackbox_exporter config example, and a five-row comparison table on stack / probe richness / status page / resource monitoring / alert channels / HA path. The recommendation: pick Kuma unless your fleet is large enough that Beszel's resource monitoring pays off, or you're already on Prometheus. Pair any of these with a GitHub Actions cron for defense in depth.
