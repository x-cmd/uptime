# x-cmd/uptime

<!-- uptime-catalog-as-of:START -->
**目录截至:2026-10-06** _(3 大类共 16 个 provider:cloud、ai、other)_
<!-- uptime-catalog-as-of:END -->

> 🌐 **English: [README.md](./README.md)** —— same catalog, English front matter.

>
> - **[16 个 provider](#16-个-provider)** —— 目录目前覆盖哪些,按分类。
> - **[API 形态](#api-形态)** —— 每种 `api_type` 各有多少家。
> - **[区域覆盖](#区域覆盖)** —— `cn` 与 `global` 分布。
> - **[Reports](#reports)** —— 上表的源 TSV。
> - **[关于 x-cmd/uptime](#关于-xcmduptime)** —— 本仓是生产者。
> - **[FAQ](#faq)** —— 常见问题。
>
> 给终端用户:[`SKILL.md`](./SKILL.md)(原始 TSV recipe)。给开发者:[`CONTRIBUTING.md`](./CONTRIBUTING.md)(目录 schema + 4 元组文章约定)。

## 16 个 provider

> 下表由 [`data/index.yml`](./data/index.yml) 派生,每次 push 由
> [`.github/workflows/index-tsv.yml`](./.github/workflows/index-tsv.yml)
> 重新生成 [`data/index.tsv`](./data/index.tsv)。
> 机器可读形式见 `data/index.tsv`;人读快照见下。

<!-- BEGIN data/catalog.snapshot.md -->

_(Phase A:静态快照。后续阶段会由 CI 脚本从 `data/index.tsv` 自动再生此块。)_

### 云服务 (7)

| Provider | 状态页 |
| --- | --- |
| aliyun | https://status.aliyun.com |
| aws | https://health.aws.amazon.com |
| azure | https://status.azure.com |
| cloudflare | https://www.cloudflarestatus.com |
| gcp | https://status.cloud.google.com |
| huawei-cloud | https://status.huaweicloud.com |
| tencent-cloud | https://status.cloud.tencent.com |

### AI 服务 (5)

| Provider | 状态页 |
| --- | --- |
| anthropic | https://status.anthropic.com |
| deepseek | https://status.deepseek.com |
| gemini | https://status.gemini.google.com |
| openai | https://status.openai.com |
| qwen | https://status.alibabacloud.com |

### 其他 (4)

| Provider | 状态页 |
| --- | --- |
| github | https://www.githubstatus.com |
| gitlab | https://status.gitlab.com |
| stripe | https://status.stripe.com |
| vercel | https://www.vercel-status.com |

<!-- END data/catalog.snapshot.md -->

## API 形态

> 每个 provider 走四种 `api_type` 之一 —— 这是未来 live-status
> pipeline 要解析的形态。下表从 `data/index.tsv` 重新生成。

<!-- BEGIN data/api-type.snapshot.md -->

| `api_type` | 数量 | 例子 |
| --- | ---: | --- |
| `atlassian-statuspage` | 11 | github, gitlab, stripe, vercel, openai, anthropic, gemini, cloudflare, azure, tencent-cloud |
| `custom-json` | 5 | aliyun, aws, gcp, huawei-cloud, deepseek, qwen |
| `statuspal` | 0 | _(暂无)_ |
| `rss` | 0 | _(暂无)_ |

<!-- END data/api-type.snapshot.md -->

每种 `api_type` 的解析示例见
[`docs/2-the-catalog/2-the-catalog.cn.md`](./docs/2-the-catalog/2-the-catalog.cn.md#3-api_type-分类法)。

## 区域覆盖

<!-- BEGIN data/region.snapshot.md -->

| 区域 | 数量 |
| --- | ---: |
| `global` | 10 |
| `cn` | 6 |

<!-- END data/region.snapshot.md -->

`x-cmd.com/uptime` 未来的实时面板会暴露 region 开关按此列过滤。
每个 region 各有独立状态页的厂商应选一个规范面。

## Reports

目录以两种形式存在,均提交进仓库:

| 文件 | 格式 | 用途 |
| --- | --- | --- |
| [`data/index.yml`](./data/index.yml) | YAML(人工策展) | 唯一源 —— 编辑它来添加 provider。 |
| [`data/index.tsv`](./data/index.tsv) | TSV(CI 生成) | 扁平形式,供 `awk` / `x uptime` shell 消费。 |

下一阶段计划(本仓暂无):

| 文件 | 格式 | 用途 |
| --- | --- | --- |
| `status-live.json` | JSON(CI 生成) | 每个 provider 的实时指示灯,由单独的 GitHub Action 每 10 分钟刷新。`x-cmd.com/uptime` 面板会读这个。 |

## 关于 x-cmd/uptime

本仓是即将上线的 [`x-cmd.com/uptime`](https://x-cmd.com/uptime)
状态页聚合站的**生产者**:

1. 持有 provider 状态页的人工策展目录([`data/index.yml`](./data/index.yml))。
2. CI 在每次 push 时重新生成 [`data/index.tsv`](./data/index.tsv)([`.github/workflows/index-tsv.yml`](./.github/workflows/index-tsv.yml))。
3. 另一个 GitHub Action(计划中)会每 10 分钟从每个 provider 的 `api_url`
   拉一次实时状态,产出 `status-live.json`。
4. 消费者是未来的 Web App `x-cmd.com/uptime` —— 红/黄/绿卡片、搜索、
   预留的赞助商位。
5. 配套的 shell 模块是 [`x uptime`](https://x-cmd.com/mod/uptime)。

### 用户获取 uptime 数据的 4 种方式

```sh
# 1. 浏览 —— 直接打开 README.md 或 x-cmd.com/uptime。

# 2. 拉 TSV 通过 HTTPS —— pipe 给 awk 过滤。
curl -fsSL https://raw.githubusercontent.com/x-cmd/uptime/main/data/index.tsv

# 3. 阅读 topic 文章 —— docs/ 下 7 篇,覆盖自托管 / 托管 / cron 风格 /
#    GitHub Actions 监控。

# 4. 用 shell 模块(计划中) —— `x uptime <provider>` 返回单个 provider
#    的实时状态;`x uptime ls` 列出全部。
```

无需 API key,无需鉴权,无需后台服务。目录 TSV 是纯文本 —— `awk -F'\t'`
直接可用。

## 开发者文档

- 添加 provider:[`CONTRIBUTING.md`](./CONTRIBUTING.md#1-add-a-provider)
- TSV schema + agent recipe:[`SKILL.md`](./SKILL.md)
- 文章工作流 + frontmatter 规范:[`CONTRIBUTING.md`](./CONTRIBUTING.md#2-write-an-article)
- 流水线脚本:[`.x-cmd/build-index-tsv.py`](./.x-cmd/build-index-tsv.py)

## 许可

Apache License 2.0 —— 见 [`LICENSE`](./LICENSE)。

## 姊妹仓库

- [`x-cmd/cve`](https://github.com/x-cmd/cve) —— topic library(规约参考)。
- [`x-cmd/seo`](https://github.com/x-cmd/seo) —— topic library(规约参考)。
- [`x-cmd/mneme/AGENTS.md`](https://github.com/x-cmd/mneme/blob/main/AGENTS.md) —— 公 org 地图 + topic-library 约定。
- 渲染站点:<https://x-cmd.com/uptime>
- 即将上线的 shell 模块:<https://x-cmd.com/mod/uptime>

## FAQ

### 这个仓库是什么?

`x-cmd/uptime` 是 `x-cmd.com/uptime` 的源仓库 —— 一个状态页聚合站,也是即将上线的 `x uptime` shell 模块的数据源。它持有 provider 状态页的人工策展目录(cloud / AI / other),`docs/` 下 uptime 和监控相关的 topic 文章,以及(计划中)由独立 GitHub Action 每 10 分钟刷新的实时状态 JSON。

### 实时状态面板已经上线了吗?

还没有。截至 Phase A,目录和 topic 文章已就位;`x-cmd.com/uptime` 的实时状态面板是下一阶段。改 `data/index.yml` 的 PR 会立刻触发 CI 重新生成 `data/index.tsv`。

### 怎么添加 provider?

编辑 [`data/index.yml`](./data/index.yml),在对应分类下追加一条含必填字段(`name`、`homepage`、`statuspage`、`api_type`、`api_url`)的条目,开 PR。CI 校验 schema、重新生成 `data/index.tsv`、自动提交。见 [`CONTRIBUTING.md`](./CONTRIBUTING.md)。

### 现在怎么查某个厂商的状态?

```sh
curl -fsSL https://raw.githubusercontent.com/x-cmd/uptime/main/data/index.tsv \
  | awk -F'\t' '$1 == "<name>" { print $4 }'
# 返回人读状态页 URL
```

`data/index.tsv` 的第 4 列是状态页 URL。第 6 列是机器可读的状态 JSON
接口,未来实时 pipeline 会探测。

### `atlassian-statuspage` / `custom-json` / `statuspal` / `rss` 有什么区别?

这是目录里的四种 `api_type` 值。`atlassian-statuspage` 最常见(Statuspage.io / Atlassian Statuspage)。`custom-json` 给有自定义接口的厂商。`statuspal` 是 [Statuspal](https://statuspal.com) 的形态。`rss` 是只发 feed 的厂商。见 [`docs/2-the-catalog`](./docs/2-the-catalog/2-the-catalog.cn.md#3-api_type-分类法)。

### `region` 是干嘛的?

把 provider 标成 `cn`(大陆)或 `global`(其他)。`x-cmd.com/uptime` 未来的实时面板会暴露 region 开关。允许留空给跨区域的厂商。

### topic 文章在哪?

[`docs/`](./docs) 下。第一篇 `1-uptime-content` 是概览;`2-the-catalog` 深入目录;`3-` 到 `6-` 分别讲自托管、托管、cron 风格、GitHub Actions 监控;`7-decision-guide` 是综合。每篇是 4 元组:`*.en.md`、`*.cn.md`、`*.llms.md`、`*.faq.yml`。
