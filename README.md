# SEO/GEO Skills

Reusable, evidence-first Agent Skills for SEO and GEO work in Codex, Claude Code, and Cursor.

面向 Codex、Claude Code 和 Cursor 的 SEO / GEO Agent Skills 合集。每个 Skill 都包含可审计的工作流程、清晰的输入与输出约束，并将事实证据与模型判断分开。

> These Skills assist research and production; they do not guarantee rankings, traffic, or AI citations.
>
> 这些 Skills 用于辅助研究与生产，不承诺搜索排名、流量或 AI 引用结果。

## Skills at a glance / Skill 总览

| Skill | Best for / 适用场景 | Main output / 主要输出 | Data requirement / 数据要求 |
| --- | --- | --- | --- |
| [`blog-post-writer`](skills/blog-post-writer/) | Researched SEO/GEO articles and content refreshes / SEO、GEO 文章及旧文更新 | Publish-ready article package / 可发布文章内容包 | Current SERP evidence required / 必须有当前 SERP 证据 |
| [`content-planner`](skills/content-planner/) | Whole-site content strategy by country / 按国家制定整站内容策略 | Validated `.xlsx` content plan / 经验证的 Excel 内容规划 | Ahrefs MCP required / 必须连接 Ahrefs MCP |
| [`query-fan-out-analysis`](skills/query-fan-out-analysis/) | Multi-provider fan-out and page-topic analysis / 多模型 Query Fan-out 与页面话题分析 | Provenance-labeled Markdown report / 带来源类型标记的 Markdown 报告 | APIs optional; simulation available / API 可选，可降级模拟 |
| [`seo-title-and-description`](skills/seo-title-and-description/) | SEO metadata generation, audit, and rewrite / SEO Title 与 Description 生成、审核、改写 | Five ranked metadata pairs / 5 组排序后的 Metadata | Current SERP evidence required / 必须有当前 SERP 证据 |
| [`tech-seo-audit`](skills/tech-seo-audit/) | Evidence-backed technical SEO audits / 基于真实证据的技术 SEO 审核 | Prioritized Markdown audit report / 按优先级排列的审核报告 | Accessible URL or supplied evidence / 可访问 URL 或用户证据 |
| [`tools-landing-page-generator`](skills/tools-landing-page-generator/) | Researched landing pages for online tools / 在线工具落地页调研与生成 | Validated static HTML package / 经验证的静态 HTML 内容包 | Keyword, official site, and current web evidence / 关键词、官网与当前网络证据 |

## Installation / 安装

Clone the repository first:

首先克隆仓库：

```bash
git clone https://github.com/SpanChenGithub/seo-geo-skills.git
cd seo-geo-skills
```

Copy the complete directory of the Skill you need into a supported Agent Skills directory. Common locations are:

将所需 Skill 的完整目录复制到宿主支持的 Agent Skills 目录。常见路径如下：

| Host / 宿主 | Project scope / 项目级 | User scope / 用户级 |
| --- | --- | --- |
| Codex | `.agents/skills/<skill-name>/` | `$CODEX_HOME/skills/<skill-name>/`, commonly `~/.codex/skills/<skill-name>/` |
| Claude Code | `.claude/skills/<skill-name>/` | `~/.claude/skills/<skill-name>/` |
| Cursor | `.cursor/skills/<skill-name>/` or `.agents/skills/<skill-name>/` | `~/.cursor/skills/<skill-name>/` or `~/.agents/skills/<skill-name>/` |

Example: install one Skill at project scope for Codex or Cursor:

示例：为 Codex 或 Cursor 安装一个项目级 Skill：

```bash
SKILL_NAME="query-fan-out-analysis"
TARGET_PROJECT="/path/to/your/project"

mkdir -p "$TARGET_PROJECT/.agents/skills"
cp -R "skills/$SKILL_NAME" "$TARGET_PROJECT/.agents/skills/"
```

For Claude Code, change the destination to `$TARGET_PROJECT/.claude/skills/`. Restart the agent session if the host does not discover a newly installed Skill automatically.

Claude Code 请将目标目录改为 `$TARGET_PROJECT/.claude/skills/`。如果宿主没有自动发现新安装的 Skill，请重新开启 Agent 会话。

## Invocation / 调用方法

You can ask the agent in natural language to use an installed Skill. Explicit invocation commonly uses `$skill-name` in Codex and `/skill-name` in Claude Code or Cursor when the host exposes installed Skills as slash commands.

