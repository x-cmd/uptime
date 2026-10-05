---
x-title: Self-hosted uptime monitors
x-desc: Uptime Kuma, Beszel, Prometheus + blackbox_exporter, and statping-ng. Install, configure, alert channels, comparison table.
x-sidebar: Self-hosted monitors
x-keywords: uptime kuma, beszel, prometheus, blackbox exporter, statping, self-hosted monitoring, docker
x-json-ld:
  '@context': https://schema.org
  '@graph':
    - '@type': TechArticle
      headline: 'Self-hosted uptime monitors'
      inLanguage: 'en'
      about: 'Self-hosted service monitoring tools'
---

# Self-hosted uptime monitors

> **What this article covers.** The first article
> ([`1-uptime-content`](../1-uptime-content/1-uptime-content.en.md))
> mentioned self-hosted monitors in passing. This one dives in:
> install, configure, alert channels, and a side-by-side comparison
> of the four options that matter in 2026 — **Uptime Kuma**,
> **Beszel**, **Prometheus + blackbox_exporter**, and
> **statping-ng**.

Self-hosted means: you run a server (or a container on a server)
that does the probing and ships the alerts. The advantage is
independence from any third party's billing, downtime, or
data-residency posture. The disadvantage is that you now have a
new thing to keep running — which is why you should be monitoring
**the monitor itself** (covered in
[`6-github-actions-as-monitor`](../6-github-actions-as-monitor/6-github-actions-as-monitor.en.md)).

## 1. Uptime Kuma — the default modern choice

