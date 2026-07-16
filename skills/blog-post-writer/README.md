# Blog Post Writer

> 从一个目标关键词出发，研究实时 SERP，并经过大纲与终稿审批，产出可发布的 SEO/GEO 文章及可审计内容包。

> Turn one target keyword into a researched, approval-gated, publish-ready SEO/GEO article and an auditable content package.

## 中文说明

### 核心能力

- 调研当前 SERP、排名页面、People Also Ask、相关搜索及适用的社区讨论。
- 判断搜索意图、文章类型、合理深度及信息增益机会。
- 支持解释型文章、How-to、Listicle、Roundup、单品评测、对比及 Alternatives 内容。
- 先生成带来源映射的大纲，经用户确认后再写完整文章。
- 校验重要事实、引用、内部链接、媒体计划、SEO 元数据及适用的 JSON-LD。
- 支持从零写作，也支持基于现有文章进行有研究依据的更新。

### 何时使用

适合需要完整博客文章、内容 Brief 与大纲、旧文章更新，或希望提升内容的 SEO、GEO、可信度与信息增益时使用。

### 输入

**必填**

- `primary_keyword`：目标关键词。

**选填**

- 目标语言、国家/地区、受众和漏斗阶段。
- 网站、页面 URL、已有草稿、品牌、产品、价值主张、证明材料和 CTA。
- 文章类型、参考长度、格式、语气、作者与截止时间。
- 次关键词、实体、问题、内部链接、竞品。
- 可核验的一方经验、测试、数据、专家意见、示例、截图或媒体。
- 输出目录，或指定仅在聊天中交付。

### 安装与调用

克隆仓库：

```bash
git clone https://github.com/SpanChenGithub/seo-geo-skills.git
cd seo-geo-skills
```

将 `skills/blog-post-writer` 整个目录复制到对应位置：

| 客户端 | 安装位置 | 调用方式 |
| --- | --- | --- |
| Codex | `~/.codex/skills/blog-post-writer/` | `$blog-post-writer` |
| Claude Code | 项目中的 `.claude/skills/blog-post-writer/` | `/blog-post-writer` |
| Cursor | 项目中的 `.cursor/skills/blog-post-writer/` | `/blog-post-writer` |

示例：

```text
$blog-post-writer 目标关键词：how to remove background noise from audio。受众是播客新手，请先给我大纲。
```

```text
/blog-post-writer Refresh this article for the keyword "AI video editing workflow": https://example.com/article
```

### 输出

默认会先提交研究驱动的大纲并等待批准，再提交文章并等待最终批准。文件模式会生成包含以下内容的文章包：研究记录、来源、已批准大纲、草稿、最终 Markdown 文章、唯一一组元数据、媒体计划、质量报告和适用的结构化数据。也可以按要求仅在聊天中交付。

### 依赖、联网与凭证安全

- 正式大纲和文章必须建立在本次任务的实时 SERP 研究上，需要宿主提供已授权的搜索、浏览器或 URL 读取能力。
- 文件包校验需要 Python 3；`query-fan-out-analysis` 和 `seo-title-and-description` 是可选配套 Skill。
- 此 Skill 不强制要求第三方 API。任何可能产生费用的 API 调用都必须先说明计划并获得授权。
- API 凭证只能通过宿主的安全连接或环境变量读取。不要在聊天、命令参数、文章包或仓库中粘贴、保存或提交密钥。

### 限制

- 无法取得实时 SERP 时不会正式生成大纲或文章；需由用户提供带查询、日期、排名、标题和 URL 的新鲜 SERP 截图或导出。
- 不会虚构测试、体验、数据、引语、专家、客户或产品事实。
- 不保证排名、摘要展示或 AI 引用。
- 最终批准不等于发布授权；除非用户另外明确要求，否则不会修改网站、上传或发布内容。

## English Guide

### Core capabilities

- Research the current SERP, ranking pages, People Also Ask, related searches, and relevant community discussions.
- Determine search intent, article format, useful depth, and information-gain opportunities.
- Support explainers, how-tos, listicles, roundups, single-product reviews, comparisons, and alternatives articles.
- Produce a source-mapped outline first and draft only after explicit outline approval.
- Verify material claims, citations, internal links, media plans, SEO metadata, and eligible JSON-LD.
- Create a new article or perform a researched refresh of an existing one.

### When to use

Use it for a complete blog post, a content brief and outline, a researched article refresh, or content that needs stronger SEO, GEO, evidence, and original editorial value.

### Inputs

**Required:** `primary_keyword`.

**Optional:** language, country or region, audience, funnel stage, site or page URL, existing draft, brand and product context, value proposition, evidence, CTA, article type, reference length, format, tone, author, deadline, secondary keywords, entities, questions, internal links, competitors, first-party experience, tests, data, expert input, examples, screenshots, media, and output location.

### Installation and invocation

Clone the repository, then copy the complete `skills/blog-post-writer` directory to the location shown above. Invoke it with `$blog-post-writer` in Codex or `/blog-post-writer` in Claude Code and Cursor.

Example:

```text
$blog-post-writer Write a researched how-to for the keyword "reduce podcast background noise". Audience: beginners.
```

### Output

The normal workflow delivers a researched outline for approval, then a complete article for final approval. File mode produces an auditable package containing research, sources, the approved outline, draft, canonical Markdown article, one metadata set, media plan, quality report, and eligible structured data. Chat-only delivery is also supported.

### Dependencies, network access, and credential safety

Current SERP access through an authorized host search or browser capability is mandatory for formal generation. Python 3 is used to validate file packages. Companion skills are optional. Never paste or commit credentials; use secure host connections or environment variables, and authorize paid API calls before execution.

### Limitations

The Skill stops formal generation when fresh SERP evidence is unavailable, never fabricates experience or claims, does not guarantee rankings or AI citations, and does not publish or modify a website without a separate explicit request.

Author: Span · License: MIT
