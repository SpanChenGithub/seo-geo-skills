# Tools Landing Page Generator

`tools-landing-page-generator` helps you turn one tool-style keyword and one official website into an evidence-backed static landing-page package. It researches current search results and public discussions, verifies product claims, follows the target site's visual language, writes American English copy by default, and validates the final responsive HTML.

`tools-landing-page-generator` 用于将一个工具型关键词与一个目标官网转化为基于证据的静态落地页内容包。它会调研当前搜索结果与公开讨论、核实产品事实、提取目标网站的视觉语言，默认撰写美式英文文案，并验证最终响应式 HTML。

> The generated tool area is intentionally non-functional. This Skill creates the page, copy, SEO assets, research records, and a clearly marked integration boundary; it does not build the product backend.
>
> 生成页面中的工具区域是明确标注的非功能占位区。本 Skill 负责页面、文案、SEO 资产、调研记录与后续接入边界，不负责实现产品后端。

## Before you start / 使用前准备

Prepare these two required inputs:

请准备以下两项必填信息：

- One primary keyword, such as `ai music video generator` / 一个主关键词，例如 `ai music video generator`
- The official target website, such as `https://example.org` / 目标官网，例如 `https://example.org`

If the final page URL already exists, include it. Otherwise, the Skill will inspect the site's URL conventions, propose a canonical URL, and wait for your confirmation before final SEO and HTML generation.

如果最终页面 URL 已存在，请一并提供。否则，Skill 会检查网站的 URL 规则、提出 Canonical URL 建议，并在生成最终 SEO 与 HTML 前等待确认。

The following context is optional but reduces follow-up questions and makes the page more accurate:

以下信息不是必填项，但可以减少追问并提高页面准确性：

- Product positioning and target users / 产品定位与目标用户
- Real input, output, and workflow / 真实输入、输出与操作流程
- Verified features, differentiators, and limitations / 已核实的功能、差异点与限制
- Pricing, signup, privacy, or security facts with official sources / 带官网来源的价格、注册、隐私或安全事实
- CTA goal, brand guide, screenshots, design tokens, or authorized assets / CTA 目标、品牌指南、截图、设计 Token 或授权素材
- Target market and page language when different from the US and English defaults / 与默认美国市场和英文页面不同的目标市场与语言

Do not paste API keys, login cookies, private credentials, or confidential customer data into the prompt.

请勿在 Prompt 中粘贴 API Key、登录 Cookie、私密凭证或机密客户数据。

## Install / 安装

Copy the complete Skill directory into a supported Agent Skills location. Do not copy only `SKILL.md`, because the references and validator are required by the workflow.

请将完整的 Skill 目录复制到宿主支持的 Agent Skills 路径中。不要只复制 `SKILL.md`，因为工作流还需要引用文档与验证器。

Common project-level locations:

常见的项目级路径：

| Host / 宿主 | Destination / 目标路径 |
| --- | --- |
| Codex | `.agents/skills/tools-landing-page-generator/` |
| Claude Code | `.claude/skills/tools-landing-page-generator/` |
| Cursor | `.cursor/skills/tools-landing-page-generator/` or `.agents/skills/tools-landing-page-generator/` |

Restart the agent session if the host does not discover a newly installed Skill automatically.

如果宿主没有自动发现新安装的 Skill，请重新开启 Agent 会话。

## Quick start / 快速开始

Explicitly invoke the Skill and provide the required inputs:

显式调用 Skill，并提供必填信息：

```text
Use $tools-landing-page-generator.

Primary keyword: ai music video generator
Official website: https://example.org
Final page URL: https://example.org/ai-music-video-generator
```

In Claude Code or Cursor, use `/tools-landing-page-generator` when the host exposes installed Skills as slash commands. Natural-language invocation also works when the host supports Agent Skills.

在 Claude Code 或 Cursor 中，如果宿主将已安装 Skill 暴露为 Slash Command，请使用 `/tools-landing-page-generator`。宿主支持 Agent Skills 时，也可以用自然语言调用。

## Recommended prompt / 推荐 Prompt

Use this template when you already have product and brand context:

已有产品与品牌资料时，建议使用以下模板：

```text
Use $tools-landing-page-generator to create one static tool landing page.

Primary keyword: <one keyword>
Official website: <https://official-site.example>
Final page URL: <existing or intended HTTPS URL>
Market and language: <for example, United States / English>

Product context:
- Product name and positioning: <...>
- Target users: <...>
- Real input and output: <...>
- Actual workflow: <3-4 steps>
- Verified features and differentiators: <...>
- Known limitations: <...>
- Privacy or security facts and official sources: <...>
- Primary CTA goal: <...>

Brand context:
- Representative same-site pages: <URLs>
- Brand guide, screenshots, tokens, or authorized local assets: <paths or links>

Output destination: <optional; default is output/<keyword-slug>/>
```

You may provide files or links instead of rewriting a knowledge base in the prompt. Clearly identify which facts are approved for public use.

你可以提供文件或链接，无需把整份知识库重新粘贴到 Prompt 中。请明确哪些事实已获准公开使用。

## What happens during a run / 运行流程

The Skill processes one keyword and one page per run:

Skill 每次只处理一个关键词与一个页面：

1. Records the brief and asks once for optional product context / 记录 Brief，并一次性询问可选产品信息
2. Checks whether the keyword matches tool-page search intent / 判断关键词是否符合工具落地页搜索意图
3. Researches current organic results, Reddit, and Quora / 调研当前自然搜索结果、Reddit 与 Quora
4. Verifies publishable product facts from official evidence / 通过官方证据核实可公开的产品事实
5. Extracts the target site's design language / 提取目标网站的设计语言
6. Writes and stabilizes the visible copy / 撰写并稳定页面文案
7. Generates metadata and JSON-LD / 生成 Metadata 与 JSON-LD
8. Builds and validates the static package / 构建并验证静态内容包

