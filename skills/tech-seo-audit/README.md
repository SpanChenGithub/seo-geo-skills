# Technical SEO Audit

> 对 1–10 个授权 URL 执行基于真实页面证据的技术 SEO 审核，并生成可复算评分、优先级建议和本地 Markdown 报告。

> Audit one to ten authorized URLs with real page evidence and deliver reproducible technical SEO scores, prioritized fixes, and saved Markdown reports.

## 中文说明

### 核心能力

- 检查 HTTP 状态、重定向、抓取和可索引信号、Canonical、Robots.txt 与 Sitemap。
- 审核 Title、Meta Description、Robots、语言、Open Graph、Twitter/X Card 等 Head 信息。
- 检查正文渲染、H1–H6、内部/外部链接、图片与媒体、结构化数据。
- 在环境支持时分别运行 Mobile 和 Desktop Lighthouse，并区分实验室数据与真实用户 Core Web Vitals。
- 检查移动端 UX、国际化/Hreflang、安全与影响抓取或渲染的控制台问题。
- 可选接入已授权的 Google Search Console、Ahrefs MCP 或用户提供的导出证据。
- 直接页面采集不完整时，可在满足安全、访问和费用门槛后使用受控 Apify Fallback。
- 使用透明的 100 分加权规则、证据覆盖率和 Critical/High/Medium/Low 严重度。
- 批量审核会为每个 URL 生成独立报告，并额外生成跨页面总结。

### 何时使用

适合单页技术 SEO 体检、多页面对比、索引和抓取问题排查、元数据与结构化数据审核、移动端与性能检查，或需要结合 GSC、Ahrefs、Lighthouse、Apify 证据确定修复优先级时使用。

### 输入

**必填，二选一**

- `url`：一个明确 URL。
- `urls`：2–10 个明确 URL。

**选填**

- 目标关键词、目标国家/地区或 Locale。
- 页面用途或预期 Indexability 状态。
- 用户浏览器中已经存在的授权登录状态。
- HTML、Headers、抓取导出、GSC 证据或 Lighthouse 报告。
- 已授权的 GSC Property 或连接工具。
- 已授权的 Ahrefs MCP 或 Ahrefs 导出。
- 已安全配置的 Apify 连接，以及明确的单次费用上限。

### 安装与调用

克隆仓库：

```bash
git clone https://github.com/SpanChenGithub/seo-geo-skills.git
cd seo-geo-skills
```

将 `skills/tech-seo-audit` 整个目录复制到对应位置：

| 客户端 | 安装位置 | 调用方式 |
| --- | --- | --- |
| Codex | `~/.codex/skills/tech-seo-audit/` | `$tech-seo-audit` |
| Claude Code | 项目中的 `.claude/skills/tech-seo-audit/` | `/tech-seo-audit` |
| Cursor | 项目中的 `.cursor/skills/tech-seo-audit/` | `/tech-seo-audit` |

示例：

```text
$tech-seo-audit https://example.com/product
```

```text
/tech-seo-audit Audit these three URLs and compare their shared template issues:
https://example.com/a
https://example.com/b
https://example.com/c
```

```text
$tech-seo-audit 审核 https://example.com/page，并在直接抓取不完整且符合安全门槛时，使用已配置的 Apify，单次费用上限 1 美元。
```

### 输出

每个 URL 会生成一份完整 Markdown 报告，固定包含：

1. Executive Summary
2. Top Priorities
3. Detailed Findings
4. Actionable Checklist
5. Assumptions and Limitations

报告默认保存到项目下的 `audits/tech-seo/`，不会覆盖已有文件。批量任务还会生成 Batch Summary，并链接每个独立页面报告。报告包括透明技术 SEO 评分、证据覆盖率、单独的移动端/桌面端性能结果、严重度统计、具体证据、修复方式与验证方法。

### 依赖、联网与凭证安全