可以直接用自然语言要求 Agent 使用已安装的 Skill。显式调用通常在 Codex 中使用 `$skill-name`；Claude Code 或 Cursor 在将已安装 Skills 暴露为 Slash Command 时使用 `/skill-name`。

```text
Use $seo-title-and-description.

Primary keyword: audio to text converter
Page URL: https://example.com/audio-to-text
```

```text
使用 /tech-seo-audit 审核以下页面：
https://example.com/product
```

## Skill guide / Skill 使用说明

### `blog-post-writer`

Researches the current search landscape, creates a source-mapped outline, writes the article after outline approval, and packages the final SEO/GEO assets after a second approval gate. It supports explainers, how-to guides, listicles, roundups, product reviews, comparisons, alternatives articles, and researched refreshes of existing posts.

调研当前搜索结果，生成带来源映射的大纲；大纲获批后再写正文，并在最终审批前整理完整 SEO / GEO 内容包。支持知识解释、How-to、Listicle、Roundup、产品评测、对比、Alternatives 文章及旧文更新。

**Use it for / 适用于**

- Creating a new article from a target keyword / 根据目标关键词创建新文章
- Refreshing an existing article with current evidence / 用当前证据更新旧文章
- Producing a researched outline before drafting / 正文写作前生成调研型大纲

**Inputs / 输入**

- Required / 必填：`primary_keyword`
- Optional / 选填：language, market, audience, site or draft, brand/product context, article type, tone, reference length, first-party evidence, internal links, CTA, and output location / 语言、市场、受众、网站或旧稿、品牌与产品背景、文章类型、语气、参考篇幅、第一手资料、内链、CTA 与输出位置

```text
Use $blog-post-writer to create a publish-ready article.

Primary keyword: best AI music video generator
Audience: independent musicians
```

The Skill first presents live SERP findings and the source-mapped outline, then pauses for approval. It never treats outline approval as permission to publish.

Skill 会先展示实时 SERP 结论与来源映射大纲，并暂停等待审批；大纲审批不等于发布授权。

**Output / 输出**

By default, it creates `articles/<keyword-slug>-<YYYY-MM-DD>/` with a brief, SERP research, source records, approved outline, draft, final `article.md`, one metadata set, media plan, quality report, and applicable structured data. Chat-only delivery is also supported.

默认生成 `articles/<keyword-slug>-<YYYY-MM-DD>/`，其中包含 Brief、SERP 调研、来源记录、已审批大纲、Draft、最终 `article.md`、一组 Metadata、媒体计划、质量报告与适用的结构化数据；也支持仅在对话中交付。

**Network / 联网要求**

Current SERP evidence is mandatory before the formal outline or article. If live search is unavailable, the Skill asks for a fresh ranked top-10 export, screenshots, or copied results with query context and date. Paid APIs and companion Skills are optional and require authorization unless the current request already grants it.

正式大纲和文章必须建立在当前 SERP 证据上。无法实时搜索时，Skill 会请求带查询背景和日期的最新前 10 名导出、截图或复制结果。付费 API 与配套 Skills 均为可选；除非当前请求已授权，否则调用前必须获得授权。

### `content-planner`

Builds a country-specific, whole-site SEO/GEO content strategy for a new or existing website. It clusters same-intent keywords into planned pages, maps funnel and content types, identifies existing-page actions, calculates priorities, and generates a validated Excel workbook.

为新网站或已有网站建立按国家独立的整站 SEO / GEO 内容策略。它会把相同搜索意图的关键词聚合为规划页面，映射 Funnel 与内容类型，判断已有页面应采取的 Action，计算优先级，并生成经验证的 Excel Workbook。

**Use it for / 适用于**

- Keyword universes, topic clusters, pillar pages, and content gaps / 关键词池、主题集群、Pillar Pages 与内容缺口
- TOFU, MOFU, BOFU planning and publishing roadmaps / TOFU、MOFU、BOFU 规划与发布路线图
- Existing-page update, consolidation, and internal-link decisions / 已有页面更新、合并及内链决策

**Inputs / 输入**

- Required / 必填：existing or new site, target language, target country/market, and website theme or product description / 已有站或新站、目标语言、目标国家或市场、网站主题或产品简介
- Additionally required for an existing site / 已有网站额外必填：website URL
- Optional / 选填：ICP, business model, conversion goal, seed keywords, competitors, exclusions, content capacity, and content-type constraints / ICP、商业模式、转化目标、种子关键词、竞品、排除主题、内容产能与内容类型限制

