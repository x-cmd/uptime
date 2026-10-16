---
x-title: Uptime、状态页与监控
x-desc: Uptime 在三个层面上的含义——本地 `uptime(1)` 命令、本仓的 provider 状态页目录、以及监控自有服务的实操方法（自托管工具、GitHub Actions）。
x-sidebar: Uptime —— 基础与监控
x-keywords: uptime, 状态页, 监控, uptime-kuma, github actions, cron, 健康检查, 可观测性
x-json-ld:
  '@context': https://schema.org
  '@graph':
    - '@type': TechArticle
      headline: 'Uptime、状态页与监控'
      inLanguage: 'cn'
      about: 'Uptime 与服务监控'
---

# Uptime、状态页与监控

> **TL;DR.** Uptime 这个词出现在三个不同的尺度上。(1) 本地的
> [`uptime(1)`](https://man.x-cmd.com/man1/uptime) 命令告诉你这台机器跑了多久。
> (2) **状态页**告诉你所依赖的服务是否活着。(3) **监控**在某个你关心的事
> 停止响应的那一刻自动通知你。本文覆盖全部三个,第三个给出可直接复制的模板。

这是 uptime 主题库的第一篇文章。文中的内容接受修改 PR —— 见
[`CONTRIBUTING.md`](../../CONTRIBUTING.md)。

## 1. 本地 `uptime(1)` 与 `x uptime`

### 标准 `uptime(1)` 命令

每个类 Unix 系统都自带一个叫 `uptime` 的小程序。它读
`/proc/uptime`,输出三件事:

- 系统已运行时长(`dd:hh:mm` 形式),
- 当前登录用户数,
- 过去 1、5、15 分钟的负载平均值。

```sh
$ uptime
22:14:03 up 47 days,  3:12,  4 users,  load average: 0.12, 0.18, 0.21
```

手册页
[`man.x-cmd.com/man1/uptime`](https://man.x-cmd.com/man1/uptime)
是规范参考。`uptime`、`w`、`top` 第一行的输出完全相同 —— 它们读的是
同一份内核状态。

### `x uptime` —— x-cmd 增强版

[`x uptime`](https://x-cmd.com/mod/uptime) 是 x-cmd 的封装。它增加了
格式化选项、可供管道消费的 JSON 输出,以及(未来)从本仓目录叠加 provider
状态的能力。

```sh
# 同 `uptime(1)`:
x uptime

# 机器可读:
x uptime --json

# 美化 / 上色:
x uptime --pretty
```

规划中的更深集成:`x uptime` 读取本仓的
[`data/index.tsv`](../../data/index.tsv),让你用一行命令问"OpenAI
现在活着吗?" —— 同一个问题,即将上线的 `x-cmd.com/uptime` 实时面板
会在浏览器里给出答案。

## 2. Provider 状态页目录

### 本仓内容

本仓在 [`data/index.yml`](../../data/index.yml) 下维护一份人工策展的
provider 状态页目录,分为三大类:

| 分类 | 范围 |
|---|---|
| `cloud` | 云厂商(Aliyun、AWS、GCP、Azure、Cloudflare 等) |
| `ai` | AI 模型服务(OpenAI、Anthropic、Gemini、DeepSeek、Qwen) |
| `other` | 相邻工具(GitHub、GitLab、Vercel、Stripe 等) |

扁平化、自动生成的形式是
[`data/index.tsv`](../../data/index.tsv) —— 一行一个 provider,
七列。schema 见
[`SKILL.md`](../../SKILL.md)。

### 为什么要做策展

当你依赖的东西坏了,你想要的是"一个直接打开的 URL",而不是去猜哪
个厂商子域名托管了他们的状态页。本仓把"去哪查?"这件事集中起来:

```sh
# 目录里追踪了哪些 provider?
curl -fsSL https://raw.githubusercontent.com/x-cmd/uptime/main/data/index.tsv \
  | awk -F'\t' 'NR > 1 { print $1 }'

# 在哪里查 OpenAI 的状态?
curl -fsSL https://raw.githubusercontent.com/x-cmd/uptime/main/data/index.tsv \
  | awk -F'\t' '$1 == "openai" { print $4 }'
# → https://status.openai.com
```

`api_url` 列是未来 GitHub Action 每 10 分钟拉一次的实时状态接口
(绿/黄/红)。该 pipeline 的首个版本是本仓的下一阶段。

### 即将上线的实时面板 x-cmd.com/uptime

上面的静态目录是**第一视图**。**第二视图**(目前在建设中)是位于
[`x-cmd.com/uptime`](https://x-cmd.com/uptime) 的实时面板 —— 展示
目录中每个 provider 的红/黄/绿指示灯,带搜索、卡片布局、以及赞助
provider 的预留位。面板会读取 `status-live.json`(同样由本仓未来
的 GitHub Action 产出),在客户端渲染。

如果你是 provider 维护方、希望加入,直接 PR 把条目加进
`data/index.yml` —— 见
[`CONTRIBUTING.md`](../../CONTRIBUTING.md)。

## 3. 监控你自己的网站

对自家服务来说,问题反过来:不是去查别人,而是希望**有人来 ping 你**,
在**你**宕机时吼一声。选项分三类。

### 自托管:自己跑一台服务器

| 工具 | 技术栈 | 备注 |
|---|---|---|
| [**Uptime Kuma**](https://github.com/louislam/uptime-kuma) | Node.js + SQLite | 现代化的默认选择。UI 漂亮、Docker 镜像、顺带出状态页。GitHub ~50k stars,非常活跃。 |
| [**Beszel**](https://github.com/henrygd/beszel) | Go + SQLite | 轻量,除了 HTTP 检查还顺带监控服务器资源(CPU、内存、磁盘)。 |
| **statping / statping-ng** | Go | 最早的"自托管状态页"。维护断断续续;建议改用 uptime-kuma。 |
| **Prometheus + blackbox_exporter** | Go | "重型"方案。已经在跑 Prometheus 时才考虑。 |

对大多数中小型站点,**Uptime Kuma** 就是正确答案:`docker run` 一行,
另一头出来一个状态页,Telegram / Slack / 邮件 / Discord 告警都
在同一 UI 里。

### Cron 风格:心跳不到就通知

当你关心的是"我的 cron 任务真的跑了吗?"而不是"我的 HTTP 接口
有响应吗?",有另一类工具更合用:

- [**Healthchecks.io**](https://healthchecks.io/) —— 开源项目免费;
  任务开始、结束、失败时各 ping 一次。ping 没到就告警。
- [**Cronitor**](https://cronitor.io/) —— 同思路,更偏企业。
- **Dead Man's Snitch** —— 这个领域的初代商业产品;已被 Sentry 收购。

故障模式是"任务根本没跑"而不是"服务器宕机"时,这些是正确答案。

### 托管:花钱让别人帮你盯

不想自己跑任何东西:

- [**UptimeRobot**](https://uptimerobot.com/) —— 免费版 5 分钟一次,
  最多 50 个监控。
- [**Better Stack**](https://betterstack.com/uptime) —— 现代托管
  替代品,自带 status-page-as-a-product。
- [**Better Uptime**](https://betteruptime.com/) —— on-call +
  状态页打包。

托管监控有一个自托管监控没有的缺点:当你**和托管监控厂商**的账户
出了问题(或欠费宽限期过了),你的监控也停了。纵深防御的做法是把
托管监控和下面的 GitHub Actions cron 配对 —— 两套独立系统。

## 4. 通过 GitHub Actions 监控

GitHub Actions cron 不是真正监控的替代品,但它是一层有用的**第二防线**:
独立于你的托管服务商,独立于你的 DNS,在 Actions 分钟配额内免费。

### 最小化:每 5 分钟 ping 一次 URL

```yaml
# .github/workflows/uptime-ping.yml
name: uptime-ping
on:
  schedule:
    # 每 5 分钟。GitHub cron 是 UTC,前置一个非整点分钟以避开全网扎堆。
    - cron: '7,12,17,22,27,32,37,42,47,52,57 * * * *'
  workflow_dispatch:

jobs:
  ping:
    runs-on: ubuntu-latest
    timeout-minutes: 2
    steps:
      - name: Probe target
        run: |
          status=$(curl -fsSL -o /dev/null -w '%{http_code}' \
                    --max-time 10 \
                    https://example.com/healthz)
          if [ "$status" != "200" ]; then
            echo "::error::target returned $status"
            exit 1
          fi
```

保存到任意仓库的 `.github/workflows/uptime-ping.yml`,它就会每 5 分钟
探一次目标 URL。探失败,run 失败,在 Actions 标签里一眼就能看见。

**注意:** GitHub 不保证 cron 触发的时间。
[官方文档](https://docs.github.com/actions/using-workflows/events-that-trigger-workflows#schedule)
明确写"最长间隔平均约 40 分钟,但有时会长达数小时"。真正 SLA 级的
监控请用专门的监控服务。"我想有个便宜的第二意见",GitHub Actions
cron 够用。

### 进阶:失败时开 GitHub Issue

2026 年邮件已经不够可靠。Issue 跟踪能活下来。

```yaml
# .github/workflows/uptime-alert.yml
name: uptime-alert
on:
  schedule:
    - cron: '*/5 * * * *'

jobs:
  alert:
    runs-on: ubuntu-latest
    timeout-minutes: 2
    steps:
      - name: Probe
        id: probe
        run: |
          code=$(curl -fsSL -o /dev/null -w '%{http_code}' \
                  --max-time 10 https://example.com/healthz || echo 000)
          echo "code=$code" >> "$GITHUB_OUTPUT"
      - name: Open issue if down
        if: steps.probe.outputs.code != '200'
        uses: actions/github-script@v7
        with:
          script: |
            await github.rest.issues.create({
              owner: context.repo.owner,
              repo: context.repo.repo,
              title: `Target returned ${process.env.CODE}`,
              body: 'The uptime cron detected a non-200 response. ' +
                    'Inspect the run, then close this issue when fixed.',
              labels: ['uptime', 'incident']
            });
        env:
          CODE: ${{ steps.probe.outputs.code }}
```

每次故障产生一个 Issue,把它 pin 到仓库,打上 `incident` 标签,团队的
通知流程就能接住。

### 更进一步:用公开接口做状态徽章

想做公开徽章("99.9% uptime"),需要历史状态。不跑服务器就能做到的最
便宜办法:

- 用 GitHub workflow 把一行结果 push 到仓库里的 CSV(每次探测提交一次,
  配一个每天 squash 一次的 workflow 降噪)。
- 或者用第三方,比如
  [atlassian-statuspage](https://www.statuspage.io),它本身通过 webhook
  消费探测输出。

个人站点够用。有付费客户的产品,从 §3 那张表里选一个方案更合适。

## 相关资源

- [`data/index.tsv`](../../data/index.tsv) —— 策展目录。
- [`data/index.yml`](../../data/index.yml) —— YAML 源。
- [`SKILL.md`](../../SKILL.md) —— schema + 常见 agent 查询。
- [`CONTRIBUTING.md`](../../CONTRIBUTING.md) —— 添加 provider 或文章。
- [Uptime Kuma](https://github.com/louislam/uptime-kuma) —— 自托管
  监控的默认选择。
- [GitHub Actions: scheduled events](https://docs.github.com/actions/using-workflows/events-that-trigger-workflows#schedule)
  —— 时间相关注意事项。

## 许可

本文是 `x-cmd/uptime` 仓库的一部分,采用 Apache License 2.0 许可。
