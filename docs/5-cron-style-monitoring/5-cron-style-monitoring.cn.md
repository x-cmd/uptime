---
x-title: Cron 风格心跳监控
x-desc: Healthchecks.io、Cronitor、Dead Man's Snitch —— 用于"任务根本没跑"这种故障模式。批处理任务、ETL、定时脚本、备份。
x-sidebar: Cron 风格监控
x-keywords: healthchecks io, cronitor, dead man's snitch, 心跳监控, cron 任务监控, 批处理任务监控, ping url
x-json-ld:
  '@context': https://schema.org
  '@graph':
    - '@type': TechArticle
      headline: 'Cron 风格心跳监控'
      inLanguage: 'cn'
      about: '心跳 / cron 风格监控'
---

# Cron 风格心跳监控

> **本文内容。** 第一篇文章
> ([`1-uptime-content`](../1-uptime-content/1-uptime-content.cn.md))
> 只顺带提了 cron 风格监控。本文深入:什么时候"任务有没有跑?"才是
> 正确问题(以及 HTTP 探测是错的工具),以及 2026 年用得上的三家
> —— **Healthchecks.io**、**Cronitor**、**Dead Man's Snitch** ——
> 各家多少钱。

cron 风格监控回答的是一个和 HTTP uptime 不同的问题:**"我那个定时
任务跑了没?"** 而不是"我的 HTTP 端点响应吗?"。两个问题容易混、
容易用错工具。本文讲什么时候 cron 风格才是你真正需要的。

## 1. cron 风格什么时候对

你有一个定时任务 —— cron 条目、ETL pipeline、备份脚本、周期性数据
刷新。你关心的故障模式:

- 任务**根本没跑**(cron 守护进程崩了、容器被取消调度、deploy 关掉了
  schedule)。
- 任务**开了但没跑完**(卡在网络调用上、被 OOM kill、丢了 DB 连接)。
- 任务**跑完但失败了**(行数对不上、exit code 非零)。

HTTP 探测这些一个都查不到。HTTP 探测能告诉你**你的 web 服务器**在
不在;它不能告诉你昨天凌晨 3 点的备份有没有完成。

cron 风格工具的解法是**翻转任务和监控的关系**:

```
HTTP monitor:    monitor → pings → target           (monitor 是主动的)
Cron monitor:    job     → pings → monitor         (job 是主动的)
```

你的任务在开始、成功、失败时分别 ping 一下监控。监控在预期 ping 没
到时告警。

## 2. Healthchecks.io —— 开源选项