```text
Use $content-planner to create a whole-site content plan.

Project type: Existing site
Website: https://example.com
Website theme: AI music creation tools
Target country: United States
Target language: English
```

**Output / 输出**

Each country receives a separate non-overwriting run directory under `content-planner-output/`. The validated workbook contains these visible sheets in order: `Content Plan`, `Raw Keywords`, `Topic Map`, `Roadmap`, `Strategy Notes`, and `Methodology`. JSON checkpoints and validation artifacts remain beside the workbook.

每个国家都会在 `content-planner-output/` 下获得独立且不覆盖旧结果的运行目录。经验证的 Workbook 按顺序包含 `Content Plan`、`Raw Keywords`、`Topic Map`、`Roadmap`、`Strategy Notes` 与 `Methodology`；JSON Checkpoints 和验证文件保存在 Workbook 旁边。

**Network and dependencies / 联网与依赖**

- An authenticated Ahrefs MCP connection is mandatory. Ahrefs is the exclusive source of keyword, competitor, ranking, and SERP metrics / 必须连接并授权 Ahrefs MCP；关键词、竞品、排名和 SERP Metrics 只能来自 Ahrefs
- Authentication uses OAuth or the locally configured `AHREFS_MCP_KEY`; never paste its value into chat / 使用 OAuth 或本地配置的 `AHREFS_MCP_KEY` 授权，绝不要在对话中粘贴其值
- Ahrefs MCP requires an eligible paid Ahrefs plan and may consume API units / Ahrefs MCP 需要符合条件的付费方案，并可能消耗 API Units
- Collection pauses after every 100 newly persisted keyword rows and asks whether to continue / 每保存 100 条新关键词后暂停，并询问是否继续
- Workbook generation requires Python and `openpyxl`; missing dependencies are reported rather than installed silently / Workbook 生成需要 Python 与 `openpyxl`，依赖缺失时只提示，不会静默安装

See [`Ahrefs MCP setup`](skills/content-planner/references/ahrefs-mcp-setup.md) for Codex, Claude Code, and Cursor configuration.

Codex、Claude Code 与 Cursor 的配置方法见 [`Ahrefs MCP setup`](skills/content-planner/references/ahrefs-mcp-setup.md)。

### `query-fan-out-analysis`

Maps the likely search subqueries used to resolve a keyword or prompt across OpenAI/ChatGPT-style APIs, Gemini, a Google AI Mode simulation, Claude, and Perplexity. It separates exact queries exposed by structured API traces from provider-generated candidates and host-model heuristic simulations.

分析一个关键词或 Prompt 在 OpenAI/ChatGPT 风格 API、Gemini、Google AI Mode 模拟、Claude 与 Perplexity 中可能展开的搜索子查询。它会严格区分 API 结构化 Trace 实际暴露的 Query、Provider 生成的候选 Query 与宿主模型启发式模拟。

**Use it for / 适用于**

- Provider-specific fan-out queries and cross-model consensus / Provider 特定 Query 与跨模型共识
- Repeated-run stability and platform-specific angles / 多轮稳定度与平台差异
- Optional URL topic-gap analysis / 可选的 URL 话题缺口分析
- Prioritized topics a page should cover for SEO/GEO / 页面应覆盖的 SEO / GEO 优先话题

**Inputs / 输入**

- Required / 必填：`seed_input`, either a target keyword or a complete prompt / `seed_input`，可以是目标关键词或完整 Prompt
- Optional / 选填：language, locale, persona, business context, freshness, desired answer type, URL or pasted page, providers, model IDs, run count, query target, and execution mode / 语言、地区、Persona、业务背景、时效要求、答案类型、URL 或页面内容、Providers、Model IDs、运行轮次、Query 数量和执行模式

```text
Use $query-fan-out-analysis to analyze "best CRM for startups"
across all supported providers and recommend topics for the primary page.
```

```text
使用 /query-fan-out-analysis 分析“AI 音乐生成器”，并检查
https://example.com/ai-music-generator 对优先话题的覆盖情况。
```

**Output / 输出**

The default Markdown report contains method and assumptions, intent gaps, optional external signals, provider-specific clusters, recurrence, cross-model consensus, a coverage matrix, optional page coverage, limitations, and prioritized SEO/GEO page topics. Validated JSON or CSV is returned only when requested.