The agent may pause for your decision. A pause protects factual accuracy; it is not a failed run.

Agent 可能会暂停并等待你的决定。暂停用于保护事实准确性，并不代表运行失败。

| Pause reason / 暂停原因 | What you need to decide or provide / 你需要决定或提供的内容 |
| --- | --- |
| No final page URL / 缺少最终页面 URL | Confirm the proposed canonical URL / 确认建议的 Canonical URL |
| Keyword is unsuitable or mixed / 关键词不适合或意图混杂 | Revise the keyword or explicitly approve continuing / 更换关键词或明确同意继续 |
| Fewer than 7 usable organic pages / 可用自然结果少于 7 个 | Accept reduced evidence or stop / 接受较少证据或停止 |
| Product facts are insufficient / 产品事实不足 | Supply the smallest missing set of official facts / 补充最少且必要的官方事实 |
| Target-site style cannot be inspected / 无法检查目标网站样式 | Provide screenshots, tokens, CSS, or a brand guide; or approve a neutral fallback / 提供截图、Token、CSS 或品牌指南；或同意中性降级方案 |

## Output / 输出内容

The default destination is `output/<keyword-slug>/`. Existing output is never overwritten; a versioned sibling such as `-v2` is created instead.

默认输出到 `output/<keyword-slug>/`。已有结果不会被覆盖；如发生冲突，会创建 `-v2` 等版本目录。

```text
output/<keyword-slug>/
├── index.html
├── manifest.json
├── research/
│   ├── intake.md
│   ├── keyword-research-<keyword-slug>.md
│   ├── sources.json
│   ├── fact-ledger.json
│   └── style-report.md
├── content/
│   ├── landing-page-copy.md
│   └── seo-elements-<keyword-slug>.md
├── assets/
│   └── asset-manifest.json
└── validation/
    ├── validation-report.json
    ├── qa-report.md
    └── screenshots/  # when browser rendering is available / 浏览器渲染可用时
```

The package keeps research, fact, design, copy, and QA artifacts separate so reviewers can trace important claims and decisions before publication.

内容包会分别保留调研、事实、设计、文案与 QA 产物，方便审核者在发布前追溯重要事实与决策。

## Validate an output package / 验证输出包

The Skill runs its validator before handoff. You can run it again after manual edits:

Skill 会在交付前运行验证器。手动修改页面后，可以再次运行：

```bash
python3 ".agents/skills/tools-landing-page-generator/scripts/validate_landing_page.py" \
  "output/<keyword-slug>" \
  --keyword "<exact primary keyword>" \
  --pretty \
  --output "output/<keyword-slug>/validation/validation-report.json"
```

Replace the Skill path when you installed it elsewhere. Fix all errors before publishing; review warnings individually and document any accepted exception.

如果安装在其它位置，请替换 Skill 路径。发布前应修复全部 Error；Warning 需要逐项检查，并记录接受例外的原因。

## Scope and limitations / 能力边界

- Creates a static, responsive HTML page and supporting artifacts / 创建静态响应式 HTML 页面与配套产物
- Does not implement the actual generator, checker, converter, calculator, or other backend / 不实现 Generator、Checker、Converter、Calculator 等真实后端
- Does not guarantee rankings, traffic, conversions, or AI citations / 不承诺排名、流量、转化或 AI 引用
- Does not fabricate prices, limits, privacy promises, ratings, performance, or product features / 不虚构价格、限制、隐私承诺、评分、性能或产品功能
- Does not bypass CAPTCHA, login, paywalls, robots restrictions, or other access controls / 不绕过 CAPTCHA、登录、付费墙、Robots 限制或其它访问控制
- Does not hotlink third-party assets or copy another site's DOM, CSS, scripts, or tracking / 不盗链第三方素材，也不复制其它网站的 DOM、CSS、脚本或 Tracking

## Troubleshooting / 常见问题

**The Skill asks many factual questions. / Skill 询问了较多事实。**

Provide official product, pricing, help, privacy, and brand sources at the start. The Skill asks only for unresolved facts that block required sections.

建议在开始时提供官方产品页、价格页、帮助文档、隐私政策与品牌资料。Skill 只会追问阻塞必需页面模块的未决事实。

**The workflow stopped after keyword research. / 工作流在关键词调研后停止。**

The keyword may be navigational, informational, mismatched with the product, or supported by too little accessible evidence. Review the saved suitability decision, then revise the keyword or explicitly approve the documented reduced-evidence path when offered.

关键词可能属于导航型或信息型意图、与产品不匹配，或可访问证据不足。请查看已保存的适用性判断，然后更换关键词；如工作流提供了低证据继续选项，也可以明确同意该路径。

**No `index.html` was created. / 没有生成 `index.html`。**

The workflow does not generate public copy or HTML when mandatory facts, canonical confirmation, evidence coverage, or visual guidance remains blocked. Resolve the handoff's listed blockers and resume the same task.

当必需事实、Canonical 确认、证据覆盖或视觉依据仍被阻塞时，工作流不会生成公开文案或 HTML。请解决交付说明中列出的阻塞项，然后继续同一任务。

**The page has a tool box but it does not work. / 页面有工具框，但无法使用。**

This is expected. The placeholder is a safe integration boundary for developers. Ask separately for implementation of the real tool and provide its API, component, or backend requirements.

这是预期行为。该占位区是为开发者预留的安全接入边界。如需实现真实工具，请另行提出开发需求，并提供 API、组件或后端要求。
