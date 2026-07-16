# SEO Title and Description

> 基于页面事实和实时 SERP，为单页或最多 10 个页面生成、审核或改写 5 组 SEO Title 与 Meta Description。

> Research, audit, rewrite, or generate five SEO Title and Meta Description pairs for one page or a batch of up to ten pages.

## 中文说明

### 核心能力

- 读取用户粘贴的内容、产品 Brief、页面 URL 或代码，提取页面真实信息和已有元数据。
- 调研当前目标语言下的前 10 个自然搜索结果、PAA、相关搜索及可见广告文案。
- 分开统计自然结果 Title 与可见 Snippet 中的高频词汇和短语。
- 判断搜索意图和页面类型，并检查关键词与目标页面是否匹配。
- 审核已有 Title 和 Meta Description 的准确性、清晰度、重复、品牌后缀、关键词堆砌和页面一致性。
- 为每个成功处理的页面生成 5 组不同角度的候选，第一组为最推荐方案。
- 支持多语言及最多 10 个页面的批量任务。

### 何时使用

适合新页面生成元数据、审核或改写已有元数据、根据目标关键词和 URL 研究搜索意图，或批量处理 SaaS、在线工具、内容站及相关页面类型。

### 输入

**必填**

- `primary_keyword`：每个页面的主关键词。
- 页面证据：粘贴内容、产品 Brief、URL、可读源码，或足以确认页面真实功能的授权研究结果。

**条件必填**

- 页面类型：只有在页面和 SERP 无法形成清晰一致判断时才需要用户确认。

**选填**

- 目标国家/地区和明确输出语言。
- 次关键词或长尾关键词、品牌名、核心卖点、目标用户。
- 审核任务中的当前 Title 和 Meta Description；也可从 URL 或源码提取。

### 安装与调用

克隆仓库：

```bash
git clone https://github.com/SpanChenGithub/seo-geo-skills.git
cd seo-geo-skills
```

将 `skills/seo-title-and-description` 整个目录复制到对应位置：

| 客户端 | 安装位置 | 调用方式 |
| --- | --- | --- |
| Codex | `~/.codex/skills/seo-title-and-description/` | `$seo-title-and-description` |
| Claude Code | 项目中的 `.claude/skills/seo-title-and-description/` | `/seo-title-and-description` |
| Cursor | 项目中的 `.cursor/skills/seo-title-and-description/` | `/seo-title-and-description` |

示例：

```text
$seo-title-and-description 目标关键词：online audio converter，页面：https://example.com/audio-converter
```

```text
/seo-title-and-description Audit and rewrite the metadata for https://example.com/pricing. Primary keyword: project management software pricing.
```

批量任务请为每个页面提供 URL 或内容及对应的主关键词，单次最多 10 个页面。

### 输出

成功时，每个页面只返回以下结构，不展示研究过程、审核说明、来源或字符数：

```text
1.
Title: ...
Meta Description: ...

2.
Title: ...
Meta Description: ...

3.
Title: ...
Meta Description: ...

4.
Title: ...
Meta Description: ...

5.
Title: ...
Meta Description: ...
```

### 依赖、联网与凭证安全

- 正式生成必须使用本次任务中的实时 SERP，依赖宿主已授权的网页搜索、浏览器或 URL 读取能力。
- 没有必须使用的付费 API，也不会使用自定义脚本抓取 Google 或绕过 CAPTCHA。
- Python 3 可用于运行内置字符宽度和结构校验器，但不是联网凭证。
- 不要把 API Key、Cookie、登录信息或私有页面凭证放入聊天、文件、命令参数或 Git 仓库。

### 限制

- 实时 SERP 不可用、权限被拒绝、地区/语言无法满足或遇到 CAPTCHA 时，会停止正式生成并请求 SERP 截图、导出，或前 10 条 Title、Snippet 与 URL。
- 不修改代码、页面文件或线上元数据。
- 不虚构 Free、折扣、速度、评分、年份、功能、价格或其他产品声明。
- Title 默认不在末尾追加品牌名，只有品牌在目标语言市场极具知名度且确实提升识别时才例外。
- 字符范围是编辑目标，不是 Google 的固定限制；Google 也可能重写 Title Link 或 Snippet。

## English Guide

### Core capabilities

- Extract page truth and existing metadata from pasted copy, a product brief, a URL, or readable source code.
- Research the current top organic results and analyze Title and visible-snippet vocabulary separately.
- Infer search intent and page type, audit existing metadata, and identify keyword-to-page mismatches.
- Generate five materially distinct Title and Meta Description pairs, with the strongest pair first.
- Support multiple languages and batches of up to ten pages.

### When to use

Use it to create metadata for a new page, audit or rewrite current metadata, study intent for a keyword and URL, or process several SaaS, online-tool, or content pages together.

### Inputs

**Required:** one primary keyword and enough page evidence for every item.

**Conditionally required:** page type when page and SERP evidence do not agree clearly.

**Optional:** country or region, output language, secondary keywords, brand, benefits, audience, and existing Title and Meta Description.

### Installation and invocation

Clone the repository, then copy the complete `skills/seo-title-and-description` directory to the location shown above. Invoke it with `$seo-title-and-description` in Codex or `/seo-title-and-description` in Claude Code and Cursor.

Example:

```text
$seo-title-and-description Primary keyword: online invoice generator. Page: https://example.com/invoice-generator
```

### Output

Each successful item returns exactly five numbered Title and Meta Description pairs. Research notes, rationale, audit commentary, sources, and character counts remain internal.

### Dependencies, network access, and credential safety

Fresh SERP access through authorized host search or browser tools is mandatory. Python 3 can run the bundled metadata validator. No paid API is required. Never provide or commit API keys, cookies, login details, or private-page credentials.

### Limitations

The Skill stops when current SERP evidence is unavailable, never edits implementation code, does not invent product claims, normally omits terminal brand suffixes, and cannot guarantee how Google displays a title link or snippet.

Author: Span · License: MIT
