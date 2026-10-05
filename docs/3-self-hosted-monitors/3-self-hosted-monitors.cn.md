---
x-title: 自托管 uptime 监控
x-desc: Uptime Kuma、Beszel、Prometheus + blackbox_exporter、statping-ng。安装、配置、告警通道、横评。
x-sidebar: 自托管监控
x-keywords: uptime kuma, beszel, prometheus, blackbox exporter, statping, 自托管监控, docker
x-json-ld:
  '@context': https://schema.org
  '@graph':
    - '@type': TechArticle
      headline: '自托管 uptime 监控'
      inLanguage: 'cn'
      about: '自托管服务监控工具'
---

# 自托管 uptime 监控

> **本文内容。** 第一篇文章
> ([`1-uptime-content`](../1-uptime-content/1-uptime-content.cn.md))
> 只顺带提了自托管监控。本文深入:**Uptime Kuma**、**Beszel**、
> **Prometheus + blackbox_exporter**、**statping-ng** 这四个 2026 年
> 真正用得上的选项的安装、配置、告警通道、横评。

"自托管"意味着:你跑一台服务器(或服务器上的一个容器)去做探测、
发告警。优点是:不依赖任何第三方的计费、宕机策略、数据驻留策略。
缺点是:你多了一个东西要保证它在跑 —— 这也是为什么你应该监控**监控
本身**(见 [`6-github-actions-as-monitor`](../6-github-actions-as-monitor/6-github-actions-as-monitor.cn.md))。

## 1. Uptime Kuma —— 现代默认选择

