---
x-title: 决策指南 —— 哪种场景用哪种监控
x-desc: 按场景选监控策略。个人站点、小企业、SaaS、内部工具、定时任务。成本表、纵深防御模式。
x-sidebar: 决策指南
x-keywords: 决策指南, 场景, 个人站点, 小企业, saas, 内部工具, 定时任务, 纵深防御, 成本
x-json-ld:
  '@context': https://schema.org
  '@graph':
    - '@type': TechArticle
      headline: '决策指南 —— 哪种场景用哪种监控'
      inLanguage: 'cn'
      about: '选择合适的监控策略'
---

# 决策指南 —— 哪种场景用哪种监控

> **本文内容。** 前六篇文章深入每个选项。本文是综合:**哪种监控策略
> 适合哪种场景**、各多少钱、以及什么时候组合多个工具做纵深防御。

目标是一张一页可查表,把"我是 ___ 有 ___ 监控需求"映射到"干这活
儿合适的工具"。多数真实场景需要**两个**工具 —— 一个主要监控 +
一个独立的第二层。

## 1. 五种场景

下面的划分覆盖 2026 年个人和小团队 ~95% 的监控需求。更大的企业有
专职 SRE 团队,大概已经在跑 Prometheus + 一家供应商 —— 这些情况
不在本文范围。

| # | 场景 | "我在监控什么?" |
|---|---|---|
| A | **个人站点** | 一个 URL,风险低,只有自己会注意到 |
| B | **小企业 / agency** | 几个客户站点,uptime 是计费相关 |
| C | **有付费用户的 SaaS** | 产品的 web app + API + 状态页即产品 |
| D | **内部工具 / dev 基础设施** | Jenkins、内部 API、dev 面板 |
| E | **定时任务** | 夜间备份、ETL pipeline、批处理报告 |

每个场景下面列主要推荐、可选的第二层、以及 cron 风格工具(若适用)。

## 2. 场景 A —— 个人站点

**任务:** 一个个人站点,风险低,只有你会注意到宕机。预算敏感。

**主要:** [UptimeRobot](https://uptimerobot.com/) 免费档(50 监控、
5 分钟间隔) —— 大多数个人站点要监控的端点远不到 50 个。

