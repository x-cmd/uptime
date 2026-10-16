---
x-title: 用 GitHub Actions 当监控
x-desc: 一层独立的纵深防御,脱离你的托管服务商和 DNS。配方:最小 ping、失败开 Issue、CSV 行做徽章、Slack webhook。时序保证、分钟配额、安全。
x-sidebar: GitHub Actions 监控
x-keywords: github actions, cron, scheduled events, uptime 探测, slack webhook, 状态徽章, csv, 纵深防御
x-json-ld:
  '@context': https://schema.org
  '@graph':
    - '@type': TechArticle
      headline: '用 GitHub Actions 当监控'
      inLanguage: 'cn'
      about: '用 GitHub Actions cron 做 uptime 监控'
---

# 用 GitHub Actions 当监控

> **本文内容。** GitHub Actions cron **不是**专用监控的替代品。它
> 是有用的**第二层纵深防御**:独立于你的托管服务商、独立于你的 DNS、
> 在 Actions 分钟配额内免费。本文走完配方和注意事项。

第一篇文章
([`1-uptime-content`](../1-uptime-content/cn.md))
给出了两个最小配方。本文展开,覆盖实战细节:用可信的 cron 时序、
分钟配额、暴露 token 的安全、以及探测失败的四种升级模式。

## 1. 为什么 GitHub Actions 是有用的第二层

[`3-self-hosted-monitors`](../3-self-hosted-monitors/cn.md)
和 [`4-hosted-monitors`](../4-hosted-monitors/cn.md)
里每一个自托管和托管监控都有一个共同的单点故障:**监控和目标跑在
同一个网络里**。GitHub Actions cron 把这打破:

- 探测跑在 GitHub 的基础设施上,不是你的。
- 探测的 DNS 解析是 GitHub 的,不是你的。
- 探测从一个真实的外部 IP 看你的端点 —— 能抓到"localhost 上活着但
  公网到不了"这种 case。

代价:GitHub 不保证 cron 触发时间。
[官方文档](https://docs.github.com/actions/using-workflows/events-that-trigger-workflows#schedule)
写:

> 最长间隔平均约 40 分钟,但有时会长达数小时。

所以 GitHub Actions cron **不是** SLA 级需求的首要监控。它是搭配
Kuma / UptimeRobot / Better Stack 的**第二层**。

## 2. 配方:最小 ping

第一篇文章的配方,配上不和全网打架的 cron:

```yaml
# .github/workflows/uptime-ping.yml
name: uptime-ping
on:
  schedule:
    # 每 5 分钟。用偏移分钟(不要 0/30)避开整点的 Actions cron 扎堆。
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

注意:

- **`workflow_dispatch`** 让你在 Actions UI 里手动触发 workflow ——
  merge 前测一下很有用。
- **`timeout-minutes: 2`** 给整个 run 设上限;否则 curl 卡住会拖死
  整个 job。
- **`--max-time 10`** 给 curl 本身设上限。
- **带偏移分钟的 cron**(7、12、17、……)避开 GitHub Actions 在
  `:00` / `:30` 的"扎堆效应"。挑非整点分钟让你的 workflow 跑在全
  网前面。

### 实际可靠的 cron 表达式

| 频率 | Cron 表达式 | 触发节奏 |
|---|---|---|
| 每 5 分钟 | `*/5 * * * *` | 12 次/小时 —— 注意分钟配额 |
| 每 5 分钟,偏移 | `7,12,17,22,27,32,37,42,47,52,57 * * * *` | 12 次/小时,偏移 |
| 每 15 分钟 | `*/15 * * * *` | 4 次/小时 |
| 每小时 | `0 * * * *` | 1 次/小时 |
| 每天 03:00 UTC | `0 3 * * *` | 1 次/天 |

即便是"每 5 分钟偏移"也可能被 GitHub 调度器拖后。如果你的 SLA 能
接受 30 分钟检测窗口, **`*/15 * * * *`** 是甜蜜点:4 次/小时,远低于
分钟配额,最坏延迟也是文档化的。

## 3. 配方:失败时开 GitHub Issue

2026 年邮件已经不够可靠。Issue 跟踪能活下来:

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

每次故障产生一个新 issue,打上 `uptime` / `incident` 标签。pin 到仓
库,团队的 notification flow 就能接住。

### 避免告警风暴

凌晨 3 点失败的探测每 5 分钟开一个 issue,会把仓库刷屏。缓解模式:

- **先查有没有开着的 issue。** 用 `gh issue list --label uptime
  --state open`,有就跳过。
- **冷却步骤。** 在 workflow artifact 里记上次失败时间戳,只有 N
  小时过了才开新 issue。
- **按特征聚合。** 如果连续探测都是同一故障模式(比如都 504),只
  开一个 issue 然后加 comment。

## 4. 配方:追加 CSV 行(给状态徽章用)

对外的"99.9% uptime"徽章需要历史状态。最便宜的无服务器选项:

```yaml
# .github/workflows/uptime-csv.yml
name: uptime-csv
on:
  schedule:
    - cron: '*/5 * * * *'

jobs:
  record:
    runs-on: ubuntu-latest
    timeout-minutes: 2
    steps:
      - name: Probe
        id: probe
        run: |
          code=$(curl -fsSL -o /dev/null -w '%{http_code}' \
                  --max-time 10 https://example.com/healthz || echo 000)
          echo "code=$code" >> "$GITHUB_OUTPUT"
          echo "ts=$(date -u +%Y-%m-%dT%H:%M:%SZ)" >> "$GITHUB_OUTPUT"

      - name: Append to history
        run: |
          echo "${{ steps.probe.outputs.ts }},${{ steps.probe.outputs.code }}" \
            >> uptime-history.csv
      - name: Commit (squashed nightly)
        if: github.event_name == 'schedule' && startsWith(steps.probe.outputs.ts, format('{0}', github.event.repository.updated_at))
        run: |
          git config user.name "x-cmd-bot"
          git config user.email "bot@x-cmd.com"
          git add uptime-history.csv
          git diff --cached --quiet || git commit -m "uptime: append probe result"
          git push
```

这个 workflow 每次探测 push 一行。如果 5 分钟一次探测每天产生太多
commit(约 288 次/天),加一个**每天 squash 的 workflow**(`0 0 * * *`)
把行聚合成单次日 commit。徽章生成器两种格式都能读。

## 5. 配方:Slack / Discord webhook

团队本身就在 Slack 或 Discord 里:

```yaml
# .github/workflows/uptime-slack.yml
name: uptime-slack
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
      - name: Post to Slack
        if: steps.probe.outputs.code != '200'
        env:
          SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK_URL }}
        run: |
          curl -fsSL -X POST -H 'Content-Type: application/json' \
            --data "{\"text\":\":rotating_light: target returned ${{ steps.probe.outputs.code }}\"}" \
            "$SLACK_WEBHOOK_URL"
