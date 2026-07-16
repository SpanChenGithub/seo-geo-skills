# Content Planner

> 使用 Ahrefs MCP 为 SaaS、在线工具和内容站制定按国家拆分的全站 SEO/GEO 内容策略，并生成经过校验的 Excel 内容规划表。

> Build country-specific, whole-site SEO/GEO strategies and validated Excel content plans for SaaS, online tools, and content sites using Ahrefs MCP evidence.

## 中文说明

### 核心能力

- 使用 Ahrefs MCP 收集关键词、流量潜力、KD、CPC、搜索意图、Parent Topic、竞品和 SERP 证据。
- 为新网站或已有网站构建关键词库、Topic Cluster、Pillar/Cluster 结构和用户旅程。
- 将同一搜索意图的关键词聚合为一个规划页面，减少重复内容和关键词蚕食。
- 规划 TOFU、MOFU、BOFU、内容类型、已有页面处理方式、内部链接和发布顺序。
- 使用固定的 100 分规则计算 P1、P2、P3 优先级。
- 为每个国家生成独立、可审计且经过结构校验的 `.xlsx` 工作簿。

### 何时使用

适合规划新站或已有站的全站内容体系，包括关键词研究、内容差距、Topic Cluster、页面合并、内容漏斗、内部链接、优先级和内容路线图。

### 输入

**必填**

- 项目类型：`Existing site` 或 `New site`。
- 目标语言。
- 目标国家/市场。
- 网站主题或产品说明。
- 已有网站项目还必须提供网站 URL。

**选填**

- ICP、商业模式、转化目标。
- 种子关键词、竞品、排除主题或合规边界。
- 内容产能、偏好或不可用的内容类型。

### 安装与调用

克隆仓库：

```bash
git clone https://github.com/SpanChenGithub/seo-geo-skills.git
cd seo-geo-skills
```

将 `skills/content-planner` 整个目录复制到对应位置：

| 客户端 | 安装位置 | 调用方式 |
| --- | --- | --- |
| Codex | `~/.codex/skills/content-planner/` | `$content-planner` |
| Claude Code | 项目中的 `.claude/skills/content-planner/` | `/content-planner` |
| Cursor | 项目中的 `.cursor/skills/content-planner/` | `/content-planner` |

示例：

```text
$content-planner 新站，英语，美国市场。产品是一款面向播客创作者的在线音频清理工具。
```

```text
/content-planner Existing site: https://example.com. Language: Spanish. Market: Mexico. Build a whole-site content plan.
```

### 输出

每个国家生成一个独立运行目录，核心输出为 `content-plan.xlsx`。工作簿固定包含：

1. `Content Plan`
2. `Raw Keywords`
3. `Topic Map`
4. `Roadmap`
5. `Strategy Notes`
6. `Methodology`

同时保留不覆盖的 JSON 检查点、结构化内容计划和校验报告，便于暂停、恢复和审计。

### 依赖、联网与凭证安全

- 必须连接 Ahrefs MCP；关键词、排名、竞品、SERP 和指标只允许来自 Ahrefs MCP。
- Ahrefs MCP 通常需要符合条件的付费 Ahrefs 方案。优先使用 OAuth，也可以在本地环境安全配置 `AHREFS_MCP_KEY`。
- 生成与校验 Excel 需要 Python 3 和 `openpyxl`。缺少依赖时，Skill 会停止并提示用户自行安装，不会静默安装。
- 不要把凭证粘贴到聊天、命令、配置示例的真实值、检查点、工作簿或 Git 仓库中。`.local.env` 等本地凭证文件应保持在版本控制之外。

### 限制

- Ahrefs MCP 不可用、未授权或无法返回关键词数据时会停止，不能用普通网页搜索或模型记忆替代指标。
- 每次采集最多返回 100 个关键词行；每新增保存 100 行后会保存检查点并询问是否继续。
- 多个国家必须独立研究并分别生成工作簿，不能混合指标或优先级百分位。
- 不会声称覆盖所有可能关键词；只描述已批准且实际完成的 Ahrefs 研究边界。
- 不生成文章正文，不发布内容，也不修改网站。

## English Guide

### Core capabilities

- Collect keyword, demand, difficulty, CPC, intent, Parent Topic, competitor, and SERP evidence through Ahrefs MCP.
- Build keyword universes, topic clusters, pillar structures, funnels, internal-link directions, and publishing roadmaps.
- Consolidate same-intent terms into one planned indexable page and flag ambiguous clustering decisions.
- Map pages to TOFU, MOFU, BOFU, content type, existing-site action, and a deterministic P1/P2/P3 priority.
- Generate a separate, styled, validated `.xlsx` workbook for every country.

### When to use

Use it for whole-site planning, keyword discovery, content and competitor gaps, page consolidation, topic clusters, funnel balance, internal linking, priority scoring, and publishing sequence.

### Inputs

**Required:** project type, target language, target country or market, website theme or product description, and a website URL for an existing-site project.

**Optional:** ICP, business model, conversion goal, seed keywords, competitors, exclusions, content capacity, and content-type constraints.

### Installation and invocation

Clone the repository, then copy the complete `skills/content-planner` directory to the location shown above. Invoke it with `$content-planner` in Codex or `/content-planner` in Claude Code and Cursor.

Example:

```text
$content-planner New site. Language: English. Market: Canada. Product: an online subtitle editor for creators.
```

### Output

The primary deliverable is one validated Excel workbook per country, with `Content Plan`, `Raw Keywords`, `Topic Map`, `Roadmap`, `Strategy Notes`, and `Methodology` sheets. Versioned JSON, resumable checkpoints, and a validation report provide the audit trail.

### Dependencies, network access, and credential safety

Ahrefs MCP is mandatory and is the exclusive source for SEO metrics and SERP evidence. Use OAuth where possible or configure `AHREFS_MCP_KEY` locally without revealing its value. Python 3 and `openpyxl` are required for workbook generation and validation. Never commit credentials or local environment files.

### Limitations

The Skill cannot replace missing Ahrefs evidence with web search or model estimates, pauses after each 100 newly persisted keyword rows, separates every country into its own research run, does not claim absolute keyword exhaustiveness, and does not write articles or modify the target site.

Author: Span · License: MIT
