# 2026 年 2 月 AI 最新动态：千问 3.5 开源、OpenAI 与 Anthropic 同日发码力模型

> 梳理 2026 年 2 月大模型领域重点变动：阿里千问 Qwen3.5 开源、OpenAI GPT-5.3-Codex 与 Anthropic Claude Opus 4.6 同日发布，及对开发者的影响与获取方式。

---

## 一、变动概览

2026 年 2 月，大模型领域有三类值得开发者关注的变化：

1. **阿里千问 Qwen3.5**：2 月 16 日（除夕）开源新一代基础模型，多尺寸、原生多模态、MoE 架构，在魔搭与 HuggingFace 可下载，并配有低价 API。
2. **OpenAI 与 Anthropic 同日发码力/Agent 模型**：2 月 5 日，Anthropic 发布 Claude Opus 4.6（百万级上下文、Agent Teams），OpenAI 随后发布 GPT-5.3-Codex（编程与推理合一、即将开放 API）。
3. **生态与弃用**：GitHub 等平台对部分旧版 OpenAI/Anthropic 模型做弃用或切换，集成时需关注模型 id 与文档。

下文按「时间线 + 来源 + 对开发者的影响」展开，便于你判断是否要升级集成或试用新模型。

---

## 二、阿里千问 Qwen3.5 开源（2026 年 2 月 16 日）

### 时间与来源

- **发布时间**：2026 年 2 月 16 日（除夕夜），阿里通义千问团队开源 **Qwen3.5** 系列。
- **来源**：阿里官方发布、魔搭社区（ModelScope）、HuggingFace、财经与科技媒体报道（如新浪财经、腾讯新闻、VentureBeat 等）。

### 核心信息（以官方与主流报道为准）

- **架构**：从纯文本升级为**原生多模态**，采用**混合架构**（门控注意力 + 稀疏 MoE）；旗舰规模约 **397B 总参数、17B 激活**，兼顾能力与推理成本。
- **能力与评测**：长上下文（如 256K 场景下推理吞吐提升明显）、视频理解（支持约 2 小时/百万 token 级输入）；公开评测中在 MMLU-Pro、GPQA、IFBench 等基准上有领先表现，具体分数以官方公告为准。
- **对开发者的影响**：
  - **开源获取**：魔搭社区、HuggingFace、GitHub 可下载多尺寸模型（如 0.8B/2B/4B/9B/27B/35B/122B 及 397B-A17B 等），便于本地或私有化部署。
  - **API**：阿里云百炼等平台提供 Qwen3.5 系列 API（如 Qwen3.5-Flash），定价与计费以控制台与文档为准，适合快速接入而不自建推理。
  - **选型**：需要「强能力 + 可控成本」或「多模态 + 长上下文」时，可把 Qwen3.5 列入对比；需注意版本号与模型 id（如 Qwen3.5-35B-A3B 等）与文档一致。

### 官方与获取链接（建议以当前页面为准）

- 魔搭社区：[modelscope.cn](https://www.modelscope.cn) 搜索「Qwen3.5」或「千问」。
- HuggingFace：搜索 `Qwen` 或 `Qwen3.5`。
- 阿里云百炼/通义：阿里云官网「百炼」或「通义」产品页。

---

## 三、OpenAI GPT-5.3-Codex 与 Anthropic Claude Opus 4.6（2026 年 2 月 5 日）

### 时间与来源

- **时间**：2026 年 2 月 5 日，Anthropic 与 OpenAI 在相近时间分别发布新模型（多家外媒报道为「同日/同小时」发布）。
- **来源**：TechCrunch、Business Insider、Unite.AI、OpenAI 与 Anthropic 官方渠道（含 Help Center、博客）；GitHub Changelog 对部分模型弃用做了说明。

### Anthropic Claude Opus 4.6

- **主要变化**：**百万 token 级上下文**（约 100 万 token，约 3000 页文本）、**Agent Teams**（多 Claude 实例协同处理同一代码库等任务）、**128K token 输出**、自适应推理等。
- **对开发者的影响**：API 定价（报道中提及输入约 $5/百万 token、输出约 $25/百万 token，以官方价格页为准）；适合长文档、大代码库与多 Agent 协作场景；集成时使用新模型 id，旧版 Claude 模型在部分平台可能被标记弃用，需查 GitHub/文档。

### OpenAI GPT-5.3-Codex

- **主要变化**：将**编程能力**（对标 GPT-5.2-Codex）与**通用推理**（对标 GPT-5.2）统一；报道称推理速度较前代提升约 25%；可通过 ChatGPT 付费计划、Codex 应用/CLI/IDE 扩展/网页使用；**API 开放计划**以官方公告为准。
- **对开发者的影响**：若已用 GPT-5.2-Codex 或 GPT-5.2，可关注 GPT-5.3-Codex 的 API 上线时间与模型名，便于迁移；本地/IDE 集成依赖官方 CLI 与扩展的版本更新。

### 官方与延伸

- OpenAI 模型发布说明：[OpenAI Help Center - Model Release Notes](https://help.openai.com/en/articles/9624314-model-release-notes)。
- Anthropic：官网文档与 API 页。
- GitHub 对部分 OpenAI/Anthropic 旧模型的弃用说明（2026-02-19）：[GitHub Changelog](https://github.blog/changelog/) 搜索 “Anthropic” / “OpenAI” / “deprecated”。

---

## 四、小结与建议

- **千问 Qwen3.5**：2 月 16 日开源，多尺寸、多模态、MoE，适合需要开源可部署或低价 API 的场景；从魔搭/HuggingFace/阿里云获取与接入。
- **Claude Opus 4.6 / GPT-5.3-Codex**：2 月 5 日前后发布，前者侧重长上下文与 Agent 协作，后者侧重编程+推理统一与即将到来的 API；集成时使用新模型 id，并关注各平台对旧模型的弃用与切换。
- **建议**：新项目可优先试用上述新模型；已有集成请核对模型 id 与文档，避免使用已弃用版本。具体价格、限额与 API 名称以各厂商当前文档为准。

若对你有用，欢迎点赞、收藏；你若有基于 Qwen3.5 或 Codex/Claude 4.6 的实践，也欢迎在评论区分享。
