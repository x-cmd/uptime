---
x-title: x-cmd/uptime 目录 —— schema、查询与贡献
x-desc: 深入 data/index.yml(策展源)与 data/index.tsv(生成的扁平目录)。Schema 参考、awk 查询大全、api_type 分类法、region 过滤,以及贡献流程。
x-sidebar: 目录
x-keywords: data index yml, data index tsv, schema, awk 查询, atlassian statuspage, statuspal, region 过滤, 贡献
x-json-ld:
  '@context': https://schema.org
  '@graph':
    - '@type': TechArticle
      headline: 'x-cmd/uptime 目录 —— schema、查询与贡献'
      inLanguage: 'cn'
      about: 'x-cmd/uptime 的数据目录'
---

# `x-cmd/uptime` 目录

> **本文内容。** 第一篇文章
> ([`1-uptime-content`](../1-uptime-content/cn.md))
> 给出了整体视图。本文深入目录本身 —— 每个字段、每种查询模式、每个
> 贡献开关。

目录是本仓库的**第一视图**。它是一个小型 YAML 文件
[`data/index.yml`](../../data/index.yml),加上一个从中生成的扁平 TSV
[`data/index.tsv`](../../data/index.tsv)。TSV 是未来的 `x uptime`
shell 命令和位于 [`x-cmd.com/uptime`](https://x-cmd.com/uptime) 的
实时面板要消费的对象。

## 1. `data/index.yml` —— 策展源

YAML 按分类组织。目前有三个分类(`cloud`、`ai`、`other`);加第四个
是一行代码的事。每条条目是一个扁平映射。

```yaml
cloud:
  - name: aliyun
    homepage: https://www.aliyun.com
    statuspage: https://status.aliyun.com
    api_type: custom-json
    api_url: https://status.aliyun.com/api/v1/status
    region: cn
```

### 字段参考

| 字段 | 必填 | 类型 | 含义 |
|---|---|---|---|
| `name` | 是 | str | 小写 slug,作为该行的主键。稳定 —— 改名要在 PR 里提前说。 |
| `homepage` | 是 | url | 厂商官网(不是状态页)。 |
| `statuspage` | 是 | url | 厂商的状态页(人读)。用户在浏览器里打开的 URL。 |
| `api_type` | 是 | enum | `atlassian-statuspage` / `custom-json` / `statuspal` / `rss` 之一。详见 §3。 |
| `api_url` | 是 | url | 机器可读的状态接口。`atlassian-statuspage` 约定为 `<statuspage-host>/api/v2/summary.json`。 |
| `region` | 否 | str | 大陆厂商填 `cn`,其他填 `global`。即将上线的实时面板按这个过滤。允许留空(给跨区域的厂商)。 |

CI 拒绝分类内重复 —— `(category, name)` 在文件中必须唯一。CI 也拒
绝缺必填字段的条目,错误信息会指出文件和字段。

## 2. `data/index.tsv` —— 生成的扁平形式

TSV 是一个 7 列文件,每次 push 触及 `data/index.yml` 或构建脚本时
重新生成。整个流水线在
[`.github/workflows/index-tsv.yml`](../../.github/workflows/index-tsv.yml)。

```
name    category    homepage    statuspage    api_type    api_url    region
aliyun  cloud       https://www.aliyun.com    https://status.aliyun.com    custom-json    https://status.aliyun.com/api/v1/status    cn
aws     cloud       https://aws.amazon.com    https://health.aws.amazon.com    custom-json    https://health.aws.amazon.com/public/currentevent    global
openai  ai          https://openai.com    https://status.openai.com    atlassian-statuspage    https://status.openai.com/api/v2/summary.json    global
```

**请编辑 `index.yml`。** 对 `index.tsv` 的手改会在下次 push 时被静默
覆盖。CI 的 `--check` 也会让任何带过期 `index.tsv` 的 PR 失败。

### 为什么要单独一个 TSV

YAML 是给人类看的;TSV 是给 `awk`、`grep`、`sort` 和 shell 管道用的。
一个扁平、排序过的制表符分隔文件,既支持人类查看,也支持机器处理,
还不用在每次 shell 调用时解析 YAML —— 这是最简单的形式。

## 3. `api_type` 分类法

四个值,每个都有严格含义:

| `api_type` | 使用场景 | URL 形态 |
|---|---|---|
| `atlassian-statuspage` | 状态页托管在 Atlassian Statuspage(statuspage.io 背后的产品)。多数主流 SaaS。 | `<host>/api/v2/summary.json` 返回 JSON,含 `status.indicator`(`none` / `minor` / `major` / `critical`)和 `status.description`。 |
| `custom-json` | 厂商有自定义 JSON 接口,不符合 Atlassian 格式。AWS、GCP、Aliyun 属此类。 | 形态各异;实时面板会用每厂商 parser 归一化。 |
| `statuspal` | 厂商在 [Statuspal](https://statuspal.com)。 | `<host>/api/v1/status`(JSON)。 |
| `rss` | 厂商只发布 Atom/RSS feed,没有 JSON。少见。 | 实时面板需要 feed parser。 |

如果你发现一个厂商的接口不符合其中任何一项,请加新的 `api_type`
值并在 PR 里说明需要的归一化逻辑 —— 实时面板的 parser 表就是要随
此增长的契约。

## 4. 常用 `awk` 查询

TSV 有 header 行;用 `NR > 1` 跳过。

```sh
BASE='https://raw.githubusercontent.com/x-cmd/uptime/main/data/index.tsv'

# 所有 provider,只看 name + status URL
curl -fsSL "$BASE" | awk -F'\t' 'NR > 1 { print $1, $4 }'

# 在哪里查 OpenAI 的状态?
curl -fsSL "$BASE" | awk -F'\t' '$1 == "openai" { print $4 }'

# 所有 cn 区域的云厂商
curl -fsSL "$BASE" | awk -F'\t' '$2 == "cloud" && $7 == "cn"'

# 所有走 atlassian-statuspage 接口的 provider
curl -fsSL "$BASE" | awk -F'\t' '$5 == "atlassian-statuspage" { print $1, $6 }'

# 每个分类的 provider 数量
curl -fsSL "$BASE" | awk -F'\t' 'NR > 1 { print $2 }' \
  | sort | uniq -c | sort -rn

# 哪些厂商用同一种 API 形态?(按 api_type 分组)
curl -fsSL "$BASE" | awk -F'\t' 'NR > 1 { print $5 }' \
  | sort | uniq -c | sort -rn
```

这些 recipe 都能在拉到的原文件上直接跑;无需解析、无需 Python、无
需 jq。想要 JSON 形式,未来的 `x uptime` shell 命令会从同一个 TSV
产出。

## 5. region 过滤

今天两个 region:`cn` 和 `global`。设计意图:

- `x-cmd.com/uptime` 的实时面板会暴露一个 region 开关。`cn` 显示大陆
  厂商(GFW 外可能慢或被墙);`global` 显示其他。一些厂商(比如 Aliyun
  的海外业务,既有 global 又有 cn 状态面)标 `global`。
- 如果一个厂商每个 region 各有一个状态页,条目应该挑一个规范面(推荐),
  或者在不同 name 下挂多条 —— 但后者目前会被唯一性检查拒掉。

现在就拿 `cn` 切片:

```sh
curl -fsSL "$BASE" | awk -F'\t' 'NR > 1 && $7 == "cn" { print $1, $4 }'
```

## 6. 贡献一个新 provider

开一个**只动 `data/index.yml`** 的 PR。CI 处理剩下的事。完整规则在
[`CONTRIBUTING.md`](../../CONTRIBUTING.md),简版如下:

1. 在对应分类下追加一条。
2. 所有必填字段齐全;`api_type` 是正确的 enum 值。
3. `statuspage` URL 必须能解析(这里打错会让实时面板该 provider 永久
   不可用)。
4. `api_url` 必须存在(实时面板会探测它;首次 404 会让该 provider 在
   第一个周期就亮红并一直红)。

PR 模板(请附):

```
- provider: <name>
- category: <cloud | ai | other>
- api_type: <enum>
- statuspage: <URL —— 已在浏览器打开过验证>
- api_url: <URL —— 已在 curl 上 2xx 验证>
```

如果发现某厂商的 `api_url` 自上次策展后变了,一行 fix —— 同一流程。

## 7. 目录如何喂实时面板

今天的流程:

1. PR 改 `data/index.yml`。
2. CI 校验 schema、重新生成 `data/index.tsv`、提交。

下一阶段的计划:

1. 另一个 GitHub Action 读 `data/index.tsv`,对每个 `api_url` 扇出探测,
   把响应归一化成 `{status, fetched_at, indicator}`,写入 `status-live.json`。
2. `x-cmd.com/uptime` 的实时面板读 `status-live.json`,和 `data/index.tsv`
   做 join 拿人读字段,然后按 provider 渲染红/黄/绿。

`status-live.json` 计划发布到 `gh-pages` 分支(暂定),这样面板无需
鉴权就能拉。契约确定后再写本文此处。

## 相关资源

- [`data/index.yml`](../../data/index.yml) —— 策展源。
- [`data/index.tsv`](../../data/index.tsv) —— 生成的 TSV。
- [`.x-cmd/build-index-tsv.py`](../../.x-cmd/build-index-tsv.py) —— 生成器。
- [`.github/workflows/index-tsv.yml`](../../.github/workflows/index-tsv.yml) —— CI。
- [`CONTRIBUTING.md`](../../CONTRIBUTING.md) —— 添加 provider。
- [`SKILL.md`](../../SKILL.md) —— TSV schema 参考。

## 许可

本文是 `x-cmd/uptime` 仓库的一部分,采用 Apache License 2.0 许可。