默认 Markdown 报告包含方法与假设、意图缺口、可选外部信号、Provider Clusters、重复稳定度、跨模型共识、覆盖矩阵、可选页面覆盖、限制及 SEO / GEO 页面优先话题。只有用户明确要求时才交付经验证的 JSON 或 CSV。

**Network and credentials / 联网与凭证**

The default mode is API-first hybrid: three runs per provider and 10–15 generated candidates per run. If a documented API route and its environment credential are available, the Skill shows a sanitized plan and executes the ordinary default scope. Missing or failed APIs fall back to clearly labeled heuristic simulation unless the user requested observed-only mode. Google AI Mode has no corresponding consumer API here and is always labeled as simulation.

默认采用 API-first Hybrid 模式：每个 Provider 运行 3 轮，每轮生成 10–15 个候选 Query。若存在受支持的 API Route 及环境凭证，Skill 会展示不含敏感信息的计划并执行普通默认范围；API 缺失或失败时会降级为明确标记的启发式模拟，除非用户要求 Observed-only。这里没有 Google AI Mode 的 Consumer API，因此相关结果始终标记为模拟。

Optional credentials are read only from these environment variables:

可选凭证仅从以下环境变量读取：

- `OPENAI_API_KEY`
- `GEMINI_API_KEY` or `GOOGLE_API_KEY`
- `ANTHROPIC_API_KEY`
- `PERPLEXITY_API_KEY`

Use simulated-only, offline, no-network, or no-paid-API mode when desired. A larger-than-default run plan requires explicit authorization.

需要时可指定 Simulated-only、Offline、No-network 或 No-paid-API 模式。超出默认规模的运行计划必须获得明确授权。

### `seo-title-and-description`

Researches, audits, rewrites, and generates SEO Title tags and Meta Descriptions for SaaS, online tools, content sites, and related page types. It reads supplied content, URLs, or source code for page truth but never edits the implementation.

为 SaaS、在线工具、内容站及相关页面调研、审核、改写和生成 SEO Title 与 Meta Description。它可以读取页面内容、URL 或源代码以确认页面事实，但不会修改实现代码。

**Use it for / 适用于**

- Creating metadata for a new page / 为新页面创建 Metadata
- Auditing and rewriting current metadata / 审核并改写已有 Metadata
- Processing a batch of up to 10 pages / 批量处理最多 10 个页面

**Inputs / 输入**

- Required / 必填：primary keyword and enough page evidence from pasted copy, a product brief, a URL, readable source code, or authorized web research / 主关键词，以及来自页面文案、产品简介、URL、可读取源代码或已授权网络调研的充分页面证据
- Conditionally required / 条件必填：page type when page and SERP evidence cannot infer it reliably / 页面与 SERP 无法可靠判断时需要提供页面类型
- Optional / 选填：country or region, output language, secondary keywords, brand, core benefits, audience, and existing Title/Meta Description / 国家或地区、输出语言、次关键词、品牌、核心卖点、受众及已有 Title/Meta Description

```text
Use $seo-title-and-description.

Primary keyword: audio to text converter
Page type: Online tool
Page brief: A browser-based tool that converts audio files into editable text.
```

**Output / 输出**

For each successful page, the Skill returns exactly five distinct Title and Meta Description pairs. Pair 1 is the strongest recommendation. Successful output intentionally omits character counts, audit notes, research rationale, sources, and internal reasoning.

每个成功处理的页面只返回 5 组不同的 Title 与 Meta Description，第一组为最推荐方案。成功结果不会展示字符数、审核记录、调研理由、来源或内部推理。

**Network / 联网要求**

Current SERP research is mandatory. The Skill inspects up to the top 10 organic results when available and analyzes Title vocabulary separately from snippet vocabulary. If live SERP access is unavailable or blocked, it pauses formal generation and asks for a SERP screenshot, export, or the top 10 titles, snippets, and URLs. It never bypasses CAPTCHA or scrapes Google with a custom script.

必须进行当前 SERP 调研。在结果可用时，Skill 会检查前 10 条自然搜索结果，并分别分析 Title 与 Snippet 的高频词汇。若实时 SERP 不可用或被阻止，则暂停正式生成，并请求 SERP 截图、导出文件，或前 10 条 Title、Snippet 与 URL。Skill 不会绕过 CAPTCHA，也不会使用自定义脚本抓取 Google。

### `tech-seo-audit`