```

webhook URL 是 GitHub Actions secret —— 见 §7。Discord 同形,只是
payload 格式不同。

## 6. 配额:分钟上限

GitHub Actions 免费分钟,按仓库可见性:

| 可见性 | 免费分钟/月 |
|---|---|
| 公开 | 2,000 |
| 私有(免费档) | 500 |
| 私有(Team 档) | 3,000 |
| 私有(Enterprise 档) | 50,000 |

5 分钟一次探测每次大约烧 30 秒 runner 时间。按 `*/5 * * * *`(约
8,640 次/月)大概 70 小时/月,公开仓库的 2,000 分钟内完全放得下。
私有仓库会在一周内把 500 分钟的免费档烧光。改用 30 分钟间隔
(`*/30 * * * *`),或升级到 Team 档付费。

## 7. 暴露 token 的安全

如果探测要打私有端点(不是公开的 `/healthz`),三种模式:

- **公开副作用的状态检查。** `/healthz` 端点对任何调用者都返回
  200 —— 仅为监控。对需要鉴权的应用不理想。
- **HMAC 签名的探测。** 探测签一个已知 token;端点校验。token 存
  GitHub Actions secrets。看 workflow 文件的人能看到变量名,看不到
  secret 值。
- **IP 白名单。** GitHub 发布了一份
  [runner IP 列表](https://docs.github.com/actions/security-guides/security-harden-deployments/using-ip-allow-lists-with-github-hosted-runners)。
  配置端点只接受这些 IP 的探测。这是需要鉴权的内部服务最干净的模式。

三种情况下 secret 都放在 `Settings → Secrets and variables →
Actions`,**不要** 写在 workflow 文件里。用 `${{ secrets.NAME }}`
引用 —— 永远不要 echo 到日志。

## 8. GitHub Actions 什么时候是错的选择

- 你需要**亚分钟级 SLA 检测**。cron 时序太松。
- 你需要**多区域探测**。GitHub-hosted runner 在少数区域;要全覆盖
  就用托管监控或在多数据中心自托管。
- 你想要**状态页即产品**。Actions cron 能检测失败,但渲染不出打磨
  过的公开状态页 —— 那是 Uptime Kuma / Better Stack 的活儿。

这三种情况,把 GitHub Actions cron 当作主要监控旁边的第二层。

## 相关资源

- [`1-uptime-content`](../1-uptime-content/cn.md) —— 概览 + 首批配方
- [`3-self-hosted-monitors`](../3-self-hosted-monitors/cn.md) —— 主要监控选择
- [`4-hosted-monitors`](../4-hosted-monitors/cn.md) —— 托管主要监控
- [`7-decision-guide`](../7-decision-guide/cn.md) —— 按场景选择
- [GitHub Actions: scheduled events](https://docs.github.com/actions/using-workflows/events-that-trigger-workflows#schedule)
- [GitHub Actions: IP allowlists](https://docs.github.com/actions/security-guides/security-harden-deployments/using-ip-allow-lists-with-github-hosted-runners)
- [GitHub Actions: billing](https://docs.github.com/billing/managing-billing-for-github-actions/about-billing-for-github-actions)

## 许可

本文是 `x-cmd/uptime` 仓库的一部分,采用 Apache License 2.0 许可。
