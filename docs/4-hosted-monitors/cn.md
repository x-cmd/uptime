---
x-title: 托管 uptime 监控
x-desc: UptimeRobot、Better Stack、Better Uptime、Hyperping —— 价格、监控类型、告警通道、status-page-as-a-product。什么时候托管胜过自托管。
x-sidebar: 托管监控
x-keywords: uptimerobot, better stack, better uptime, hyperping, 托管监控, status page as a product, saas 监控
x-json-ld:
  '@context': https://schema.org
  '@graph':
    - '@type': TechArticle
      headline: '托管 uptime 监控'
      inLanguage: 'cn'
      about: '托管 / SaaS uptime 监控'
---

# 托管 uptime 监控

> **本文内容。** 第一篇文章
> ([`1-uptime-content`](../1-uptime-content/cn.md))
> 只顺带提了托管监控。本文深入 2026 年真正用得上的四个 —— **UptimeRobot**、
> **Better Stack**、**Better Uptime**、**Hyperping** —— 各家擅长什么、
> 价格多少、以及"花钱让别人做"什么时候胜过自己跑容器。

不想运维任何基础设施时,托管监控就是正确答案:别人家的机器去探测
你的端点,出问题就打电话。代价 —— 自托管工具没有 —— 是**当你和托管
监控厂商的账户本身出问题(或欠费宽限期过了),你的监控也停了**。
建议的缓解在 [`6-github-actions-as-monitor`](../6-github-actions-as-monitor/cn.md)。

## 1. UptimeRobot —— 默认免费选项