Audits one accessible URL or a batch of up to 10 explicit URLs using observed browser, HTTP, rendered DOM, Lighthouse, and authorized connector evidence. It keeps the audit read-only and separates confirmed defects from unavailable checks.

使用浏览器、HTTP、渲染后 DOM、Lighthouse 与已授权连接器的真实证据，审核一个可访问 URL 或最多 10 个明确 URL 的批次。全流程保持只读，并区分已确认缺陷与无法验证的检查项。

**Use it for / 适用于**

- Crawlability and indexability reviews / 可抓取性与可索引性检查
- Metadata, headings, links, images, and structured data / Metadata、Headings、链接、图片与结构化数据
- Mobile and desktop performance checks / 移动端与桌面端性能检查
- Internationalization, security, and batch root-cause analysis / 国际化、安全及批量根因分析

**Inputs / 输入**

- Required / 必填：one `url`, or `urls` containing 2–10 explicit URLs / 一个 `url`，或包含 2–10 个明确 URL 的 `urls`
- Optional / 选填：target keyword, country or locale, expected page purpose or indexability, authenticated browser access already available, supplied HTML/headers/crawl exports/Search Console evidence/Lighthouse reports, and authorized GSC, Ahrefs, or Apify connections / 目标关键词、国家或地区、预期页面用途或索引状态、已有授权浏览器会话、HTML、Headers、Crawl Exports、Search Console 证据、Lighthouse 报告，以及已授权的 GSC、Ahrefs 或 Apify 连接

```text
Use $tech-seo-audit to audit:
https://example.com/product

Target keyword: example product
Expected state: indexable
```

**Output / 输出**

For one URL, the complete five-section Markdown report is returned in the conversation and saved without overwriting to `audits/tech-seo/<host>-<path-slug>-<YYYY-MM-DD>.md`. A batch creates one complete report per URL plus a cross-page summary. Reports include evidence coverage, a reproducible Skill score when sufficient evidence exists, separate mobile and desktop results, prioritized findings, fixes, and limitations.

单 URL 模式会在对话中返回完整五段式 Markdown 报告，并保存到 `audits/tech-seo/<host>-<path-slug>-<YYYY-MM-DD>.md`，不覆盖历史结果。批量模式为每个 URL 生成完整报告，并增加跨页面汇总。报告包含证据覆盖率、证据充分时可复算的 Skill Score、分别列出的移动端和桌面端结果、问题优先级、修复建议与限制。

**Network and credentials / 联网与凭证**

The Skill prefers a real browser with DevTools-equivalent evidence, then browser automation, then limited static HTTP inspection. GSC and Ahrefs are optional read-only evidence sources. Apify is used only as a controlled fallback or when explicitly requested; every possibly chargeable Apify run requires explicit authorization and a positive cost cap. Its token is read only from `APIFY_API_TOKEN` or a secure host connection.

Skill 优先使用具有 DevTools 等效证据的真实浏览器，其次是浏览器自动化，再其次是受限的静态 HTTP 检查。GSC 与 Ahrefs 仅作为可选只读证据源。Apify 只作为受控降级方案或在用户明确要求时使用；每次可能收费的 Apify Run 都必须获得明确授权，并设置正数费用上限。Token 仅从 `APIFY_API_TOKEN` 或安全的宿主连接中读取。

### `tools-landing-page-generator`

Researches a tool-style keyword, verifies product claims from official evidence, studies the current organic landscape and public discussion, extracts the target site's visual language, and creates a responsive static landing-page package with retained research, copy, SEO, design, and validation artifacts. The page includes an honest non-functional tool placeholder for later product integration.

调研工具型关键词并通过官网证据核实产品事实，分析当前自然搜索结果与公开讨论，提取目标网站的视觉语言，最终生成响应式静态落地页内容包，并保留调研、文案、SEO、设计与验证产物。页面中的工具区域是明确标注的非功能占位区，便于后续接入真实产品。

See the [complete bilingual user guide](skills/tools-landing-page-generator/README.md) for installation, prompt templates, pause points, output structure, validation, and troubleshooting.

安装、Prompt 模板、暂停节点、输出结构、验证方法与常见问题，请查看[完整双语用户指南](skills/tools-landing-page-generator/README.md)。

**Use it for / 适用于**

