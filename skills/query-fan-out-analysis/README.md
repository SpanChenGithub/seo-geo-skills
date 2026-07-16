# Query Fan-Out Analysis

> 分析一个关键词或 Prompt 在多种 AI 搜索工作流中可能触发的子查询，并将真实 API 轨迹、供应商生成结果和启发式模拟严格分开。

> Map the likely subqueries behind a keyword or prompt across AI search workflows while keeping observed API traces, provider-generated candidates, and heuristic simulations explicitly separate.

## 中文说明

### 核心能力

- 分析 OpenAI/ChatGPT-style API、Gemini API、Google AI Mode、Claude API 和 Perplexity API 的 Query Fan-out。
- 默认对每个平台运行 3 次，比较同平台重复出现的主题及跨平台覆盖度。
- 在 API 明确返回搜索查询字符串时保留原始查询，并标记为 `observed_tool_query`。
- 将供应商模型生成的候选查询标记为 `synthetic_provider_query`，无法调用供应商时的宿主模拟标记为 `heuristic_simulation`。
- 对查询进行意图分类、去重、聚类、稳定性计算和跨模型覆盖分析。
- 结合实时 SERP、PAA 和相关搜索补充外部信号，但不会把这些信号伪装成模型真实查询。
- 用户提供 URL 或页面内容时，可分析页面覆盖差距。
- 最终给出适合页面纳入的 SEO/GEO 话题优先级建议。

### 何时使用

适合研究 AI 搜索可能如何拆解一个问题、比较不同平台的查询角度、发现内容缺口，或为 SEO/GEO 页面规划主题、FAQ、对比、流程和信任内容。

### 输入

**必填**

- `seed_input`：一个目标关键词或完整 Prompt。

**选填**

- 目标语言、国家/地区、Locale 或大致位置。
- 受众、Persona、品牌、产品、业务或话题背景。
- 时间范围、时效性要求和期望答案类型。
- 页面 URL 或粘贴的页面内容。
- 平台、模型 ID、运行次数、每次候选查询数。
- API-backed、observed-only、simulated-only 或 hybrid 模式。

### 安装与调用

克隆仓库：

```bash
git clone https://github.com/SpanChenGithub/seo-geo-skills.git
cd seo-geo-skills
```

将 `skills/query-fan-out-analysis` 整个目录复制到对应位置：

| 客户端 | 安装位置 | 调用方式 |
| --- | --- | --- |
| Codex | `~/.codex/skills/query-fan-out-analysis/` | `$query-fan-out-analysis` |
| Claude Code | 项目中的 `.claude/skills/query-fan-out-analysis/` | `/query-fan-out-analysis` |
| Cursor | 项目中的 `.cursor/skills/query-fan-out-analysis/` | `/query-fan-out-analysis` |

示例：

```text
$query-fan-out-analysis ai music video generator
```

```text
/query-fan-out-analysis Analyze "best CRM for a 20-person SaaS team" in simulated-only mode and recommend page topics.
```

```text
$query-fan-out-analysis 分析关键词“AI 配音工具”，并检查 https://example.com/page 已覆盖和缺失的话题。
```

### 输出

默认返回简洁的 Markdown 报告，包含：执行方法、输入语境、搜索意图、外部信号、各平台查询聚类、同平台稳定性、跨平台覆盖、平台特有角度、Coverage Matrix、可选页面覆盖分析、限制，以及最终的 SEO/GEO 页面话题建议。

JSON 和 CSV 只在用户明确要求时保存或导出；输出前会使用内置校验器检查结构、引用关系、来源标签和潜在凭证泄露。

### 依赖、联网与凭证安全

- 默认模式为 API-first hybrid：如果对应 API 路径、模型和环境凭证均可用，会优先执行真实供应商 API；否则降级为明确标注的模拟。
- 默认范围最多为每个平台 3 次运行、每次 10–15 个生成候选。已配置凭证会在这个普通默认范围内触发 API 调用，并可能产生供应商费用；可以在请求中明确指定 `simulated-only`、`no-network` 或 `no-paid-API`。
- 供应商凭证只允许从 `OPENAI_API_KEY`、`GEMINI_API_KEY`/`GOOGLE_API_KEY`、`ANTHROPIC_API_KEY`、`PERPLEXITY_API_KEY` 等本地环境变量读取。
- 不要在聊天、请求 JSON、命令参数、报告或仓库中粘贴、保存或提交密钥。默认不持久化完整 API 响应。
- 收集和校验脚本需要 Python 3；实时外部信号需要宿主提供已授权的联网搜索能力。

### 限制

- 不访问或推断隐藏 Chain-of-Thought、私有检索逻辑或稳定不变的平台查询列表。
- API 结果不等同于 chatgpt.com、Gemini App、Google AI Mode、claude.ai 或 perplexity.ai 的消费者产品行为。
- Google AI Mode 没有对应的公开消费者查询轨迹，本 Skill 只提供明确标注的模拟。
- 重复率不是搜索量、真实触发概率或市场份额；覆盖这些话题也不保证排名或 AI 引用。
- URL 无法访问时可以继续做 Fan-out，但页面覆盖判断需要用户提供可读内容。

## English Guide

### Core capabilities

- Compare likely fan-outs across OpenAI/ChatGPT-style API, Gemini API, Google AI Mode simulation, Claude API, and Perplexity API.
- Run repeated independent analyses and calculate within-provider recurrence and cross-model coverage.
- Preserve exact structured API search traces as `observed_tool_query` and keep provider-generated and host-simulated candidates separately labeled.
- Classify, normalize, deduplicate, cluster, and prioritize query families.
- Add current SERP, PAA, and related-search signals without mislabeling them as provider queries.
- Assess optional URL coverage and finish with prioritized SEO/GEO page-topic recommendations.

### When to use

Use it to understand how AI search may decompose a request, compare platform angles, discover content gaps, or plan topics, FAQs, comparisons, workflows, trust signals, and supporting pages.

### Inputs

**Required:** `seed_input`, either a keyword or a complete prompt.

**Optional:** language, locale, location, audience or persona, brand or business context, freshness, answer type, URL or pasted page content, providers, models, run count, query target, and execution mode.

### Installation and invocation

Clone the repository, then copy the complete `skills/query-fan-out-analysis` directory to the location shown above. Invoke it with `$query-fan-out-analysis` in Codex or `/query-fan-out-analysis` in Claude Code and Cursor.

Example:

```text
$query-fan-out-analysis Analyze "best accounting software for freelancers" and recommend the topics a landing page should cover.
```

### Output

The default output is a concise Markdown report covering method, intent, evidence provenance, provider clusters, recurrence, cross-model coverage, coverage matrix, optional page coverage, limitations, and prioritized SEO/GEO topics. Validated JSON or formula-safe CSV is available on request.

### Dependencies, network access, and credential safety

The default is API-first hybrid execution. Available provider credentials can trigger ordinary default-scope API calls and provider charges; request simulated-only, no-network, or no-paid-API mode when needed. Python 3 supports collection and validation. Keep provider credentials only in local environment variables and never paste or commit their values.

### Limitations

The Skill does not expose hidden reasoning, does not reproduce consumer-product behavior, treats Google AI Mode as simulation, and does not interpret recurrence as volume or probability. No query set can guarantee ranking or AI citation.

Author: Span · License: MIT