[**Healthchecks.io**](https://healthchecks.io/) 是默认选择。它是开源
的(可以[自托管](https://github.com/healthchecks/healthchecks)同样的
后端),免费档慷慨。

### ping 模型

每个 check 是一个独立 URL。你的任务可以发三种事件:

- **开始** —— `curl -fsSL https://hc-ping.com/<uuid>/start`
- **成功** —— `curl -fsSL https://hc-ping.com/<uuid>`
- **失败** —— `curl -fsSL https://hc-ping.com/<uuid>/fail`

你告诉 Healthchecks.io **周期**(比如"每天")和 **grace**(比如"1 小
时")。周期过了还没收到 ping,就告警。grace 用来兜住任务晚几分钟这
种合法情况。

### 完整示例

凌晨 3 点的数据库备份,2 小时 grace:

```sh
#!/bin/sh
# /etc/cron.d/backup-db
UUID='<从 Healthchecks UI 复制>'

curl -fsSL "https://hc-ping.com/$UUID/start"

pg_dump --file=/backups/db-$(date +%Y%m%d).sql.gz mydb \
  || curl -fsSL "https://hc-ping.com/$UUID/fail"

# 真正跑完才 ping success。
curl -fsSL "https://hc-ping.com/$UUID"
```

cron 条目停跑了,第二天早上 Healthchecks.io 会发邮件 / Slack /
PagerDuty 通知你。cron 跑了但备份失败,`/fail` ping 让告警从"任务
晚了"变成"任务失败" —— 排查时很有用。

### 价格

- **免费** —— 开源项目 20 个 check,任意间隔。
- **Standard**(2026 年约 $20/mo)—— 200 个 check,周期最小 1 分钟。
- 再上一档是给超大 check 数的。

OSS 自托管是同一份代码、自己的 Postgres、自己的成本 —— 没部署过的
话几小时就能起来。

## 3. Cronitor —— 偏意见的 cron 任务可观测性

[**Cronitor**](https://cronitor.io/) 老一些、更企业向。同样的 ping
模型,但额外有:

- cron 表达式解析器,在定义时就检测不可能的 schedule(比如
  "Feb 30")。
- 运行指标:任务比上周跑得快/慢?日志输出形态变了?
- 与 Kubernetes CronJob、ECS、Airflow 等的 telemetry 风格集成。

### 价格

- **免费** —— 5 个 check。
- **Startup**(2026 年约 $25/mo)—— 25 个 check,加 schedule 解析
  功能。
- 再上一档是给有上千个 cron 条目的团队。

### 何时选 Cronitor 而不是 Healthchecks.io

你有一**批定时任务**,想要一个统一面板,能抓出"schedule 写错"和"跑
得慢"。对几个 cron 条目,Healthchecks.io 更合用。

## 4. Dead Man's Snitch —— 这个领域的开山祖师(现在归 Sentry)

[**Dead Man's Snitch**](https://deadmanssnitch.com/) 是这个类别最
早的商业产品。2023 年被 [Sentry](https://sentry.io/) 收购,现在作为
Sentry 的 Cron Monitoring 产品的一部分交付。

如果你是 Sentry 现成客户,你可能已经开了 Cron Monitoring —— 同样的
ping 模型,与 Sentry issue 集成。

如果不在 Sentry 上、想要一个专门的 cron 监控供应商,Healthchecks.io
更显然的选择。Dead Man's Snitch / Sentry Cron Monitoring 适合想让
cron 告警和应用错误走同一条事故流水线的场景。

## 5. 横评

| | Healthchecks.io | Cronitor | Dead Man's Snitch |
|---|---|---|---|
| 开源后端 | 是 | 否 | 否 |
| 免费档 | 开源项目 20 check、任意间隔 | 5 check | 通过 Sentry 限量 |
| 最便宜付费 | ~$20/mo | ~$25/mo | 经 Sentry 套餐 |
| Ping 端点 | /start、/(success)、/fail | 类似 | 类似 |
| Schedule 解析 | 基础 | 强(检测不可能的) | 基础 |
| 运行指标 | 基础 | 有(时长、日志形态) | 基础 |
| 自托管选项 | 有(Postgres + Docker) | 无 | 无 |
| 何时选 | 默认;OSS 自托管可用 | 大量 cron 条目的 fleet | 已经在用 Sentry |

## 6. cron 风格什么时候**错**

常见误用:

- **探测 HTTP 端点。** 这是 HTTP 监控的活儿;见
  [`3-self-hosted-monitors`](../3-self-hosted-monitors/3-self-hosted-monitors.cn.md)
  或 [`4-hosted-monitors`](../4-hosted-monitors/4-hosted-monitors.cn.md)。
  Healthchecks.io 会接受外部 ping 当作"ping 到了" —— 但它没法告诉
  你端点是不是真的在响应。
- **代替你的应用健康检查。** Kuma / UptimeRobot 探的 `/healthz`
  端点告诉你应用活着。cron 监控的 ping 对应用状态一无所知。
- **监控交互式事件。** 用户操作流(注册、下单)最好用应用层可观测
  性来做,不是心跳。

问题问对了,用对工具。如果问题是"我的定时任务跑了没?",本文介绍
的 cron 风格工具就是答案。

## 相关资源

- [`1-uptime-content`](../1-uptime-content/1-uptime-content.cn.md) —— 概览
- [`3-self-hosted-monitors`](../3-self-hosted-monitors/3-self-hosted-monitors.cn.md) —— HTTP 探测,自托管
- [`4-hosted-monitors`](../4-hosted-monitors/4-hosted-monitors.cn.md) —— HTTP 探测,托管
- [`7-decision-guide`](../7-decision-guide/7-decision-guide.cn.md) —— 按场景选
- [Healthchecks.io](https://healthchecks.io/) 官网
- [Healthchecks 自托管仓库](https://github.com/healthchecks/healthchecks) GitHub

## 许可

本文是 `x-cmd/uptime` 仓库的一部分,采用 Apache License 2.0 许可。