- Building a new SEO landing page for a generator, maker, checker, converter, calculator, analyzer, editor, or similar utility / 为 Generator、Maker、Checker、Converter、Calculator、Analyzer、Editor 等在线工具创建 SEO 落地页
- Replacing or improving an existing tool page through the same evidence-first workflow / 用相同的证据优先流程替换或改进已有工具页
- Producing an auditable package instead of only final-page copy / 生成可审计的完整内容包，而不只是最终页面文案

**Inputs / 输入**

- Required / 必填：one primary keyword and one official target website; provide the final page URL when it already exists / 一个主关键词与一个目标官网；已有最终页面 URL 时一并提供
- Optional / 选填：product knowledge base, positioning, target users, use cases, differentiators, limitations, market, language, canonical URL, and brand guidance / 产品知识库、定位、目标用户、场景、差异点、限制、市场、语言、Canonical URL 与品牌规范

```text
Use $tools-landing-page-generator.

Primary keyword: ai music video generator
Official website: https://example.org
Final page URL: https://example.org/ai-music-video-generator
Market and language: United States / English

Product context:
- Real input and output: <...>
- Actual workflow: <...>
- Verified features and official sources: <...>
- Primary CTA goal: <...>
```

**Output / 输出**

By default, the Skill creates a non-overwriting directory under `output/<keyword-slug>/` containing source and fact records, keyword and product research, final copy, SEO elements, design notes, asset records, responsive `index.html`, deterministic validation results, a QA report, and browser screenshots when rendering is available.

默认在 `output/<keyword-slug>/` 下创建不覆盖历史结果的目录，包含来源与事实记录、关键词及产品调研、最终文案、SEO Elements、设计说明、素材记录、响应式 `index.html`、确定性校验结果、QA 报告，以及浏览器渲染可用时的页面截图。

**Network and limits / 联网与限制**

Current organic results, Reddit, Quora, the official site, and representative same-site pages are researched through available first-party browser and web-search capabilities. The workflow does not require paid research APIs, does not bypass access controls, does not invent product claims, and does not implement the real tool backend. It stops for confirmation when the keyword is unsuitable, evidence coverage is insufficient, or a canonical URL must be chosen.

调研通过宿主提供的第一方浏览器与网页搜索能力访问当前自然搜索结果、Reddit、Quora、官网及代表性站内页面。流程不依赖付费调研 API，不绕过访问控制，不虚构产品事实，也不实现真实工具后端；关键词不适合、证据覆盖不足或需要确定 Canonical URL 时会暂停并请求确认。

## Credential and data safety / 凭证与数据安全

- Never paste API keys, OAuth tokens, cookies, authorization headers, service-account files, or signed URLs into a prompt, issue, commit, or generated artifact / 不要将 API Key、OAuth Token、Cookie、Authorization Header、Service-account 文件或 Signed URL 粘贴到 Prompt、Issue、Commit 或生成文件中
- Configure credentials through the host's OAuth flow, secure connector, or environment variables only / 只通过宿主 OAuth、安全连接器或环境变量配置凭证
- Keep `.env`, `.local.env`, credential exports, raw provider responses, browser profiles, and private crawl data out of Git / 不要将 `.env`、`.local.env`、凭证导出、Provider 原始响应、浏览器 Profile 或私有抓取数据提交到 Git
- Review `git status` and staged changes before every commit; use a secret scanner when available / 每次提交前检查 `git status` 与暂存内容，并在条件允许时运行 Secret Scanner
- A configured credential does not override a Skill's scope, access-control, cost, or approval rules / 已配置凭证不会绕过 Skill 对范围、访问控制、费用或审批的要求
- Do not use these Skills to bypass CAPTCHA, login, paywall, robots restrictions, rate limits, or another access decision / 不要使用这些 Skills 绕过 CAPTCHA、登录、付费墙、Robots 限制、Rate Limit 或其它访问控制

## Design principles / 设计原则

- Evidence before claims / 先有证据，再写结论
- Explicit provenance for observed, sourced, and simulated data / 明确区分观测数据、来源证据与模拟结果
- Read-only by default; publishing and implementation require separate instructions / 默认只读；发布与实施必须另行授权
- No invented metrics, product facts, rankings, tests, or user experience / 不虚构指标、产品事实、排名、测试或用户体验
- Outputs are validated where a bundled deterministic validator exists / 存在确定性校验器时必须验证输出

## Author / 作者

Span

## License / 许可证

Licensed under the [MIT License](LICENSE).

Copyright (c) 2026 SpanChenGithub.