**可选第二层:** 一个
[GitHub Actions cron `*/15 * * * *`](https://docs.github.com/actions/using-workflows/events-that-trigger-workflows#schedule)
去探测你的状态页 URL。公开仓库每月大概花 5 分钟 Actions 配额。

**为何不自托管?** 在自己的 VPS 上跑 Uptime Kuma 看个人站点,是
运维债。托管选项免费,自托管选项消耗你花不起的时间。

**总成本:$0/mo。**

## 3. 场景 B —— 小企业 / agency

**任务:** 几个客户站点;客户会注意到宕机;uptime 是计费相关。

**主要:** [UptimeRobot Pro](https://uptimerobot.com/) 约 $7/mo,
拿到 1 分钟间隔、短信告警、多个状态页(每个客户一个)。

**主要替代:** 在 $5/mo VPS 上自托管
[Uptime Kuma](https://github.com/louislam/uptime-kuma) —— 成本
相当,告警通道更多,搭起来费时。

**第二层:** GitHub Actions cron `*/15 * * * *`,探测每个客户的
公开状态页 URL。每月花几分钟。

**为何这个组合?** 托管主要监控提供丰富的告警。GitHub 这一层
兜住"监控账户过期了"或"监控本身挂了"这种情况。

**总成本:$7-12/mo,全托管。**

## 4. 场景 C —— 有付费用户的 SaaS

**任务:** 产品有付费用户;状态页是产品表面的一部分;宕机直接亏
收入。

**主要:** [Better Stack](https://betterstack.com/uptime) 或
[Better Uptime](https://betteruptime.com/) —— 两家都有打磨过的
状态页、事故发布、on-call 排班。Better Stack 偏状态页为先,Better
Uptime 偏事故管理意见化。

**主要替代:** 自托管 Uptime Kuma + 自托管状态页。更便宜,但状态
页 UI 和事故工作流要自己写。

**第二层:** 公开仓库用 GitHub Actions cron `*/5 * * * *`(免费);
私有仓库 Team 档用 `*/15 * * * *`(付费)。cron 探测状态页 URL,
不是应用 URL —— 这样 GitHub 这边看到的和你的 SaaS 独立。

**cron 风格附加(若适用):** [Healthchecks.io](https://healthchecks.io/)
盯夜间 ETL、计费、定时报告任务。开源项目免费,其他约 $20/mo。

**为何这个组合?** 打磨过的主要监控给团队和客户可见的状态页;独
立的第二层抓"监控本身挂了";cron 风格回答"我的夜间任务跑了没?",
HTTP 监控答不了这个问题。

**总成本:$25-50/mo 托管 + $0-20/mo Healthchecks.io。**

## 5. 场景 D —— 内部工具 / dev 基础设施

**任务:** 内部面板、Jenkins、dev API。宕机影响团队速度,但不直接
亏收入。可见性重要;"监控的监控"不那么重要。

**主要:** 在你已有的容器上自托管
[Uptime Kuma](https://github.com/louislam/uptime-kuma)。Slack 告警
进工程频道。

**可选搭配:** 在同一台机器自托管 [Beszel](https://github.com/henrygd/beszel)
—— 给跑 Jenkins、数据库等的服务器加上资源监控。

**第二层:** GitHub Actions cron `*/30 * * * *` 轻量够用;团队的通
知流程本身就是真正的第二层。

**为何不托管?** 大多数内部基础设施不暴露公网 —— Better Stack /
UptimeRobot 的外部探测看不见。自托管是天然形态。

**总成本:$0/mo 软件 + 你已有的机器成本。**

## 6. 场景 E —— 定时任务

**任务:** 夜间备份、ETL pipeline、周期报告、定时清理。问题是
"任务跑了没?",不是"端点在不在?"。

**主要:** [Healthchecks.io](https://healthchecks.io/) —— 开源,
开源项目免费,OSS 自托管可。每个任务一个 UUID,ping `/start`、
`/`、`/fail`。

**主要替代:** [Cronitor](https://cronitor.io/) 当你有一批 cron
条目,想要 schedule 解析 + 运行指标。

**何时加 HTTP 监控:** 如果你的定时任务会推到你在乎的 HTTP 端点
(webhook 接收器、分析 ingestion),用 Uptime Kuma 或 UptimeRobot
另外探那个端点。HTTP 探测另外抓"接收器挂了",独立于"任务没跑"。

**总成本:$0-25/mo(OSS 项目免费)。**

## 7. 成本表

| 场景 | 主要 | 第二层 | cron 附加 | 总计 |
|---|---|---|---|---|
| A. 个人站点 | UptimeRobot 免费 | GH Actions `*/15` | — | **$0/mo** |
| B. 小企业 | UptimeRobot Pro $7 | GH Actions `*/15` | — | **$7-12/mo** |
| C. SaaS 有付费用户 | Better Stack $25-50 | GH Actions `*/5`(公开) | Healthchecks.io $0-20 | **$25-70/mo** |
| D. 内部工具 | Uptime Kuma 自托管 | GH Actions `*/30` | — | **$0 + 机器成本** |
| E. 定时任务 | Healthchecks.io $0-20 | UptimeRobot/Kuma 若有 HTTP | — | **$0-20/mo** |

数字是 2026 年末的量级。预算前自己看供应商定价页。

## 8. 纵深防御 —— 为什么"两个"是底线

跨场景反复出现的主题:每个主要监控都有一个主要监控自己抓不到的
单点故障。两种模式:

- **监控本身挂了。** 托管监控罕见发生,自托管更常见(它跑的那台
  机器)。
- **你和监控的账户过期了。** 人会忘。

最便宜的独立第二层是 GitHub Actions cron(第 6 篇)。cron 探测主
要监控**发布的状态页 URL**,不是你的应用 URL。状态页在 GitHub 这
边变红,说明主要监控本身坏了 —— 不必等有人发现主要监控哑了。

场景 A、B、C 这一层不用想;每月就花几个 Actions 分钟。场景 D,
团队的通知流程实际上就是充分的第二层。场景 E,cron 风格监控的
职责是抓"没跑" —— 只有当有下游 HTTP 端点要看时,才加 HTTP 监控。

## 9. 决策树,一段话版

> *我是个人站点 / 小企业 / SaaS / 内部工具 / 定时任务运营者。*
> 我想监控 **HTTP 端点**:已经运营服务器、有运维人员,就自托管 Kuma,
> 否则选 UptimeRobot 免费(个人)或 Pro(小企业),或 Better Stack /
> Better Uptime(SaaS)。加一个 **GitHub Actions cron `*/15`** 探测
> 我的状态页 URL 当第二层。如果我有**定时任务**,叠 **Healthchecks.io**
> —— 每个任务 `/start`、`/`、`/fail` —— 因为 HTTP 探测答不了"我的
> cron 跑了没?"。对**只有内网可达的服务**,自托管 Uptime Kuma,配
> 较轻的 GitHub Actions 频率。

## 相关资源

- [`1-uptime-content`](../1-uptime-content/cn.md) —— 概览
- [`2-the-catalog`](../2-the-catalog/cn.md) —— 本仓目录
- [`3-self-hosted-monitors`](../3-self-hosted-monitors/cn.md) —— 自托管选项
- [`4-hosted-monitors`](../4-hosted-monitors/cn.md) —— 托管选项
- [`5-cron-style-monitoring`](../5-cron-style-monitoring/cn.md) —— cron 风格选项
- [`6-github-actions-as-monitor`](../6-github-actions-as-monitor/cn.md) —— 第二层配方

## 许可

本文是 `x-cmd/uptime` 仓库的一部分,采用 Apache License 2.0 许可。