[**Uptime Kuma**](https://github.com/louislam/uptime-kuma) is a
Node.js + SQLite app with a beautiful UI. It handles HTTP(S),
TCP, ping, DNS, push, Docker container, and even steam-game-server
checks out of the box. Alerts go to ~90 notification channels
(Telegram, Slack, Discord, email, SMS via Twilio, ntfy, Gotify,
Pushover, ...).

### Install with Docker

The canonical install:

```sh
docker run -d \
  --name uptime-kuma \
  --restart=always \
  -p 3001:3001 \
  -v uptime-kuma:/app/data \
  louislam/uptime-kuma:1
```

The web UI is at `http://your-host:3001`. The first account you
create becomes the admin. SQLite lives in the named volume; the
container can be restarted without losing state.

For a hardened setup, put it behind a reverse proxy (Caddy, Nginx,
Traefik) with TLS, and restrict the management UI by IP allowlist.
The public-facing status page (`/status/<slug>`) is intended to be
exposed — design your URL accordingly.

### Add a monitor

In the UI: **Add Monitor → Type → HTTPS**. The minimum required
fields are a friendly name, the URL, and an interval (60 seconds
is the default for the public image; many teams settle on 60s for
critical, 300s for everything else). Acceptable status codes can
be left at the default `200-299` or tightened to a single code.

For more than one or two monitors, configure monitors via the
JSON import (Settings → Backup → Import) rather than clicking
through the UI each time.

### Status page as a side effect

Each monitor group can render its own public status page at
`/status/<slug>`. The page is unauthenticated and intended for
public consumption — Uptime Kuma is built around "ship a status
page, period." Multiple status pages coexist; you can have one
per service family.

### Caveats

- The 1.x line is the actively-developed branch; the 2.x rewrite is
  in progress at the time of writing (late 2026). If you start
  fresh today, pin to `louislam/uptime-kuma:1`.
- SQLite is fine for a single instance. If you want HA, use
  the project's documented PostgreSQL back end (still 1.x) or run
  two instances behind a load balancer with a shared external
  database.
- The container's bundled `node` is not patched separately from
  the upstream releases — keep the image current.

## 2. Beszel — lightweight + server-resource aware

[**Beszel**](https://github.com/henrygd/beszel) is a Go + SQLite
app with a different scope: in addition to HTTP/TCP/ICMP uptime
checks, it ships a **per-host agent** that reports CPU, memory,
disk, and network. The architecture is hub-and-spoke — you run
one Beszel **hub** (the web UI) and one **agent** per server you
want monitored.

### Install

The hub:

```sh
docker run -d \
  --name beszel-hub \
  --restart=always \
  -p 8090:8090 \
  -v ./beszel-data:/beszel_data \
  henrygd/beszel
```

The agent (on each server you monitor):

```sh
docker run -d \
  --name beszel-agent \
  --restart=always \
  --network host \
  -e PORT=45876 \
  -e KEY="<paste-from-hub-ui>" \
  henrygd/beszel-agent
```

The `KEY` is generated inside the hub UI when you add a new
system. The agent speaks to the hub over the host network; expose
port 45876 only on the trusted side.

### When to pick Beszel over Kuma

Beszel's **uptime** checks are second-class compared to its
**resource** monitoring. If your main worry is "did the box fall
over?", Beszel handles it. If you need rich HTTP checks (status
code patterns, response-time histograms, keyword matching), Kuma
is the better tool.

A common pairing: Beszel for fleet resource monitoring + Uptime
Kuma for service uptime — both running as small Docker containers
on the same host.

## 3. Prometheus + blackbox_exporter — the heavy option

If you already run Prometheus for metrics, adding
[`blackbox_exporter`](https://github.com/prometheus/blackbox_exporter)
is the path of least resistance for uptime probing.

### How it fits

```
[prometheus] --scrape--> [blackbox_exporter:9115] --probe--> target
       │
       └──> alertmanager --> pagerduty / slack / email
```

The blackbox_exporter runs probes (`http_2xx`, `http_post_2xx`,
`tcp_connect`, `icmp`, `dns`, `ssh_banner`, ...). Prometheus
scrapes the exporter, evaluates an `up{job="blackbox"} == 0`
rule, and fires an alert via Alertmanager.

### Sample config

`prometheus.yml`:

```yaml
scrape_configs:
  - job_name: blackbox
    metrics_path: /probe
    params:
      module: [http_2xx]
    static_configs:
      - targets:
          - https://example.com/healthz
          - https://api.example.com/v1/ping
    relabel_configs:
      - source_labels: [__address__]
        target_label: __param_target
      - source_labels: [__param_target]
        target_label: instance
      - target_label: __address__
        replacement: blackbox-exporter:9115
```

`blackbox.yml` (the exporter's module config):

```yaml
modules:
  http_2xx:
    prober: http
    timeout: 5s
    http:
      valid_status_codes: [200]
      preferred_ip_protocol: ip4
```

Alert rule:

```yaml
groups:
  - name: blackbox-up
    rules:
      - alert: BlackboxProbeFailed
        expr: probe_success{job="blackbox"} == 0
        for: 2m
        labels: { severity: critical }
        annotations:
          summary: "Blackbox probe failing for {{ $labels.instance }}"
```

### When to pick this

You're already paying the Prometheus tax (Prometheus server,
Grafana, Alertmanager, a label taxonomy, retention storage). In
that environment, adding blackbox is one extra scrape config and
one alert rule. Outside an existing Prometheus install, the
operational overhead is too high — Uptime Kuma is faster to ship.

## 4. statping-ng — the legacy option

[**statping-ng**](https://github.com/statping-ng/statping-ng) is a
Go fork of the original statping. It works, has a decent UI, but
the project is maintained by a small team and has fewer alert
channels than Uptime Kuma.

The honest recommendation in 2026: pick statping-ng only if you
have an existing deployment you're not ready to migrate, or if
Uptime Kuma's license (MIT, fine) or Node.js footprint is a
problem for your environment.

## 5. Comparison table

| | Uptime Kuma | Beszel | Prometheus + blackbox | statping-ng |
|---|---|---|---|---|
| Stack | Node.js + SQLite | Go + SQLite | Go + external TSDB | Go + SQLite |
| HTTP / TCP / ICMP probes | rich | basic | rich (via modules) | basic |
| Status page | built-in | none (use third party) | none (Grafana panel) | built-in |
| Resource monitoring | no | yes (agent) | yes (node_exporter) | no |
| Notification channels | ~90 | ~10 | unlimited via Alertmanager | ~15 |
| HA story | single-instance + Postgres | single-instance | HA by design (cluster) | single-instance |
| Best when | you want one tool that does it all | fleet resource + uptime | you're already on Prometheus | maintaining an old install |

## Related resources

- [`1-uptime-content`](../1-uptime-content/1-uptime-content.en.md) — overview
- [`4-hosted-monitors`](../4-hosted-monitors/4-hosted-monitors.en.md) — if you don't want to run anything
- [`6-github-actions-as-monitor`](../6-github-actions-as-monitor/6-github-actions-as-monitor.en.md) — independent second layer
- [Uptime Kuma](https://github.com/louislam/uptime-kuma) on GitHub
- [Beszel](https://github.com/henrygd/beszel) on GitHub
- [Prometheus blackbox_exporter](https://github.com/prometheus/blackbox_exporter) on GitHub

## License

This article is part of the `x-cmd/uptime` repo and is licensed under
Apache License 2.0.