[**Uptime Kuma**](https://github.com/louislam/uptime-kuma) 是
Node.js + SQLite 应用,UI 漂亮。原生支持 HTTP(S)、TCP、ping、DNS、
push、Docker 容器、甚至 steam-game-server 检测。告警通道约 90 个
(Telegram、Slack、Discord、邮件、经 Twilio 的短信、ntfy、Gotify、
Pushover 等)。

### 用 Docker 安装

标准安装:

```sh
docker run -d \
  --name uptime-kuma \
  --restart=always \
  -p 3001:3001 \
  -v uptime-kuma:/app/data \
  louislam/uptime-kuma:1
```

Web UI 在 `http://your-host:3001`。创建的第一个账号是 admin。SQLite
存在命名卷里,容器重启不会丢状态。

加固一点的部署:把它放在 Caddy/Nginx/Traefik 这类反向代理后面、配
TLS、按 IP 白名单限制管理 UI。公开的状态页(`/status/<slug>`)
本身就是设计成对外的 —— URL 按这个意图规划。

### 添加监控项

UI 里:**Add Monitor → Type → HTTPS**。最少字段是友好名、URL、间隔
(默认镜像 60 秒;多数团队对核心用 60s、其他用 300s)。可接受状态
码默认 `200-299`,也可以收紧到单一状态码。

超过一两个监控项之后,用 JSON import 配置(Settings → Backup →
Import),而不是每次都点 UI。

### 顺带出状态页

每个 monitor group 都能在 `/status/<slug>` 出独立的公开状态页。页面
无需鉴权,就是给公开看的 —— Uptime Kuma 的整个设计就是"一键出状态页"。
多个状态页共存,可以按服务族分。

### 注意事项

- 1.x 是当前活跃分支;2.x 重写 2026 年底仍在进行。今天新部署 pin 到
  `louislam/uptime-kuma:1`。
- SQLite 对单实例够用。要 HA,用项目文档化的 PostgreSQL 后端(也
  是 1.x),或者跑两个实例 + 共享外部数据库,放在负载均衡后面。
- 容器自带的 `node` 不会独立于上游 release 打补丁 —— 镜像保持更新。

## 2. Beszel —— 轻量 + 感知服务器资源

[**Beszel**](https://github.com/henrygd/beszel) 是 Go + SQLite 应用,
范围不同:除了 HTTP/TCP/ICMP uptime 检测,它还自带**每主机 agent**
上报 CPU、内存、磁盘、网络。架构是 hub-and-spoke —— 跑一个 Beszel
**hub**(web UI)和若干 **agent**(每台要监控的服务器一个)。

### 安装

Hub:

```sh
docker run -d \
  --name beszel-hub \
  --restart=always \
  -p 8090:8090 \
  -v ./beszel-data:/beszel_data \
  henrygd/beszel
```

Agent(每台要监控的服务器上):

```sh
docker run -d \
  --name beszel-agent \
  --restart=always \
  --network host \
  -e PORT=45876 \
  -e KEY="<从 hub UI 复制>" \
  henrygd/beszel-agent
```

`KEY` 在 hub UI 加新 system 时生成。agent 通过 host 网络和 hub 通信;
45876 只在受信侧暴露。

### 何时选 Beszel 而不是 Kuma

Beszel 的 **uptime** 检查不如它的**资源**监控强。如果你主要担心
"这台机器是不是挂了",Beszel 胜任。如果你需要丰富的 HTTP 检查(状态
码模式、响应时间直方图、关键字匹配),Kuma 更合适。

常见组合:Beszel 盯 fleet 资源 + Uptime Kuma 盯服务 uptime —— 两个
小容器跑在同一台机器上。

## 3. Prometheus + blackbox_exporter —— 重型方案

如果你已经在跑 Prometheus 做指标,加一个
[`blackbox_exporter`](https://github.com/prometheus/blackbox_exporter)
就是最少改动增加 uptime 探测的路径。

### 怎么接进去

```
[prometheus] --scrape--> [blackbox_exporter:9115] --probe--> target
       │
       └──> alertmanager --> pagerduty / slack / 邮件
```

blackbox_exporter 跑探测(`http_2xx`、`http_post_2xx`、`tcp_connect`、
`icmp`、`dns`、`ssh_banner` 等)。Prometheus 抓取 exporter、评估
`up{job="blackbox"} == 0` 规则,经 Alertmanager 发告警。

### 配置示例

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

`blackbox.yml`(exporter 的 module 配置):

```yaml
modules:
  http_2xx:
    prober: http
    timeout: 5s
    http:
      valid_status_codes: [200]
      preferred_ip_protocol: ip4
```

告警规则:

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

### 何时选这个

你已经为 Prometheus 交了"税"(Prometheus server、Grafana、
Alertmanager、标签策略、保留存储)。在那个环境里加 blackbox 就
多一段 scrape 配置 + 一条告警规则。脱离现有 Prometheus,运维负担
就太重 —— Uptime Kuma 上线更快。

## 4. statping-ng —— 历史遗留选项

[**statping-ng**](https://github.com/statping-ng/statping-ng) 是原
statping 的 Go fork。能跑、UI 还可以,但团队小,告警通道数比 Uptime
Kuma 少。

2026 年的诚实建议:只有在你有现存部署不想迁移,或者 Uptime Kuma 的
MIT 许可 / Node.js footprint 在你的环境里有冲突时,才选 statping-ng。

## 5. 横评

| | Uptime Kuma | Beszel | Prometheus + blackbox | statping-ng |
|---|---|---|---|---|
| 技术栈 | Node.js + SQLite | Go + SQLite | Go + 外部 TSDB | Go + SQLite |
| HTTP / TCP / ICMP 探测 | 丰富 | 基础 | 丰富(经 module) | 基础 |
| 状态页 | 内置 | 无(需第三方) | 无(Grafana 面板) | 内置 |
| 资源监控 | 否 | 是(agent) | 是(node_exporter) | 否 |
| 告警通道数 | ~90 | ~10 | 不限(经 Alertmanager) | ~15 |
| HA 路径 | 单实例 + Postgres | 单实例 | 天然 HA(集群) | 单实例 |
| 何时选 | 想一个工具搞定 | fleet 资源 + uptime | 已经在用 Prometheus | 维护旧部署 |

## 相关资源

- [`1-uptime-content`](../1-uptime-content/1-uptime-content.cn.md) —— 概览
- [`4-hosted-monitors`](../4-hosted-monitors/4-hosted-monitors.cn.md) —— 不想自托管时的替代
- [`6-github-actions-as-monitor`](../6-github-actions-as-monitor/6-github-actions-as-monitor.cn.md) —— 独立第二层
- [Uptime Kuma](https://github.com/louislam/uptime-kuma) GitHub
- [Beszel](https://github.com/henrygd/beszel) GitHub
- [Prometheus blackbox_exporter](https://github.com/prometheus/blackbox_exporter) GitHub

## 许可

本文是 `x-cmd/uptime` 仓库的一部分,采用 Apache License 2.0 许可。