- 最完整的审核需要已授权的真实浏览器或 DevTools 等效能力；也可使用 Playwright 等浏览器自动化。静态 HTTP 模式会明确标记能力限制。
- Lighthouse、CrUX/PageSpeed、GSC 和 Ahrefs 都是按可用性使用的证据源，不是完成所有审核的强制依赖。
- Apify 仅作为受控 Fallback 或在用户明确要求时使用。必须已在本地环境配置 `APIFY_API_TOKEN` 或安全连接，并在运行前取得费用授权和正数的 `maxTotalChargeUsd` 上限。
- 不要将 API Key、OAuth Token、Cookie、账号信息、私有查询参数、数据集访问 URL 或环境文件提交到 Git。不要把凭证放在聊天、URL、命令参数或报告中。
- 内置 Apify Helper 需要 Python 3；默认只预览计划，只有满足授权条件才会联网执行。

### 限制

- 不绕过 CAPTCHA、登录、付费墙、Robots 限制、Bot Challenge、Rate Limit 或地域访问控制。
- 单页审核不能证明全站 Title 唯一性、孤儿页面、完整抓取深度、Sitemap 完整性或全部 Hreflang 互链。
- 只有 GSC URL Inspection 或等效一方证据才能支持 Google 实际索引状态；技术可索引不等于已经收录。
- 没有真实测量时不会虚构 Lighthouse、Core Web Vitals、HTTP 状态、Schema、链接数或评分。
- 默认只审核用户明确提供的 URL，不会因为收到域名或 Sitemap 就自动全站抓取。
- 审核保持只读，不会修改网站、代码、CMS、DNS、Analytics、GSC 或生产配置。

## English Guide

### Core capabilities

- Inspect HTTP behavior, redirects, crawl and indexability signals, canonicals, robots.txt, and sitemaps.
- Audit metadata, rendered content, headings, links, images, media, and structured data.
- Run separate mobile and desktop Lighthouse audits when supported and keep lab and field evidence distinct.
- Review mobile UX, internationalization, security, and rendering-related failures.
- Add optional read-only GSC, Ahrefs MCP, user-export, and controlled Apify evidence.
- Calculate a transparent weighted score and evidence coverage, then prioritize deduplicated root causes.
- Produce one report per URL and an additional batch summary for two to ten URLs.

### When to use

Use it for a technical SEO health check, multi-page comparison, crawl or indexability investigation, metadata and schema review, performance and mobile analysis, or evidence-backed remediation planning.

### Inputs

**Required:** one explicit URL or a list of two to ten explicit URLs.

**Optional:** keyword, locale, expected page purpose or indexability, an authorized browser session, supplied HTML or exports, authorized GSC or Ahrefs access, and an authorized Apify connection with a positive per-run cost cap.

### Installation and invocation

Clone the repository, then copy the complete `skills/tech-seo-audit` directory to the location shown above. Invoke it with `$tech-seo-audit` in Codex or `/tech-seo-audit` in Claude Code and Cursor.

Example:

```text
$tech-seo-audit Audit https://example.com/category for technical SEO. Target keyword: online design tools.
```

### Output

The Skill returns and saves a complete five-section Markdown report for each URL under `audits/tech-seo/` without overwriting earlier runs. Batch work also creates a cross-page summary. Reports include evidence coverage, a reproducible technical score when enough evidence exists, device-specific Lighthouse results, prioritized findings, implementation guidance, and verification steps.

### Dependencies, network access, and credential safety

A real browser or equivalent inspection capability provides the strongest evidence; browser automation and limited static inspection are supported fallbacks. Lighthouse, GSC, Ahrefs, and Apify are optional evidence sources. Apify requires a securely configured `APIFY_API_TOKEN`, explicit charge authorization, and a positive cost cap. Never paste or commit credentials, cookies, private URLs, environment files, or dataset access links.

### Limitations

The Skill never bypasses access controls, cannot prove sitewide conditions from one page, cannot claim Google indexing without direct evidence, never invents unavailable metrics, audits only the URLs placed in scope, and remains read-only unless implementation is separately requested.

Author: Span · License: MIT