[**UptimeRobot**](https://uptimerobot.com/) 自 2010 年就有了。免费版
**50 个监控、5 分钟间隔**,支持 HTTP(S)、ping、port、keyword 检查。
邮件和一小批 webhook 通道免费。

### 免费版能拿到什么

- 50 个监控、5 分钟检查间隔(免费版无法更紧)。
- 1 个状态页(UptimeRobot 品牌)。
- 5 分钟粒度对多数免费用户是瓶颈 —— 故障检测要 0-5 分钟,通常
  接近 5 分钟才被发现。

### 付费解锁什么

- **Pro**(2026 年约 $7/mo):1 分钟间隔、更多监控、短信告警、多个
  状态页。
- 再上一档加团队功能、事故管理、SLA 报告。价格到企业级只在监控
  数非常大时才上得去。

### 何时选它

个人站点、副业项目、小微企业的默认。UI 实用主义 —— 能干活。主要
槽点是**免费版要 5 分钟**,意味着一个故障窗口最长 5 分钟才会被
你听见。对故障本身就亏钱的付费 SaaS,Pro 的 1 分钟间隔值得花。

## 2. Better Stack —— 现代,以状态页为先

[**Better Stack**](https://betterstack.com/uptime) 是新一代选项。卖
点是"Uptime + Status Page + On-call"做成一个产品:

- **Uptime** —— HTTP(S)、TCP、ICMP、keyword、JSON path、SSL 到期
  检查。最便宜付费档 30 秒间隔。
- **Status page** —— 打磨过的、Atlassian-Statuspage 风格的页面,带
  事故发布。
- **On-call** —— 排班、升级、与 PagerDuty / Slack / MS Teams 集成。

### 价格一览

- **免费**:第一个监控(1 分钟间隔)+ 一个状态页。
- **Starter** 档:小团队 2026 年约 $25/mo,多个状态页、更丰富的
  告警路由。
- **Enterprise** 规模到几百个监控,带 SOC 2、审计日志、SSO。

### 何时选它

你在做一个有付费用户的产品,状态页是产品表面的一部分 —— 不仅是
附属品。状态页编辑器是差异化:事故可手动发布、可从 uptime 故障
自动检测、可两者兼有。如果你曾在凌晨三点手工拼过一个 HTML 状态
页,这个价值立刻兑现。

## 3. Better Uptime —— 事故管理为先

[**Better Uptime**](https://betteruptime.com/) 形态和 Better Stack
相似,但更偏 on-call / 事故这一侧:

- **Uptime** 检查和 Better Stack 相当。
- **Status page** 含。
- **On-call 排班**、升级,以及 Sentry 风格的事故工作流(复盘模板、
  状态更新、retros)。

差异化在于事故管理工作流。如果你的团队已经在用 PagerDuty 或
Opsgenie,只需要 uptime,Better Uptime 就过重了。如果团队小,想
一份账单搞定监控 + 状态 + on-call + 复盘,Better Uptime 在事故流程
上的意见比 Better Stack 更明确。

### 何时选它

小团队、没有现成的 PagerDuty 订阅、想一家供应商搞定监控 + 状态 +
on-call + 复盘。小档价格和 Better Stack 相当。

## 4. Hyperping —— 小团队精简方案

[**Hyperping**](https://hyperping.com/) 是四家里最小的一个 —— 一个
创始人、产品紧凑,价格是 UptimeRobot Pro 的一半左右。功能类似
UptimeRobot Pro:HTTP(S)、keyword、ping、port、SSL 检查;状态页;
邮件 + Slack + webhook 告警。

### 何时选它

你是独立开发者或微型团队,想要比 UptimeRobot 免费版更好的间隔和更
好看的状态页,但不需要 Better Stack / Better Uptime 的事故管理栈。
Hyperping 的形态正合"盯几个站点、拿到好看的告警、上一个状态页"。

## 5. 横评

| | UptimeRobot | Better Stack | Better Uptime | Hyperping |
|---|---|---|---|---|
| 免费版 | 50 监控、5 分钟间隔 | 1 监控、1 分钟间隔 | 限时试用 | 2026 年暂无 |
| 最便宜付费 | ~$7/mo(Pro,1 分钟) | ~$25/mo(Starter) | ~$25/mo | ~$5-10/mo |
| 最小间隔(付费) | 1 分钟 | 30 秒 | 30 秒 | 1 分钟 |
| 监控类型 | HTTP(S)、ping、port、keyword | + JSON path、SSL 到期 | 类似 | HTTP(S)、ping、port、keyword |
| 状态页 | 有(多个需付费) | 有,打磨过 | 有,打磨过 | 有 |
| On-call / 排班 | 无 | 有(付费) | 有(差异化) | 无 |
| 事故工作流 | 基础 | 好 | 四家最佳 | 基础 |
| 何时选 | 个人站点 / 副业 | 状态页即产品的 SaaS | 没有 PagerDuty 的小团队 | 微型团队,比 Kuma 更简单 |

## 6. 什么时候托管胜过自托管

平衡点大致在**自己跑监控的运维成本**:

- 一个小型 Uptime Kuma 容器装几分钟就行,但它需要打补丁、SQLite
  备份、以及有人盯它跑的那台机器。
- 托管监控一张信用卡 + 几分钟配置,剩下的厂商兜底。

如果**没有专职 ops**、**也没有现成基础设施**挂监控,2026 年几乎
总是托管对。一旦你这两样都有其中之一 —— 已有跑 Prometheus 的服务
器、能给容器打补丁的运维 —— 自托管就在成本和数据驻留上开始胜出。

如果价格是决定因素:UptimeRobot 免费版 50 监控 $0/mo;自托管付
CPU + 内存 + 你的时间;Better Stack / Better Uptime 付费档 $25/mo
起,跟租一台小 VPS 差不多。

## 7. 托管监控的单点故障

托管监控在你的依赖图里又多了一家供应商。两种故障模式:

- **监控本身挂了**(罕见但确实会;他们的面板和你目标在同一个互联
  网上)。他们的 UI 上不会有任何东西告诉你。
- **你的账户过期了**(忘续费、信用卡过期)。监控停止探测,告警停
  止。

纵深防御模式:把托管监控和 GitHub Actions cron(第 6 篇)配对,
后者探测**监控发布的状态页 URL**。状态页在 GitHub 这边变红,说明
托管监控本身坏了。

## 相关资源

- [`1-uptime-content`](../1-uptime-content/cn.md) —— 概览
- [`3-self-hosted-monitors`](../3-self-hosted-monitors/cn.md) —— 想自托管时的替代
- [`5-cron-style-monitoring`](../5-cron-style-monitoring/cn.md) —— cron 任务而非 HTTP 端点
- [`6-github-actions-as-monitor`](../6-github-actions-as-monitor/cn.md) —— 独立第二层
- [`7-decision-guide`](../7-decision-guide/cn.md) —— 按场景选择

## 许可

本文是 `x-cmd/uptime` 仓库的一部分,采用 Apache License 2.0 许可。
